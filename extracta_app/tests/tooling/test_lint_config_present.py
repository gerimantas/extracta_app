"""
Tooling test to verify lint configuration is present and properly set up.

This test should initially fail until proper ruff and mypy configurations are added.
"""
import pytest
from pathlib import Path


class TestLintConfigPresent:
    
    def test_ruff_config_exists_and_valid(self):
        """Test that ruff configuration exists and contains required settings."""
        # Check for pyproject.toml with ruff config (in project root)
        pyproject_path = Path("../pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml file not found in project root"
        
        content = pyproject_path.read_text(encoding="utf-8")
        
        # Verify ruff configuration sections exist
        assert "[tool.ruff]" in content, "Missing [tool.ruff] section in pyproject.toml"
        assert "[tool.ruff.lint]" in content, "Missing [tool.ruff.lint] section in pyproject.toml"
        
        # Verify key settings are configured
        assert "line-length" in content, "Missing line-length setting in ruff config"
        assert "target-version" in content, "Missing target-version in ruff config"
        assert "select" in content, "Missing select rules in ruff config"
        
        # Verify essential rules are enabled
        assert '"E"' in content or "'E'" in content, "Missing pycodestyle errors (E) in ruff select"
        assert '"F"' in content or "'F'" in content, "Missing pyflakes (F) in ruff select"
        assert '"I"' in content or "'I'" in content, "Missing isort (I) in ruff select"
    
    def test_mypy_config_exists(self):
        """Test that mypy configuration exists (optional but recommended)."""
        # Check for mypy configuration in either mypy.ini or pyproject.toml (in project root)
        mypy_ini = Path("../mypy.ini")
        pyproject_toml = Path("../pyproject.toml")
        
        has_mypy_ini = mypy_ini.exists()
        has_mypy_in_pyproject = False
        
        if pyproject_toml.exists():
            content = pyproject_toml.read_text(encoding="utf-8")
            has_mypy_in_pyproject = "[tool.mypy]" in content
        
        # At least one mypy config should exist
        assert has_mypy_ini or has_mypy_in_pyproject, "No mypy configuration found (mypy.ini or [tool.mypy] in pyproject.toml)"
        
        if has_mypy_ini:
            mypy_content = mypy_ini.read_text(encoding="utf-8")
            assert "[tool.mypy]" in mypy_content or "[mypy]" in mypy_content, "Invalid mypy.ini format"
    
    def test_lint_commands_available(self):
        """Test that lint tools can be invoked (basic smoke test)."""
        import subprocess
        import sys
        
        # Test ruff is available
        try:
            result = subprocess.run([sys.executable, "-m", "ruff", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            # If ruff is not installed, this test documents the requirement
            if result.returncode != 0:
                pytest.skip("ruff not installed - install with: pip install ruff")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("ruff not available - install with: pip install ruff")
        
        # Test mypy is available (optional)
        try:
            result = subprocess.run([sys.executable, "-m", "mypy", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            # mypy is optional, so we just note if it's missing
            if result.returncode != 0:
                pytest.skip("mypy not installed - optional: pip install mypy")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mypy not available - optional: pip install mypy")
    
    def test_lint_stage_integration(self):
        """Test that lint configuration integrates with project structure."""
        # Verify configuration targets the correct directories
        pyproject_path = Path("../pyproject.toml")
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8")
            
            # Should have per-file ignores for tests
            if "[tool.ruff.lint.per-file-ignores]" in content:
                assert "tests/" in content, "Missing test directory configuration in ruff"
        
        # Verify src directory exists (target for linting)
        src_dir = Path("src")
        assert src_dir.exists(), "Source directory 'src' not found"
        
        # Verify tests directory exists
        tests_dir = Path("tests")
        assert tests_dir.exists(), "Tests directory 'tests' not found"