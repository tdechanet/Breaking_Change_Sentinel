"""
Execution nodes for the LangGraph code migration agent.
"""

import ast
import logging
from typing import Any

from breaking_change_sentinel.agent.state import AgentState
from breaking_change_sentinel.parser.ast_parser import parse_code_for_deprecations
from breaking_change_sentinel.rag.vector_store import MigrationVectorStore

logger = logging.getLogger(__name__)


def analyze_ast_node(state: AgentState) -> dict[str, Any]:
    """
    Parses the target source code via AST and identifies deprecated Pydantic constructs.

    Args:
        state: Current graph state containing the source code.

    Returns:
        Partial state update dictionary containing 'extracted_usages'.
    """

    source_code = state["source_code"]

    try:
        ast.parse(source_code)
    except SyntaxError as e:
        return {"extracted_usages": [{"type": "syntax_error", "message": str(e)}]}

    extracted_usages = parse_code_for_deprecations(source_code, state["target_module"])

    formatted_issues = []

    for imp in extracted_usages.get("imports", []):
        formatted_issues.append({"type": "deprecated_import", "name": imp})

    for dec in extracted_usages.get("decorators", []):
        formatted_issues.append(
            {"type": dec["name"], "name": dec["name"], "line": dec["line"]}
        )

    return {"extracted_usages": formatted_issues}


def retrieve_documentation_node(state: AgentState) -> dict[str, Any]:
    """
    Queries the vector store for each detected issue to retrieve migration rules.

    Args:
        state: Current graph state containing 'extracted_usages' and 'target_module'.

    Returns:
        Partial state update dictionary containing 'retrieved_rules'.
    """
    extracted_usages = state.get("extracted_usages", [])
    if not extracted_usages:
        logger.info("No usages extracted. Skipping documentation retrieval.")
        return {"retrieved_rules": []}

    target_module = state.get("target_module", "")

    vector_store = MigrationVectorStore()

    detected_issues: list[dict[str, Any]] = []
    retrieved_rules_dict: dict[str, dict[str, Any]] = {}

    for usage in extracted_usages:
        deprecation_search = vector_store.search(
            f"{target_module}: {usage['name']} migration deprecation"
        )

        if deprecation_search:
            detected_issues.append(usage)
            for result in deprecation_search:
                print("Valeur de result :", result)
                retrieved_rules_dict[result["metadata"]["chunk_id"]] = {
                    "content": result["content"],
                    "source": result["metadata"]["source"],
                }

    return {
        "detected_issues": detected_issues,
        "retrieved_rules": list(retrieved_rules_dict.values()),
    }
