"""
Unit tests for the AST parser logic.
"""

import pytest
import textwrap
from pathlib import Path
from breaking_change_sentinel.parser.ast_parser import parse_file_for_deprecations

@pytest.fixture
def sample_deprecated_code(tmp_path: Path) -> Path:
    """Fixture to generate a temporary Python file with deprecated code."""
    code = textwrap.dedent("""
    from pydantic import BaseModel, validator
    
    class User(BaseModel):
        name: str
    
        @validator('name')
        def check_name(cls, v):
            return v
    """).strip()
    file_path = tmp_path / "dummy_model.py"
    file_path.write_text(code)
    return file_path

def test_parse_file_for_deprecations(sample_deprecated_code: Path) -> None:
    """Tests if the AST parser correctly identifies target imports and decorators."""
    results = parse_file_for_deprecations(sample_deprecated_code, target_module="pydantic")
    
    assert "BaseModel" in results["imports"]
    assert "validator" in results["imports"]
    
    assert len(results["decorators"]) == 1
    assert results["decorators"][0]["name"] == "validator"
    assert results["decorators"][0]["line"] == 7