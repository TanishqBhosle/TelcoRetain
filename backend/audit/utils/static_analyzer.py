"""Static analysis utilities for code inspection without execution.

Provides AST parsing, file counting, pattern matching, and import
checking capabilities used by multiple audit phases.
"""

import ast
import re
from pathlib import Path


class StaticAnalyzer:
    """Collection of static analysis utilities for code inspection.

    All methods are static and operate on file paths or parsed AST
    modules. No execution of the target code is performed.
    """

    @staticmethod
    def count_files(directory: Path, pattern: str) -> int:
        """Count files matching a glob pattern in a directory.

        Args:
            directory: Root directory to search within.
            pattern: Glob pattern to match files (e.g. "*.py", "**/*.tsx").

        Returns:
            Number of files matching the pattern. Returns 0 if the
            directory does not exist.
        """
        if not directory.exists():
            return 0
        return len(list(directory.glob(pattern)))

    @staticmethod
    def parse_python_module(file_path: Path) -> ast.Module:
        """Parse a Python file into an AST module node.

        Args:
            file_path: Path to the Python source file to parse.

        Returns:
            Parsed AST Module node.

        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file contains invalid Python syntax.
        """
        return ast.parse(file_path.read_text(encoding="utf-8"))

    @staticmethod
    def find_class_definitions(module: ast.Module) -> list[ast.ClassDef]:
        """Extract all class definitions from an AST module.

        Walks the entire AST tree, finding class definitions at any
        nesting depth (including nested classes).

        Args:
            module: Parsed AST module to inspect.

        Returns:
            List of ClassDef AST nodes found in the module.
        """
        return [node for node in ast.walk(module) if isinstance(node, ast.ClassDef)]

    @staticmethod
    def find_function_definitions(module: ast.Module) -> list[ast.FunctionDef]:
        """Extract all function and method definitions from an AST module.

        Finds both synchronous (FunctionDef) and asynchronous
        (AsyncFunctionDef) function definitions at any nesting depth.

        Args:
            module: Parsed AST module to inspect.

        Returns:
            List of FunctionDef and AsyncFunctionDef AST nodes.
        """
        return [
            node
            for node in ast.walk(module)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    @staticmethod
    def grep_pattern(
        directory: Path, pattern: str, extensions: list[str]
    ) -> list[tuple[Path, int, str]]:
        """Search for a regex pattern in files with given extensions.

        Recursively searches all files matching the specified extensions
        within the directory tree. Returns matches with file path, line
        number, and stripped line content.

        Args:
            directory: Root directory to search recursively.
            pattern: Regular expression pattern to search for.
            extensions: List of file extensions to include (e.g. [".py", ".ts"]).

        Returns:
            List of tuples (file_path, line_number, line_content) for each
            matching line. Line numbers are 1-indexed. Line content is
            stripped of leading/trailing whitespace. Returns an empty list
            if the directory does not exist.
        """
        if not directory.exists():
            return []

        results: list[tuple[Path, int, str]] = []
        compiled = re.compile(pattern)

        for ext in extensions:
            for file in directory.rglob(f"*{ext}"):
                if not file.is_file():
                    continue
                try:
                    content = file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                for i, line in enumerate(content.splitlines(), 1):
                    if compiled.search(line):
                        results.append((file, i, line.strip()))

        return results

    @staticmethod
    def check_imports(module: ast.Module, target_module: str) -> bool:
        """Check if a module imports from a target module path.

        Inspects all `from X import Y` statements in the AST and checks
        whether the import source contains the target module string.

        Args:
            module: Parsed AST module to inspect.
            target_module: Module path substring to search for
                (e.g. "services" or "app.repositories").

        Returns:
            True if any ImportFrom statement references the target module,
            False otherwise.
        """
        for node in ast.walk(module):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and target_module in node.module
            ):
                return True
        return False
