"""Tests for the static analysis utilities."""

import ast
from pathlib import Path

import pytest

from audit.utils.static_analyzer import StaticAnalyzer


class TestCountFiles:
    """Tests for StaticAnalyzer.count_files."""

    def test_counts_matching_files(self, tmp_path):
        (tmp_path / "a.py").write_text("# module a")
        (tmp_path / "b.py").write_text("# module b")
        (tmp_path / "c.txt").write_text("not python")

        assert StaticAnalyzer.count_files(tmp_path, "*.py") == 2

    def test_returns_zero_for_empty_directory(self, tmp_path):
        assert StaticAnalyzer.count_files(tmp_path, "*.py") == 0

    def test_returns_zero_for_nonexistent_directory(self, tmp_path):
        nonexistent = tmp_path / "does_not_exist"
        assert StaticAnalyzer.count_files(nonexistent, "*.py") == 0

    def test_counts_with_recursive_pattern(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "top.py").write_text("")
        (sub / "nested.py").write_text("")

        assert StaticAnalyzer.count_files(tmp_path, "**/*.py") == 2

    def test_counts_non_python_extensions(self, tmp_path):
        (tmp_path / "app.tsx").write_text("")
        (tmp_path / "util.tsx").write_text("")
        (tmp_path / "style.css").write_text("")

        assert StaticAnalyzer.count_files(tmp_path, "*.tsx") == 2


class TestParsePythonModule:
    """Tests for StaticAnalyzer.parse_python_module."""

    def test_parses_valid_python_file(self, tmp_path):
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\n")

        module = StaticAnalyzer.parse_python_module(py_file)

        assert isinstance(module, ast.Module)
        assert len(module.body) == 1

    def test_parses_file_with_classes_and_functions(self, tmp_path):
        py_file = tmp_path / "sample.py"
        py_file.write_text("class Foo:\n    pass\n\ndef bar():\n    pass\n")

        module = StaticAnalyzer.parse_python_module(py_file)

        assert isinstance(module, ast.Module)
        assert len(module.body) == 2

    def test_raises_on_nonexistent_file(self, tmp_path):
        missing = tmp_path / "missing.py"
        with pytest.raises(FileNotFoundError):
            StaticAnalyzer.parse_python_module(missing)

    def test_raises_on_invalid_syntax(self, tmp_path):
        py_file = tmp_path / "bad.py"
        py_file.write_text("def broken(:\n")

        with pytest.raises(SyntaxError):
            StaticAnalyzer.parse_python_module(py_file)


