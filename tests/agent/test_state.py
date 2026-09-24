"""
Unit tests for AgentState initialization and validation.
"""

from pathlib import Path
import pytest

from breaking_change_sentinel.agent.state import create_initial_state


def test_create_initial_state_success() -> None:
    """Verifies that create_initial_state sets default values correctly."""
    file_path = Path("src/models.py")
    source_code = "from pydantic import BaseModel\n\nclass User(BaseModel): pass"

    state = create_initial_state(file_path=file_path, source_code=source_code)

    assert state["file_path"] == file_path
    assert state["source_code"] == source_code
    assert state["detected_issues"] == []
    assert state["retrieved_rules"] == []
    assert state["patched_code"] is None
    assert state["test_passed"] is False
    assert state["test_output"] == ""
    assert state["iteration"] == 0
    assert state["max_iterations"] == 3
    assert state["error_message"] is None


def test_create_initial_state_empty_code_raises_error() -> None:
    """Verifies that an empty source code string raises a ValueError."""
    with pytest.raises(ValueError, match="Source code cannot be empty"):
        create_initial_state(file_path=Path("dummy.py"), source_code="   \n ")


def test_create_initial_state_invalid_max_iterations_raises_error() -> None:
    """Verifies that max_iterations < 1 raises a ValueError."""
    with pytest.raises(ValueError, match="max_iterations must be at least 1"):
        create_initial_state(
            file_path=Path("dummy.py"),
            source_code="print('ok')",
            max_iterations=0,
        )
