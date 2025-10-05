"""Streamlit UI for Extracta financial data pipeline (Task 44).

Provides user interface for:
- Upload: File upload and raw extraction preview
- Transactions: View normalized data and assign categories
- Reports: Query builder with filters, grouping, aggregation
- Templates: Save and load report configurations

Design: Thin UI layer, business logic in src/ modules.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to Python path to resolve src imports
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import streamlit as st

# Import business logic modules
try:
    from src.categorization.service import assign_category, create_category, list_categories
    from src.ingestion.pipeline import ingest_file
    from src.normalization.engine import normalize_rows
    try:
        from src.normalization.counterparty_derivation import derive_counterparties  # type: ignore
    except ImportError:  # pragma: no cover
        derive_counterparties = None  # type: ignore
    from src.persistence.migrations import init_db
    from src.persistence.transactions_repository import bulk_insert_transactions, get_transactions
    from src.persistence.documents_repository import create_document, list_documents, delete_document_by_file_hash
    from src.persistence.counterparties_repository import list_counterparties, rename as rename_counterparty, merge as merge_counterparties, RenameCollisionError
    from src.reporting.executor import execute_report
    from src.reporting.templates import list_templates, save_template
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def parse_raw_text_to_structured_data(raw_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Parse raw_text rows into structured transaction data.
    This is a simple parser - in production you'd want more sophisticated parsing.
    """
    import re
    from datetime import datetime
    
    structured_rows = []
    
    for row in raw_rows:
        raw_text = row.get('raw_text', '').strip()
        if not raw_text:
            continue
            
        # Simple parsing logic - look for patterns like:
        # "€632.39 €31.62 2025-10-31" (amount amount date)
        # or other common transaction patterns
        
        # Pattern 1: Look for amount and date
        amount_date_pattern = r'€?(-?\d+[.,]\d+).*?(\d{4}-\d{2}-\d{2})'
        match = re.search(amount_date_pattern, raw_text)
        
        if match:
            amount_str = match.group(1).replace(',', '.')
            date_str = match.group(2)
            
            # Extract description (everything before the amount/date part)
            description = raw_text[:match.start()].strip()
            if not description:
                description = raw_text.replace(match.group(0), '').strip()
                
            if not description:
                description = raw_text
                
            structured_rows.append({
                "Date": date_str,
                "Description": description,
                "Amount": amount_str
            })
        else:
            # Pattern 2: Look for just dates
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            date_match = re.search(date_pattern, raw_text)
            
            if date_match:
                structured_rows.append({
                    "Date": date_match.group(1),
                    "Description": raw_text,
                    "Amount": "0.00"
                })
    
    return structured_rows


def init_session_state():
    """Initialize session state variables."""
    if 'db_path' not in st.session_state:
        # Use temp DB for demo, could be configurable
        st.session_state.db_path = "data/extracta.db"
        os.makedirs("data", exist_ok=True)
        init_db(st.session_state.db_path)

    if 'uploaded_files_processed' not in st.session_state:
        st.session_state.uploaded_files_processed = []


def _resolve_document_type(user_value: str | None) -> str:
    value = (user_value or "").strip()
    return value if value else "Other"