class TestFindClassDefinitions:
    """Tests for StaticAnalyzer.find_class_definitions."""

    def test_finds_top_level_classes(self, tmp_path):
        py_file = tmp_path / "models.py"
        py_file.write_text(
            "class User:\n    pass\n\nclass Order:\n    pass\n"
        )
        module = StaticAnalyzer.parse_python_module(py_file)

        classes = StaticAnalyzer.find_class_definitions(module)

        assert len(classes) == 2
        names = {c.name for c in classes}
        assert names == {"User", "Order"}

    def test_finds_nested_classes(self, tmp_path):
        py_file = tmp_path / "nested.py"
        py_file.write_text(
            "class Outer:\n    class Inner:\n        pass\n"
        )
        module = StaticAnalyzer.parse_python_module(py_file)

        classes = StaticAnalyzer.find_class_definitions(module)

        assert len(classes) == 2
        names = {c.name for c in classes}
        assert names == {"Outer", "Inner"}

    def test_returns_empty_for_no_classes(self, tmp_path):
        py_file = tmp_path / "funcs.py"
        py_file.write_text("def foo():\n    pass\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        classes = StaticAnalyzer.find_class_definitions(module)

        assert classes == []


class TestFindFunctionDefinitions:
    """Tests for StaticAnalyzer.find_function_definitions."""

    def test_finds_sync_functions(self, tmp_path):
        py_file = tmp_path / "funcs.py"
        py_file.write_text("def foo():\n    pass\n\ndef bar():\n    pass\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        funcs = StaticAnalyzer.find_function_definitions(module)

        assert len(funcs) == 2
        names = {f.name for f in funcs}
        assert names == {"foo", "bar"}

    def test_finds_async_functions(self, tmp_path):
        py_file = tmp_path / "async_funcs.py"
        py_file.write_text("async def fetch():\n    pass\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        funcs = StaticAnalyzer.find_function_definitions(module)

        assert len(funcs) == 1
        assert funcs[0].name == "fetch"

    def test_finds_methods_inside_classes(self, tmp_path):
        py_file = tmp_path / "cls.py"
        py_file.write_text(
            "class MyClass:\n"
            "    def method_a(self):\n"
            "        pass\n"
            "    async def method_b(self):\n"
            "        pass\n"
        )
        module = StaticAnalyzer.parse_python_module(py_file)

        funcs = StaticAnalyzer.find_function_definitions(module)

        assert len(funcs) == 2
        names = {f.name for f in funcs}
        assert names == {"method_a", "method_b"}

    def test_returns_empty_for_no_functions(self, tmp_path):
        py_file = tmp_path / "empty.py"
        py_file.write_text("x = 1\ny = 2\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        funcs = StaticAnalyzer.find_function_definitions(module)

        assert funcs == []


class TestGrepPattern:
    """Tests for StaticAnalyzer.grep_pattern."""

    def test_finds_pattern_in_files(self, tmp_path):
        (tmp_path / "a.py").write_text("import os\npassword = 'secret'\n")
        (tmp_path / "b.py").write_text("x = 1\n")

        results = StaticAnalyzer.grep_pattern(tmp_path, r"password", [".py"])

        assert len(results) == 1
        path, line_num, content = results[0]
        assert path == tmp_path / "a.py"
        assert line_num == 2
        assert content == "password = 'secret'"

    def test_searches_multiple_extensions(self, tmp_path):
        (tmp_path / "code.py").write_text("# TODO: fix\n")
        (tmp_path / "code.ts").write_text("// TODO: fix\n")
        (tmp_path / "notes.txt").write_text("TODO: fix\n")

        results = StaticAnalyzer.grep_pattern(tmp_path, r"TODO", [".py", ".ts"])

        assert len(results) == 2

    def test_searches_recursively(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.py").write_text("SECRET_KEY = 'abc'\n")

        results = StaticAnalyzer.grep_pattern(tmp_path, r"SECRET_KEY", [".py"])

        assert len(results) == 1
        assert results[0][0] == sub / "deep.py"

    def test_returns_empty_for_no_matches(self, tmp_path):
        (tmp_path / "clean.py").write_text("x = 1\n")

        results = StaticAnalyzer.grep_pattern(tmp_path, r"password", [".py"])

        assert results == []

    def test_returns_empty_for_nonexistent_directory(self, tmp_path):
        nonexistent = tmp_path / "nope"

        results = StaticAnalyzer.grep_pattern(nonexistent, r".", [".py"])

        assert results == []

    def test_strips_line_content(self, tmp_path):
        (tmp_path / "indented.py").write_text("    x = SECRET\n")

        results = StaticAnalyzer.grep_pattern(tmp_path, r"SECRET", [".py"])

        assert results[0][2] == "x = SECRET"

    def test_regex_pattern_matching(self, tmp_path):
        (tmp_path / "urls.py").write_text(
            "url = 'http://localhost:8000'\n"
            "api = 'https://api.example.com'\n"
        )

        results = StaticAnalyzer.grep_pattern(
            tmp_path, r"https?://(?!localhost)", [".py"]
        )

        assert len(results) == 1
        assert "example.com" in results[0][2]


class TestCheckImports:
    """Tests for StaticAnalyzer.check_imports."""

    def test_detects_import_from_target(self, tmp_path):
        py_file = tmp_path / "router.py"
        py_file.write_text("from app.services.user_service import UserService\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        assert StaticAnalyzer.check_imports(module, "services") is True

    def test_returns_false_when_no_match(self, tmp_path):
        py_file = tmp_path / "router.py"
        py_file.write_text("from app.models import User\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        assert StaticAnalyzer.check_imports(module, "services") is False

    def test_detects_partial_module_match(self, tmp_path):
        py_file = tmp_path / "service.py"
        py_file.write_text("from app.repositories.user_repo import UserRepo\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        assert StaticAnalyzer.check_imports(module, "repositories") is True

    def test_ignores_regular_import_statements(self, tmp_path):
        py_file = tmp_path / "module.py"
        py_file.write_text("import os\nimport services\n")
        module = StaticAnalyzer.parse_python_module(py_file)

        # Only checks ImportFrom, not Import
        assert StaticAnalyzer.check_imports(module, "services") is False

    def test_handles_empty_module(self, tmp_path):
        py_file = tmp_path / "empty.py"
        py_file.write_text("")
        module = StaticAnalyzer.parse_python_module(py_file)

        assert StaticAnalyzer.check_imports(module, "anything") is False
