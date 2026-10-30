"""
Unit tests for the LangGraph agent execution nodes.
"""

from pathlib import Path

from breaking_change_sentinel.agent.nodes import (
    analyze_ast_node,
    retrieve_documentation_node,
    generate_patch_node,
)
from breaking_change_sentinel.agent.state import create_initial_state
from unittest.mock import MagicMock, patch


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

    assert "extracted_usages" in update
    assert len(update["extracted_usages"]) > 0
    issue_types = [issue["type"] for issue in update["extracted_usages"]]
    assert "validator" in issue_types or "deprecated_decorator" in issue_types


def test_analyze_ast_node_extracts_all_target_usages() -> None:
    """Verifies that the AST node extracts all usages for downstream RAG evaluation."""
    clean_code = """
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        return v
"""
    state = create_initial_state(
        file_path=Path("clean.py"), source_code=clean_code, target_module="pydantic"
    )

    update = analyze_ast_node(state)

    assert "extracted_usages" in update
    names = [issue["name"] for issue in update["extracted_usages"]]
    assert "BaseModel" in names
    assert "field_validator" in names


def test_analyze_ast_node_syntax_error_handled_gracefully() -> None:
    """Verifies that syntax errors do not crash the node and are reported as issues."""
    broken_code = "class IncompleteModel(BaseModel):\n    def def def"
    state = create_initial_state(
        file_path=Path("broken.py"), source_code=broken_code, target_module="pydantic"
    )

    update = analyze_ast_node(state)

    assert "extracted_usages" in update
    assert len(update["extracted_usages"]) == 1
    assert update["extracted_usages"][0]["type"] == "syntax_error"


@patch("breaking_change_sentinel.agent.nodes.MigrationVectorStore")
def test_retrieve_documentation_node_with_issues(mock_store_class: MagicMock) -> None:
    """Verifies that documentation is retrieved and deduplicated for detected issues."""
    # Configure the mock to return a dummy document
    mock_instance = MagicMock()
    mock_instance.search.return_value = [
        {
            "content": "Use field_validator instead of validator.",
            "score": 0.95,
            "metadata": {"chunk_id": "chunk_123", "source": "docs/migration.md"},
        }
    ]
    mock_store_class.return_value = mock_instance

    state = create_initial_state(
        file_path=Path("dummy.py"),
        source_code="dummy code",
        target_module="pydantic",
    )
    state["extracted_usages"] = [
        {"type": "deprecated_decorator", "name": "validator", "line": 5},
        {"type": "deprecated_import", "name": "validator"},
    ]

    update = retrieve_documentation_node(state)

    assert "retrieved_rules" in update
    assert len(update["retrieved_rules"]) == 1
    assert "field_validator" in update["retrieved_rules"][0]["content"]
    assert mock_instance.search.call_count == 2


@patch("breaking_change_sentinel.agent.nodes.MigrationVectorStore")
def test_retrieve_documentation_node_empty_issues(mock_store_class: MagicMock) -> None:
    """Verifies that retrieval is skipped if no issues are present."""
    mock_instance = MagicMock()
    mock_store_class.return_value = mock_instance

    state = create_initial_state(
        file_path=Path("dummy.py"),
        source_code="dummy code",
        target_module="pydantic",
    )

    update = retrieve_documentation_node(state)

    assert "retrieved_rules" in update
    assert len(update["retrieved_rules"]) == 0
    mock_instance.search.assert_not_called()


@patch("breaking_change_sentinel.agent.nodes.completion")
def test_generate_patch_node_applies_fixes(mock_completion: MagicMock) -> None:
    """Verifies that the LLM is called and raw patched code is extracted cleanly."""

    # Configuration du mock LiteLLM
    mock_message = MagicMock()
    mock_message.content = "```python\nclass UserModel(BaseModel):\n    pass\n```"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response

    state = create_initial_state(
        file_path=Path("dummy.py"),
        source_code="class UserModel(BaseModel): pass",
        target_module="pydantic",
    )
    state["detected_issues"] = [{"name": "validator"}]
    state["retrieved_rules"] = [{"content": "Use field_validator instead."}]

    update = generate_patch_node(state)

    assert "patched_code" in update
    assert "class UserModel" in update["patched_code"]

    # Vérification stricte du nettoyage des balises Markdown
    assert "```python" not in update["patched_code"]
    assert "```" not in update["patched_code"]
    mock_completion.assert_called_once()