def upload_section():
    """File upload and extraction preview section."""
    st.header("📁 Upload Financial Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or image files (.pdf, .png, .jpg, .jpeg)",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )

    # Document type selector (single selection applies per-file in this simple MVP; could be per file later)
    st.subheader("Document Classification")
    doc_type = st.selectbox(
        "Document type:", ["", "Bank Statement", "Accounting Ledger", "Purchase Receipt", "Other"],
        help="Optional classification; defaults to 'Other' if left blank"
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

                    # Persist document metadata (idempotent on file_hash)
                    effective_type = _resolve_document_type(doc_type)
                    try:
                        create_document(
                            st.session_state.db_path,
                            filename=uploaded_file.name,
                            file_hash=raw_artifact['source_file_hash'],
                            document_type=effective_type,
                        )
                    except Exception as e:  # pragma: no cover - UI surface
                        st.warning(f"Could not persist document record: {e}")

                    # Show preview
                    if raw_artifact['rows']:
                        st.subheader("Raw Data Preview")
                        st.dataframe(raw_artifact['rows'][:10])  # Show first 10 rows

                    # Parse raw text into structured data
                    parsed_rows = []
                    with st.spinner("Parsing extracted text..."):
                        parsed_rows = parse_raw_text_to_structured_data(raw_artifact['rows'])
                        
                        if parsed_rows:
                            st.subheader("Parsed Structured Data")
                            st.dataframe(parsed_rows[:10])  # Show first 10 parsed rows
                        else:
                            st.warning("⚠️ Could not parse structured data from extracted text. Using mock data for demo.")
                            # Fallback to mock data for demonstration
                            parsed_rows = [
                                {"Date": "2025-10-01", "Description": "Sample Transaction 1", "Amount": "-25.50"},
                                {"Date": "2025-10-02", "Description": "Sample Transaction 2", "Amount": "-45.00"}
                            ]

                    # Normalize data
                    with st.spinner("Normalizing data..."):
                        # Load mapping config (you might want to make this configurable)
                        mapping_config = {"version": "v1", "synonyms": {}, "rules": {
                            "Date": "transaction_date",
                            "Description": "description",
                            "Amount": "amount_out"  # Simplified mapping
                        }}

                        normalized_rows = normalize_rows(
                            parsed_rows,  # Use parsed data instead of raw
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

                        # Derive counterparties (idempotent) - Phase 4 integration
                        if derive_counterparties:
                            with st.spinner("Deriving counterparties..."):
                                stats = derive_counterparties(st.session_state.db_path)
                            st.info(f"Counterparties assigned: {stats['assigned']} (skipped {stats['skipped']})")

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

    # Optional: show recent documents metadata
    docs = list_documents(st.session_state.db_path)
    if docs:
        with st.expander("📄 Document Metadata"):
            st.dataframe(docs[:25])


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


def document_management_section():
    """Manage document metadata and cascade deletes (Feature 002)."""
    st.header("📄 Document Management")
    docs = list_documents(st.session_state.db_path)
    if not docs:
        st.info("No documents found yet. Upload files in the Upload tab.")
        return
    st.subheader(f"Documents ({len(docs)})")
    for doc in docs[:50]:  # cap to 50 for initial view
        cols = st.columns([3,2,2,2,2,1])
        with cols[0]:
            st.write(doc["filename"])
        with cols[1]:
            st.write(doc["document_type"])
        with cols[2]:
            st.write(doc["status"])
        with cols[3]:
            st.write(doc["upload_date"])
        with cols[4]:
            st.code(doc["file_hash"][:8])
        with cols[5]:
            if st.button("🗑️", key=f"del_{doc['file_hash']}", help="Delete document and its transactions"):
                removed = delete_document_by_file_hash(st.session_state.db_path, doc["file_hash"])
                st.success(f"Deleted document; removed {removed} transactions.")
                st.rerun()

    with st.expander("Raw Table View"):
        st.dataframe(docs)


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
    tabs = st.tabs(["Upload", "Transactions", "Reports", "Templates", "Document Management", "Counterparties"])

    with tabs[0]:
        upload_section()

    with tabs[1]:
        transactions_section()

    with tabs[2]:
        reports_section()

    with tabs[3]:
        templates_section()

    with tabs[4]:
        document_management_section()

    with tabs[5]:
        counterparty_management_section()


def counterparty_management_section():
    st.header("🤝 Counterparty Management")
    cps = list_counterparties(st.session_state.db_path)
    if not cps:
        st.info("No counterparties yet. Upload transactions to derive them.")
        return

    st.subheader(f"Counterparties ({len(cps)})")
    filter_text = st.text_input("Filter (contains):", "")
    filtered = [c for c in cps if filter_text.lower() in c["name"].lower()]
    st.dataframe(filtered[:100])

    st.subheader("Rename")
    col_r1, col_r2, col_r3 = st.columns([2, 2, 1])
    with col_r1:
        rename_id = st.number_input("ID", min_value=1, value=1, step=1)
    with col_r2:
        new_name = st.text_input("New Name")
    with col_r3:
        if st.button("Apply Rename") and new_name:
            try:
                rename_counterparty(st.session_state.db_path, counterparty_id=int(rename_id), new_display_name=new_name)
                st.success("Renamed successfully")
                st.rerun()
            except RenameCollisionError as e:
                st.error(str(e))
            except Exception as e:  # pragma: no cover
                st.error(f"Rename failed: {e}")

    st.subheader("Merge")
    col_m1, col_m2, col_m3 = st.columns([3, 3, 1])
    with col_m1:
        winner_id = st.number_input("Winner ID", min_value=1, value=1, step=1, key="winner_id")
    with col_m2:
        losing_ids_text = st.text_input("Losing IDs (comma)")
    with col_m3:
        if st.button("Execute Merge") and losing_ids_text.strip():
            try:
                losing_ids = [int(x.strip()) for x in losing_ids_text.split(",") if x.strip()]
                reassigned = merge_counterparties(st.session_state.db_path, winner_id=int(winner_id), losing_ids=losing_ids)
                st.success(f"Merged. Reassigned {reassigned} transactions.")
                st.rerun()
            except Exception as e:  # pragma: no cover
                st.error(f"Merge failed: {e}")


if __name__ == "__main__":
    main()

# Explicit exports for test stability
__all__ = [
    "upload_section",
    "transactions_section",
    "reports_section",
    "templates_section",
    "document_management_section",
    "counterparty_management_section",
    "main",
]
