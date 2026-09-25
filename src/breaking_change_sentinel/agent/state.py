"""
State definition for the LangGraph code migration agent.
"""

from pathlib import Path
from typing import Any, TypedDict


class AgentState(TypedDict):
    """
    Represents the complete state of the migration agent during execution.

    Attributes:
        file_path: Path to the target python file being refactored.
        source_code: Original content of the target file.
        detected_issues: Deprecated syntax nodes detected by the AST parser.
        retrieved_rules: Documentation chunks retrieved from the vector store.
        patched_code: LLM-generated refactored code.
        test_command: Command executed to test the modified code.
        test_passed: Flag indicating if pytest execution succeeded.
        test_output: Output logs (stdout/stderr) from the test run.
        iteration: Current self-correction iteration counter.
        max_iterations: Maximum allowed correction attempts before stopping.
        error_message: Explanatory error message if migration fails.
    """

    file_path: Path
    source_code: str
    detected_issues: list[dict[str, Any]]
    retrieved_rules: list[dict[str, Any]]
    patched_code: str | None
    test_command: str
    test_passed: bool
    test_output: str
    iteration: int
    max_iterations: int
    error_message: str | None


def create_initial_state(
    file_path: Path,
    source_code: str,
    test_command: str = "pytest",
    max_iterations: int = 3,
) -> AgentState:
    """
    Initializes and validates a fresh AgentState instance for a new migration run.

    Args:
        file_path: Path to the python file to refactor.
        source_code: Source code content as string.
        test_command: Pytest CLI invocation string.
        max_iterations: Maximum correction loops before abortion.

    Returns:
        A fully initialized AgentState dictionary.

    Raises:
        ValueError: If source_code is empty or max_iterations is less than 1.
    """

    if not source_code.strip():
        raise ValueError("Source code cannot be empty.")

    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1.")

    return AgentState(
        file_path=file_path,
        source_code=source_code,
        detected_issues=[],
        retrieved_rules=[],
        patched_code=None,
        test_command=test_command,
        test_passed=False,
        test_output="",
        iteration=0,
        max_iterations=max_iterations,
        error_message=None,
    )
