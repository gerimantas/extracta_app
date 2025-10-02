"""Documentation tests for README.md (Task 56).

Tests that README.md contains required sections and follows documentation standards.
Uses regex checks to validate key content is present.
"""
import re
from pathlib import Path
import pytest

class TestReadmeDocumentation:
    
    @pytest.fixture
    def readme_content(self):
        """Load README.md content for testing."""
        readme_path = Path(__file__).parent.parent.parent.parent / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")
        
        return readme_path.read_text(encoding="utf-8")
    
    def test_readme_exists(self):
        """Test that README.md file exists in project root."""
        readme_path = Path(__file__).parent.parent.parent.parent / "README.md"
        assert readme_path.exists(), "README.md file not found in project root"
    
    def test_project_title_and_description_present(self, readme_content):
        """Test that README contains project title and description."""
        # Project title should be an H1 heading
        assert re.search(r'^# Extracta', readme_content, re.MULTILINE), "Missing project title (H1 heading)"
        
        # Should mention key concepts
        assert re.search(r'deterministic', readme_content, re.IGNORECASE), "Missing 'deterministic' concept"
        assert re.search(r'financial data', readme_content, re.IGNORECASE), "Missing 'financial data' description"
        assert re.search(r'pipeline', readme_content, re.IGNORECASE), "Missing 'pipeline' concept"
    
    def test_version_information_present(self, readme_content):
        """Test that README contains version information."""
        # Should have version mentioned (look for actual version string)
        assert "0.1.0" in readme_content or re.search(r'\\d+\\.\\d+\\.\\d+', readme_content), "Missing version information"
    
    def test_architecture_section_present(self, readme_content):
        """Test that README contains architecture information."""
        assert re.search(r'## Architecture', readme_content), "Missing Architecture section"
        assert re.search(r'Core Pipeline Flow', readme_content), "Missing pipeline flow description"
        
        # Should describe the main pipeline stages
        pipeline_stages = ['Ingestion', 'Extraction', 'Validation', 'Normalization', 'SQLite']
        for stage in pipeline_stages:
            assert re.search(stage, readme_content), f"Missing pipeline stage: {stage}"
    
    def test_features_section_present(self, readme_content):
        """Test that README contains features section."""
        assert re.search(r'## Features', readme_content), "Missing Features section"
        
        # Key features should be mentioned
        key_features = ['Deterministic Processing', 'Local-First', 'Multi-Format Support']
        for feature in key_features:
            assert re.search(feature, readme_content), f"Missing key feature: {feature}"
    
    def test_quick_start_section_present(self, readme_content):
        """Test that README contains quick start instructions."""
        assert re.search(r'## Quick Start', readme_content), "Missing Quick Start section"
        assert re.search(r'### Prerequisites', readme_content), "Missing Prerequisites subsection"
        assert re.search(r'### Installation', readme_content), "Missing Installation subsection"
        
        # Should have basic commands
        assert re.search(r'pip install', readme_content), "Missing pip install instructions"
        assert re.search(r'streamlit run', readme_content), "Missing streamlit run command"
    
    def test_usage_workflow_section_present(self, readme_content):
        """Test that README contains usage workflow."""
        assert re.search(r'## Usage Workflow', readme_content), "Missing Usage Workflow section"
        
        # Should describe the main workflow steps
        workflow_steps = ['Upload Documents', 'Review Transactions', 'Generate Reports', 'Save Templates']
        for step in workflow_steps:
            assert re.search(step, readme_content), f"Missing workflow step: {step}"
    
    def test_deterministic_rerun_section_present(self, readme_content):
        """Test that README contains deterministic re-run section as required by task."""
        assert re.search(r'## Deterministic Re-run', readme_content), "Missing Deterministic Re-run section"
        assert re.search(r'deterministic processing', readme_content, re.IGNORECASE), "Missing deterministic processing concept"
        
        # Should mention key deterministic concepts
        deterministic_concepts = ['Same Input.*Same Output', 'Reproducible Hashes', 'normalization_hash']
        for concept in deterministic_concepts:
            assert re.search(concept, readme_content, re.IGNORECASE), f"Missing deterministic concept: {concept}"
    
    def test_data_model_section_present(self, readme_content):
        """Test that README contains data model information."""
        assert re.search(r'## Data Model', readme_content), "Missing Data Model section"
        
        # Should describe core transaction fields
        transaction_fields = ['transaction_id', 'transaction_date', 'description', 'amount_in', 'amount_out']
        for field in transaction_fields:
            assert re.search(field, readme_content), f"Missing transaction field: {field}"
        
        # Should mention the mutual exclusivity constraint
        assert re.search(r'amount_in.*OR.*amount_out', readme_content), "Missing amount constraint description"
    
    def test_testing_section_present(self, readme_content):
        """Test that README contains testing instructions."""
        assert re.search(r'## Testing', readme_content), "Missing Testing section"
        assert re.search(r'pytest', readme_content), "Missing pytest command"
        
        # Should mention test categories
        test_categories = ['unit', 'integration', 'contract']
        for category in test_categories:
            assert re.search(category, readme_content), f"Missing test category: {category}"
    
    def test_development_section_present(self, readme_content):
        """Test that README contains development information."""
        assert re.search(r'## Development', readme_content), "Missing Development section"
        assert re.search(r'### Project Structure', readme_content), "Missing Project Structure subsection"
        
        # Should mention key directories
        key_directories = ['src/', 'tests/', 'contracts/']
        for directory in key_directories:
            assert re.search(re.escape(directory), readme_content), f"Missing directory: {directory}"
    
    def test_code_quality_tools_mentioned(self, readme_content):
        """Test that README mentions code quality tools."""
        # Should mention the tools we've configured
        quality_tools = ['ruff', 'mypy', 'pytest']
        for tool in quality_tools:
            assert re.search(tool, readme_content), f"Missing quality tool: {tool}"
    
    def test_markdown_formatting_quality(self, readme_content):
        """Test basic markdown formatting quality."""
        # Remove code blocks before counting headings to avoid false positives
        content_without_code = re.sub(r'```.*?```', '', readme_content, flags=re.DOTALL)
        
        # Should have proper heading hierarchy (exactly one H1)
        h1_count = len(re.findall(r'^# ', content_without_code, re.MULTILINE))
        assert h1_count == 1, f"Should have exactly one H1 heading, found {h1_count}"
        
        # Should have multiple H2 sections
        h2_count = len(re.findall(r'^## ', content_without_code, re.MULTILINE))
        assert h2_count >= 5, f"Should have at least 5 H2 sections, found {h2_count}"
        
        # Code blocks should be properly formatted
        code_block_count = len(re.findall(r'```', readme_content))
        assert code_block_count % 2 == 0, "Unclosed code blocks detected"
    
    def test_contains_essential_keywords(self, readme_content):
        """Test that README contains essential keywords for searchability."""
        essential_keywords = [
            'financial',
            'PDF',
            'transaction',
            'normalization',
            'deterministic',
            'local',
            'Streamlit'
        ]
        
        for keyword in essential_keywords:
            assert re.search(keyword, readme_content, re.IGNORECASE), f"Missing essential keyword: {keyword}"