"""
Module for parsing Python source code and identifying deprecated usages via AST.
"""

import ast
from pathlib import Path
from typing import Any


class DeprecationAnalyzer(ast.NodeVisitor):
    """
    AST Visitor to detect specific deprecated imports and decorators.
    """

    def __init__(self, target_module: str) -> None:
        self.target_module = target_module
        self.found_imports: set[str] = set()
        self.found_decorators: list[dict[str, Any]] = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Extracts imported names if the module matches target_module.
        """
        if node.module == self.target_module:
            for alias in node.names:
                self.found_imports.add(alias.name)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Detects specific decorators used on functions/methods.
        """
        for decorator in node.decorator_list:
            match decorator:
                case ast.Call(func=ast.Name(id=name)) | ast.Name(id=name):
                    self.found_decorators.append({"name": name, "line": node.lineno})

                case _:
                    continue

        self.generic_visit(node)


def parse_file_for_deprecations(file_path: Path, target_module: str) -> dict[str, Any]:
    """
    Parses a Python file and extracts deprecated usages related to the target module.
    """

    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content)

    analyzer = DeprecationAnalyzer(target_module)
    analyzer.visit(tree)

    return {"imports": analyzer.found_imports, "decorators": analyzer.found_decorators}
