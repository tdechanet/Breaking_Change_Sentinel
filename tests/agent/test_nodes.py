"""
Unit tests for the LangGraph agent execution nodes.
"""

from pathlib import Path

from breaking_change_sentinel.agent.nodes import analyze_ast_node
from breaking_change_sentinel.agent.state import create_initial_state


def test_analyze_ast_node_detects_deprecated_validators() -> None:
    """Verifies that analyze_ast_node extracts deprecated validator decorators."""
    code_with_issues = """
from pydantic import BaseModel, validator

class UserModel(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, v):
        return v
"""
    state = create_initial_state(
        file_path=Path("models.py"),
        source_code=code_with_issues,
        target_module="pydantic",
    )

    update = analyze_ast_node(state)

    assert "detected_issues" in update
    assert len(update["detected_issues"]) > 0
    issue_types = [issue["type"] for issue in update["detected_issues"]]
    assert "validator" in issue_types or "deprecated_decorator" in issue_types


def test_analyze_ast_node_clean_code_returns_empty_list() -> None:
    """Verifies that clean code yields an empty detected_issues list."""
    clean_code = """
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v
"""
    state = create_initial_state(
        file_path=Path("clean.py"), source_code=clean_code, target_module="pydantic"
    )

    update = analyze_ast_node(state)

    assert "detected_issues" in update
    assert len(update["detected_issues"]) == 0


def test_analyze_ast_node_syntax_error_handled_gracefully() -> None:
    """Verifies that syntax errors do not crash the node and are reported as issues."""
    broken_code = "class IncompleteModel(BaseModel):\n    def def def"
    state = create_initial_state(
        file_path=Path("broken.py"), source_code=broken_code, target_module="pydantic"
    )

    update = analyze_ast_node(state)

    assert "detected_issues" in update
    assert len(update["detected_issues"]) == 1
    assert update["detected_issues"][0]["type"] == "syntax_error"
