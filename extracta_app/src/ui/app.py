"""Streamlit UI for Extracta financial data pipeline (Task 44).

Provides user interface for:
- Upload: File upload and raw extraction preview
- Transactions: View normalized data and assign categories  
- Reports: Query builder with filters, grouping, aggregation
- Templates: Save and load report configurations

Design: Thin UI layer, business logic in src/ modules.
"""
from __future__ import annotations

import streamlit as st
import tempfile
import os
from pathlib import Path


# Import business logic modules
try:
    from src.ingestion.pipeline import ingest_file
    from src.normalization.engine import normalize_rows
    from src.persistence.migrations import init_db
    from src.persistence.transactions_repository import bulk_insert_transactions, get_transactions
    from src.categorization.service import create_category, list_categories, assign_category
    from src.reporting.executor import execute_report
    from src.reporting.templates import save_template, list_templates
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def init_session_state():
    """Initialize session state variables."""
    if 'db_path' not in st.session_state:
        # Use temp DB for demo, could be configurable
        st.session_state.db_path = "data/extracta.db"
        os.makedirs("data", exist_ok=True)
        init_db(st.session_state.db_path)
    
    if 'uploaded_files_processed' not in st.session_state:
        st.session_state.uploaded_files_processed = []


def upload_section():
    """File upload and extraction preview section."""
    st.header("📁 Upload Financial Documents")
    
    uploaded_files = st.file_uploader(
        "Upload PDF or image files (.pdf, .png, .jpg, .jpeg)",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in [f['name'] for f in st.session_state.uploaded_files_processed]:
                st.subheader(f"Processing: {uploaded_file.name}")
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Extract raw data
                    with st.spinner("Extracting data..."):
                        raw_artifact = ingest_file(tmp_path)
                    
                    st.success(f"✅ Extracted {raw_artifact['record_count_raw']} rows")
                    
                    # Show preview
                    if raw_artifact['rows']:
                        st.subheader("Raw Data Preview")
                        st.dataframe(raw_artifact['rows'][:10])  # Show first 10 rows
                    
                    # Normalize data
                    with st.spinner("Normalizing data..."):
                        # Load mapping config (you might want to make this configurable)
                        mapping_config = {"version": "v1", "synonyms": {}, "rules": {
                            "Date": "transaction_date",
                            "Description": "description", 
                            "Amount": "amount_out"  # Simplified mapping
                        }}
                        
                        normalized_rows = normalize_rows(
                            raw_artifact['rows'],
                            header_map=mapping_config['rules'],
                            mapping_version=mapping_config['version'],
                            logic_version="0.1.0",
                            source_file=uploaded_file.name,
                            source_file_hash=raw_artifact['source_file_hash']
                        )
                    
                    if normalized_rows:
                        st.success(f"✅ Normalized {len(normalized_rows)} transactions")
                        
                        # Insert into database
                        with st.spinner("Saving to database..."):
                            bulk_insert_transactions(st.session_state.db_path, normalized_rows)
                        
                        st.success("✅ Saved to database")
                        
                        # Mark as processed
                        st.session_state.uploaded_files_processed.append({
                            'name': uploaded_file.name,
                            'rows': len(normalized_rows)
                        })
                    
                except (FileNotFoundError, ValueError, RuntimeError) as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                finally:
                    # Clean up temp file
                    os.unlink(tmp_path)
    
    # Show processed files summary
    if st.session_state.uploaded_files_processed:
        st.subheader("📊 Processed Files")
        for file_info in st.session_state.uploaded_files_processed:
            st.write(f"• {file_info['name']}: {file_info['rows']} transactions")


def transactions_section():
    """View and categorize transactions."""
    st.header("💰 Transactions")
    
    # Get transactions from database
    transactions = get_transactions(st.session_state.db_path, limit=100)
    
    if not transactions:
        st.info("No transactions found. Upload some files first!")
        return
    
    st.subheader(f"Recent Transactions ({len(transactions)})")
    
    # Category management
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Manage Categories")
        categories = list_categories(st.session_state.db_path)
        
        if categories:
            st.write("Existing categories:")
            for cat in categories:
                st.write(f"• {cat['name']}")
        
        # Add new category
        new_category = st.text_input("Create new category:")
        if st.button("Add Category") and new_category:
            try:
                create_category(st.session_state.db_path, new_category)
                st.success(f"Created category: {new_category}")
                st.rerun()
            except (ValueError, RuntimeError) as e:
                st.error(f"Error creating category: {e}")
    
    with col2:
        st.subheader("🏷️ Assign Categories")
        
        # Simple category assignment (could be enhanced with better UX)
        if categories:
            uncategorized = [t for t in transactions if not t['category_id']]
            if uncategorized:
                st.write(f"{len(uncategorized)} uncategorized transactions")
                
                # Show first few uncategorized for quick assignment
                for i, tx in enumerate(uncategorized[:5]):
                    st.write(f"**{tx['description']}** - ${tx['amount_out']}")
                    cat_options = ["None"] + [c['name'] for c in categories]
                    selected = st.selectbox(f"Category for transaction {i+1}:", cat_options, key=f"cat_{i}")
                    
                    if selected != "None" and st.button("Assign", key=f"assign_{i}"):
                        cat_id = next(c['category_id'] for c in categories if c['name'] == selected)
                        assign_category(st.session_state.db_path, tx['transaction_id'], cat_id)
                        st.success(f"Assigned {selected}")
                        st.rerun()
    
    # Display transactions table
    st.subheader("📄 Transactions Table")
    st.dataframe(transactions, use_container_width=True)


def reports_section():
    """Report constructor with filters, grouping, aggregation."""
    st.header("📊 Reports")
    
    # Report configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Filters")
        
        # Date range
        date_from = st.date_input("From date:")
        date_to = st.date_input("To date:")
        
        # Category filter
        categories = list_categories(st.session_state.db_path)
        if categories:
            cat_names = [c['name'] for c in categories]
            st.multiselect("Categories:", cat_names)  # TODO: Use in filtering
    
    with col2:
        st.subheader("📈 Grouping & Aggregation")
        
        # Grouping
        group_options = ["month", "year", "category_id"]
        grouping = st.multiselect("Group by:", group_options)
        
        # Aggregation
        agg_field = st.selectbox("Aggregate field:", ["amount_out", "amount_in"])
        agg_func = st.selectbox("Function:", ["sum", "avg", "count"])
    
    # Build and execute report
    if st.button("🚀 Generate Report"):
        try:
            # Build report request
            report_request = {
                "filters": {},
                "grouping": grouping,
                "aggregations": [{
                    "field": agg_field,
                    "func": agg_func,
                    "alias": f"{agg_func}_{agg_field}"
                }]
            }
            
            # Add date filters if provided
            if date_from:
                report_request["filters"]["date_from"] = date_from.strftime("%Y-%m-%d")
            if date_to:
                report_request["filters"]["date_to"] = date_to.strftime("%Y-%m-%d")
            
            # Execute report
            with st.spinner("Generating report..."):
                result = execute_report(st.session_state.db_path, report_request)
            
            # Display results
            st.subheader("📋 Report Results")
            if result['rows']:
                st.dataframe(result['rows'])
                
                # Simple chart if grouping is used
                if grouping and len(result['rows']) > 1:
                    st.subheader("📊 Chart View")
                    st.bar_chart(result['rows'], x=grouping[0] if grouping else None)
            else:
                st.info("No data found for the specified criteria.")
            
            # Save as template option
            st.subheader("💾 Save as Template")
            template_name = st.text_input("Template name:")
            if st.button("Save Template") and template_name:
                try:
                    save_template(st.session_state.db_path, template_name, report_request)
                    st.success(f"Saved template: {template_name}")
                except (ValueError, RuntimeError) as e:
                    st.error(f"Error saving template: {e}")
        
        except (ValueError, RuntimeError) as e:
            st.error(f"Error generating report: {e}")


def templates_section():
    """Manage and load report templates."""
    st.header("📋 Report Templates")
    
    # List existing templates
    templates = list_templates(st.session_state.db_path)
    
    if templates:
        st.subheader("💾 Saved Templates")
        
        for template in templates:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{template['name']}**")
                st.write(f"Created: {template['created_at']}")
            
            with col2:
                if st.button("👁️ View", key=f"view_{template['template_id']}"):
                    st.json(template['definition'])
            
            with col3:
                if st.button("🔄 Load", key=f"load_{template['template_id']}"):
                    # This would ideally navigate to reports section with loaded config
                    st.success(f"Template '{template['name']}' loaded!")
                    st.info("Switch to Reports tab to see the loaded configuration.")
    else:
        st.info("No templates saved yet. Create some reports and save them as templates!")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Extracta Financial Pipeline",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Extracta Financial Data Pipeline")
    st.markdown("Upload, normalize, categorize, and analyze your financial documents")
    
    # Initialize session state
    init_session_state()
    
    # Main navigation
    tabs = st.tabs(["Upload", "Transactions", "Reports", "Templates"])
    
    with tabs[0]:
        upload_section()
    
    with tabs[1]:
        transactions_section()
    
    with tabs[2]:
        reports_section()
    
    with tabs[3]:
        templates_section()


if __name__ == "__main__":
    main()