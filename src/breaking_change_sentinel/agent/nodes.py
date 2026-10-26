"""
Execution nodes for the LangGraph code migration agent.
"""

import ast
import logging
from typing import Any

from breaking_change_sentinel.agent.state import AgentState
from breaking_change_sentinel.parser.ast_parser import parse_code_for_deprecations

logger = logging.getLogger(__name__)


def analyze_ast_node(state: AgentState) -> dict[str, Any]:
    """
    Parses the target source code via AST and identifies deprecated Pydantic constructs.

    Args:
        state: Current graph state containing the source code.

    Returns:
        Partial state update dictionary containing 'detected_issues'.
    """

    source_code = state["source_code"]

    try:
        ast.parse(source_code)
    except SyntaxError as e:
        return {"detected_issues": [{"type": "syntax_error", "message": str(e)}]}

    detected_issues = parse_code_for_deprecations(source_code, state["target_module"])

    formatted_issues = []

    for imp in detected_issues.get("imports", []):
        formatted_issues.append({"type": "deprecated_import", "name": imp})

    for dec in detected_issues.get("decorators", []):
        formatted_issues.append(
            {"type": dec["name"], "name": dec["name"], "line": dec["line"]}
        )

    return {"detected_issues": formatted_issues}
