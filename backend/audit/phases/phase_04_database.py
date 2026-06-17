"""Phase 4: Database Validation.

Validates database schema, migrations, and data access patterns
by inspecting ORM models and Alembic migration files.

Checks:
- Table count against 22-table claim
- Migration coverage of all ORM models
- Foreign key cascade definitions
- Unique constraints on email/username columns
- Index definitions on frequently queried columns
- Migration completeness (all 22 tables created)
"""

import ast
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class DatabaseValidationPhase(AuditPhase):
    """Phase 4: Database Validation.

    Inspects ORM model definitions and Alembic migrations to verify
    schema integrity, constraint coverage, and migration completeness.
    """

    name = "Database Validation"
    description = (
        "Validates database schema, migrations, and data access patterns "
        "for integrity and completeness."
    )

    EXPECTED_TABLE_COUNT = 22
    INDEXED_COLUMNS = {"customer_id", "user_id", "created_at"}
    UNIQUE_COLUMNS = {"email", "username"}

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute database validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all database checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 6
        passed_checks = 0

        models_dir = workspace_root / "backend" / "app" / "models"
        migrations_dir = workspace_root / "backend" / "migrations" / "versions"

        # Check 1: Table count
        table_names = self._extract_table_names(models_dir)
        if len(table_names) >= self.EXPECTED_TABLE_COUNT:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-001",
                    title="Table count mismatch",
                    severity=Severity.HIGH,
                    description=(
                        f"Expected {self.EXPECTED_TABLE_COUNT} tables but found "
                        f"{len(table_names)} ORM model definitions. "
                        f"Tables found: {sorted(table_names)}"
                    ),
                    file_path=str(models_dir),
                    recommendation=(
                        "Add missing ORM model definitions to match the "
                        "README claim of 22 tables."
                    ),
                )
            )

        # Check 2: Migration coverage
        migration_tables = self._extract_migration_tables(migrations_dir)
        uncovered = self._check_migration_coverage(
            table_names, migration_tables, migrations_dir
        )
        if not uncovered:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-002",
                    title="Unmigrated ORM models detected",
                    severity=Severity.MEDIUM,
                    description=(
                        f"The following tables defined in ORM models are not "
                        f"covered by explicit op.create_table() calls in "
                        f"migrations: {sorted(uncovered)}. "
                        f"Note: The migration uses metadata.create_all() which "
                        f"covers all models implicitly."
                    ),
                    file_path=str(migrations_dir),
                    recommendation=(
                        "Consider using explicit op.create_table() calls in "
                        "migrations for better visibility and control."
                    ),
                )
            )

        # Check 3: Foreign key cascades
        missing_cascades = self._check_foreign_key_cascades(models_dir)
        if not missing_cascades:
            passed_checks += 1
        else:
            descriptions = []
            for info in missing_cascades:
                descriptions.append(
                    f"  - {info['file']}:{info['line']} column "
                    f"'{info['column']}' FK to '{info['target']}' "
                    f"missing ondelete"
                )
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-003",
                    title="Missing foreign key cascade rules",
                    severity=Severity.MEDIUM,
                    description=(
                        f"Found {len(missing_cascades)} ForeignKey column(s) "
                        f"without explicit ondelete cascade rules:\n"
                        + "\n".join(descriptions)
                    ),
                    recommendation=(
                        "Add explicit ondelete parameter (CASCADE, SET NULL, "
                        "or RESTRICT) to all ForeignKey definitions."
                    ),
                )
            )

        # Check 4: Unique constraints on email/username
        missing_unique = self._check_unique_constraints(models_dir)
        if not missing_unique:
            passed_checks += 1
        else:
            descriptions = []
            for info in missing_unique:
                descriptions.append(
                    f"  - {info['file']}:{info['line']} column "
                    f"'{info['column']}' missing unique=True"
                )
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-004",
                    title="Missing unique constraints on email/username columns",
                    severity=Severity.HIGH,
                    description=(
                        f"Found {len(missing_unique)} column(s) named "
                        f"'email' or 'username' without unique=True:\n"
                        + "\n".join(descriptions)
                    ),
                    recommendation=(
                        "Add unique=True to all email and username columns "
                        "to enforce data integrity at the database level."
                    ),
                )
            )

        # Check 5: Index definitions on frequently queried columns
        missing_indexes = self._check_index_definitions(models_dir)
        if not missing_indexes:
            passed_checks += 1
        else:
            descriptions = []
            for info in missing_indexes:
                descriptions.append(
                    f"  - {info['file']}:{info['line']} column "
                    f"'{info['column']}' missing index=True"
                )
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-005",
                    title="Missing indexes on frequently queried columns",
                    severity=Severity.MEDIUM,
                    description=(
                        f"Found {len(missing_indexes)} column(s) named "
                        f"'customer_id', 'user_id', or 'created_at' without "
                        f"index=True:\n"
                        + "\n".join(descriptions)
                    ),
                    recommendation=(
                        "Add index=True to customer_id, user_id, and "
                        "created_at columns for query performance."
                    ),
                )
            )

        # Check 6: Migration completeness (all 22 tables)
        migration_complete = self._check_migration_completeness(
            table_names, migration_tables, migrations_dir
        )
        if migration_complete:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="DB-006",
                    title="Migration does not explicitly create all 22 tables",
                    severity=Severity.MEDIUM,
                    description=(
                        f"The migration file(s) do not contain explicit "
                        f"op.create_table() calls for all "
                        f"{self.EXPECTED_TABLE_COUNT} tables. "
                        f"Found {len(migration_tables)} explicit table "
                        f"creations. The migration uses metadata.create_all() "
                        f"as a catch-all approach."
                    ),
                    file_path=str(migrations_dir),
                    recommendation=(
                        "Use explicit op.create_table() for each table in "
                        "migrations for better traceability and rollback support."
                    ),
                )
            )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _extract_table_names(self, models_dir: Path) -> set[str]:
        """Extract all __tablename__ values from ORM model files.

        Args:
            models_dir: Path to the models directory.

        Returns:
            Set of table name strings found in ORM models.
        """
        table_names: set[str] = set()

        if not models_dir.exists():
            return table_names

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if (
                            isinstance(item, ast.Assign)
                            and len(item.targets) == 1
                            and isinstance(item.targets[0], ast.Name)
                            and item.targets[0].id == "__tablename__"
                            and isinstance(item.value, ast.Constant)
                            and isinstance(item.value.value, str)
                        ):
                            table_names.add(item.value.value)

        return table_names

    def _extract_migration_tables(self, migrations_dir: Path) -> set[str]:
        """Extract table names from op.create_table() calls in migrations.

        Args:
            migrations_dir: Path to the Alembic versions directory.

        Returns:
            Set of table names referenced in op.create_table() calls.
        """
        tables: set[str] = set()

        if not migrations_dir.exists():
            return tables

        for py_file in migrations_dir.glob("*.py"):
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "create_table"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "op"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    tables.add(node.args[0].value)

        return tables

    def _check_migration_coverage(
        self,
        orm_tables: set[str],
        migration_tables: set[str],
        migrations_dir: Path,
    ) -> set[str]:
        """Check which ORM tables lack explicit migration coverage.

        If the migration uses metadata.create_all(), all tables are
        implicitly covered and this returns an empty set.

        Args:
            orm_tables: Set of table names from ORM models.
            migration_tables: Set of table names from op.create_table() calls.
            migrations_dir: Path to the migrations directory.

        Returns:
            Set of table names not covered by migrations.
        """
        # Check if migration uses metadata.create_all() pattern
        if self._uses_metadata_create_all(migrations_dir):
            return set()

        return orm_tables - migration_tables

    def _uses_metadata_create_all(self, migrations_dir: Path) -> bool:
        """Check if any migration uses Base.metadata.create_all().

        Args:
            migrations_dir: Path to the Alembic versions directory.

        Returns:
            True if metadata.create_all() is used.
        """
        if not migrations_dir.exists():
            return False

        for py_file in migrations_dir.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "create_all" in content:
                return True

        return False

    def _check_foreign_key_cascades(
        self, models_dir: Path
    ) -> list[dict[str, str]]:
        """Check ForeignKey columns for ondelete cascade parameters.

        Args:
            models_dir: Path to the models directory.

        Returns:
            List of dicts with info about ForeignKey columns missing
            ondelete parameters.
        """
        missing: list[dict[str, str]] = []

        if not models_dir.exists():
            return missing

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                # Look for ForeignKey(...) calls
                if not self._is_foreign_key_call(node):
                    continue

                # Extract the FK target (first positional arg)
                fk_target = self._extract_fk_target(node)

                # Check for ondelete keyword
                has_ondelete = any(
                    kw.arg == "ondelete" for kw in node.keywords
                )

                if not has_ondelete:
                    # Try to determine the column name from context
                    col_name = self._get_column_name_from_context(
                        tree, node
                    )
                    missing.append(
                        {
                            "file": py_file.name,
                            "line": str(node.lineno),
                            "column": col_name or "unknown",
                            "target": fk_target or "unknown",
                        }
                    )

        return missing

    def _is_foreign_key_call(self, node: ast.Call) -> bool:
        """Check if an AST Call node is a ForeignKey() invocation.

        Args:
            node: AST Call node to inspect.

        Returns:
            True if the call is to ForeignKey.
        """
        if isinstance(node.func, ast.Name) and node.func.id == "ForeignKey":
            return True
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "ForeignKey"
        ):
            return True
        return False

    def _extract_fk_target(self, node: ast.Call) -> str | None:
        """Extract the target table.column string from a ForeignKey call.

        Args:
            node: AST Call node for ForeignKey().

        Returns:
            The target string (e.g. "users.id") or None.
        """
        if node.args and isinstance(node.args[0], ast.Constant):
            return str(node.args[0].value)
        return None

    def _get_column_name_from_context(
        self, tree: ast.Module, fk_node: ast.Call
    ) -> str | None:
        """Attempt to determine the column name containing this ForeignKey.

        Walks up the AST to find the enclosing assignment target.

        Args:
            tree: The full AST module.
            fk_node: The ForeignKey call node.

        Returns:
            Column name string or None if not determinable.
        """
        fk_line = fk_node.lineno

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    # Check annotated assignments (Mapped[...] = mapped_column(...))
                    if isinstance(item, ast.AnnAssign) and item.target:
                        if (
                            isinstance(item.target, ast.Name)
                            and item.value
                            and hasattr(item.value, "lineno")
                        ):
                            # Check if this assignment spans the FK line
                            if self._node_contains_line(item, fk_line):
                                return item.target.id
                    # Check plain assignments
                    if isinstance(item, ast.Assign):
                        if (
                            item.targets
                            and isinstance(item.targets[0], ast.Name)
                            and self._node_contains_line(item, fk_line)
                        ):
                            return item.targets[0].id

        return None

    def _node_contains_line(self, node: ast.AST, line: int) -> bool:
        """Check if an AST node's line range contains the given line.

        Args:
            node: AST node to check.
            line: Line number to look for.

        Returns:
            True if the node spans the given line.
        """
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return False
        return node.lineno <= line <= (node.end_lineno or node.lineno)

    def _check_unique_constraints(
        self, models_dir: Path
    ) -> list[dict[str, str]]:
        """Check email/username columns for unique=True.

        Args:
            models_dir: Path to the models directory.

        Returns:
            List of dicts with info about columns missing unique=True.
        """
        missing: list[dict[str, str]] = []

        if not models_dir.exists():
            return missing

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                for item in node.body:
                    col_name = self._get_assignment_name(item)
                    if col_name not in self.UNIQUE_COLUMNS:
                        continue

                    # Check if the mapped_column call has unique=True
                    call_node = self._get_mapped_column_call(item)
                    if call_node is None:
                        continue

                    has_unique = self._has_keyword_true(call_node, "unique")
                    if not has_unique:
                        missing.append(
                            {
                                "file": py_file.name,
                                "line": str(
                                    item.lineno if hasattr(item, "lineno") else 0
                                ),
                                "column": col_name,
                            }
                        )

        return missing

    def _check_index_definitions(
        self, models_dir: Path
    ) -> list[dict[str, str]]:
        """Check customer_id/user_id/created_at columns for index=True.

        Args:
            models_dir: Path to the models directory.

        Returns:
            List of dicts with info about columns missing index=True.
        """
        missing: list[dict[str, str]] = []

        if not models_dir.exists():
            return missing

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                tree = StaticAnalyzer.parse_python_module(py_file)
            except (SyntaxError, FileNotFoundError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                for item in node.body:
                    col_name = self._get_assignment_name(item)
                    if col_name not in self.INDEXED_COLUMNS:
                        continue

                    # Check if the mapped_column call has index=True
                    call_node = self._get_mapped_column_call(item)
                    if call_node is None:
                        continue

                    has_index = self._has_keyword_true(call_node, "index")
                    if not has_index:
                        missing.append(
                            {
                                "file": py_file.name,
                                "line": str(
                                    item.lineno if hasattr(item, "lineno") else 0
                                ),
                                "column": col_name,
                            }
                        )

        return missing

    def _get_assignment_name(self, node: ast.AST) -> str | None:
        """Get the variable name from an assignment node.

        Args:
            node: AST node (AnnAssign or Assign).

        Returns:
            Variable name string or None.
        """
        if isinstance(node, ast.AnnAssign) and isinstance(
            node.target, ast.Name
        ):
            return node.target.id
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
        ):
            return node.targets[0].id
        return None

    def _get_mapped_column_call(self, node: ast.AST) -> ast.Call | None:
        """Extract the mapped_column() call from an assignment.

        Args:
            node: AST assignment node.

        Returns:
            The mapped_column Call node, or None if not found.
        """
        value = None
        if isinstance(node, ast.AnnAssign):
            value = node.value
        elif isinstance(node, ast.Assign):
            value = node.value

        if value is None:
            return None

        # Direct mapped_column(...) call
        if isinstance(value, ast.Call):
            if self._is_mapped_column_call(value):
                return value

        return None

    def _is_mapped_column_call(self, node: ast.Call) -> bool:
        """Check if a Call node is mapped_column() or Column().

        Args:
            node: AST Call node.

        Returns:
            True if the call is to mapped_column or Column.
        """
        if isinstance(node.func, ast.Name):
            return node.func.id in ("mapped_column", "Column")
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ("mapped_column", "Column")
        return False

    def _has_keyword_true(self, call_node: ast.Call, keyword: str) -> bool:
        """Check if a function call has a keyword argument set to True.

        Args:
            call_node: AST Call node to inspect.
            keyword: Keyword argument name to look for.

        Returns:
            True if the keyword is present and set to True.
        """
        for kw in call_node.keywords:
            if kw.arg == keyword:
                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    return True
                # Also handle ast.NameConstant for older Python versions
                if isinstance(kw.value, ast.Name) and kw.value.id == "True":
                    return True
        return False

    def _check_migration_completeness(
        self,
        orm_tables: set[str],
        migration_tables: set[str],
        migrations_dir: Path,
    ) -> bool:
        """Check if migrations create all expected tables.

        If the migration uses metadata.create_all(), it implicitly
        creates all tables and is considered complete.

        Args:
            orm_tables: Set of table names from ORM models.
            migration_tables: Set of table names from op.create_table() calls.
            migrations_dir: Path to migrations directory.

        Returns:
            True if all tables are covered by migrations.
        """
        # If using metadata.create_all(), all tables are created
        if self._uses_metadata_create_all(migrations_dir):
            return True

        # Otherwise check explicit op.create_table() calls
        return len(migration_tables) >= self.EXPECTED_TABLE_COUNT
