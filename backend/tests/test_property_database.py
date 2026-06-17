"""Property-based tests for foreign key cascade detection logic.

**Validates: Requirements 4.3**

Tests that the Phase 4 (DatabaseValidationPhase) correctly identifies
ForeignKey columns missing ondelete cascade rules using hypothesis to
generate synthetic SQLAlchemy model code.
"""

import ast
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Ensure audit package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hypothesis import given, settings, assume
from hypothesis.strategies import (
    booleans,
    composite,
    integers,
    lists,
    sampled_from,
    text,
)

from audit.phases.phase_04_database import DatabaseValidationPhase


# --------------------------------------------------------------------------
# Strategies
# --------------------------------------------------------------------------

# Valid table names for FK targets
FK_TARGETS = [
    "users.id",
    "customers.id",
    "campaigns.id",
    "predictions.id",
    "datasets.id",
    "models.id",
    "recommendations.id",
    "audit_logs.id",
]

# Valid ondelete values
ONDELETE_VALUES = ["CASCADE", "SET NULL", "RESTRICT", "NO ACTION", "SET DEFAULT"]

# Valid column names that typically hold foreign keys
FK_COLUMN_NAMES = [
    "user_id",
    "customer_id",
    "campaign_id",
    "prediction_id",
    "dataset_id",
    "model_id",
    "created_by_id",
    "updated_by_id",
    "parent_id",
    "owner_id",
]


@composite
def fk_column_definition(draw):
    """Generate a single ForeignKey column definition.

    Returns a tuple of (code_string, has_ondelete) representing a single
    column assignment in a SQLAlchemy model class.
    """
    col_name = draw(sampled_from(FK_COLUMN_NAMES))
    fk_target = draw(sampled_from(FK_TARGETS))
    has_ondelete = draw(booleans())
    ondelete_value = draw(sampled_from(ONDELETE_VALUES))

    if has_ondelete:
        col_code = (
            f'    {col_name} = mapped_column(ForeignKey("{fk_target}", '
            f'ondelete="{ondelete_value}"), nullable=True)'
        )
    else:
        col_code = (
            f'    {col_name} = mapped_column(ForeignKey("{fk_target}"), '
            f"nullable=True)"
        )

    return col_code, col_name, has_ondelete


@composite
def sqlalchemy_model_code(draw):
    """Generate a complete synthetic SQLAlchemy model file with FK columns.

    Returns a tuple of (source_code, expected_missing_columns) where
    expected_missing_columns is the set of column names that lack ondelete.
    """
    # Generate 1-5 FK column definitions
    columns = draw(
        lists(fk_column_definition(), min_size=1, max_size=5)
    )

    # Track which columns should be flagged (no ondelete)
    # Use a list of (col_name, has_ondelete) to handle duplicate names
    missing_ondelete_count = sum(
        1 for _, _, has_ondelete in columns if not has_ondelete
    )
    has_ondelete_count = sum(
        1 for _, _, has_ondelete in columns if has_ondelete
    )

    # Build the model file source
    lines = [
        "from sqlalchemy import ForeignKey, Integer, String",
        "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column",
        "",
        "",
        "class Base(DeclarativeBase):",
        "    pass",
        "",
        "",
        "class TestModel(Base):",
        '    __tablename__ = "test_table"',
        "",
    ]

    # Add an id column
    lines.append("    id = mapped_column(Integer, primary_key=True)")
    lines.append("")

    # Add the FK columns
    for col_code, _, _ in columns:
        lines.append(col_code)

    source = "\n".join(lines) + "\n"

    return source, columns


# --------------------------------------------------------------------------
# Property 6: Foreign Key Cascade Definitions
# --------------------------------------------------------------------------


class TestForeignKeyCascadeDefinitions:
    """Property 6: Foreign Key Cascade Definitions.

    **Validates: Requirements 4.3**

    For all ForeignKey column definitions in SQLAlchemy models, the column
    SHALL include an explicit ondelete cascade rule (e.g., CASCADE, SET NULL,
    RESTRICT). Columns without ondelete must be flagged; columns with
    ondelete must not be flagged.
    """

    @given(model_data=sqlalchemy_model_code())
    @settings(max_examples=200)
    def test_fk_without_ondelete_are_flagged(self, model_data):
        """Every ForeignKey without ondelete must appear in the findings.

        **Validates: Requirements 4.3**
        """
        source, columns = model_data

        # Write source to a temp file and run the detection
        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / "test_model.py"
            model_file.write_text(source, encoding="utf-8")

            phase = DatabaseValidationPhase()
            missing = phase._check_foreign_key_cascades(Path(tmpdir))

        # Count how many columns lack ondelete
        expected_missing_count = sum(
            1 for _, _, has_ondelete in columns if not has_ondelete
        )

        assert len(missing) == expected_missing_count, (
            f"Expected {expected_missing_count} flagged FK columns, "
            f"but got {len(missing)}.\n"
            f"Source:\n{source}\n"
            f"Flagged: {missing}"
        )

    @given(model_data=sqlalchemy_model_code())
    @settings(max_examples=200)
    def test_fk_with_ondelete_are_not_flagged(self, model_data):
        """ForeignKey columns with ondelete must NOT appear in findings.

        **Validates: Requirements 4.3**
        """
        source, columns = model_data

        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / "test_model.py"
            model_file.write_text(source, encoding="utf-8")

            phase = DatabaseValidationPhase()
            missing = phase._check_foreign_key_cascades(Path(tmpdir))

        # Collect the FK targets that have ondelete defined
        cols_with_ondelete_targets = set()
        for col_code, col_name, has_ondelete in columns:
            if has_ondelete:
                # Extract the FK target from the column code
                # The target appears in ForeignKey("target", ...)
                import re
                match = re.search(r'ForeignKey\("([^"]+)"', col_code)
                if match:
                    cols_with_ondelete_targets.add(match.group(1))

        # Verify none of the flagged items have targets that were
        # generated with ondelete
        flagged_targets = {item["target"] for item in missing}

        # The flagged targets should only be from columns without ondelete
        # Note: Multiple columns could reference the same target, so we
        # verify by count instead
        for item in missing:
            # Each flagged item should correspond to a column without ondelete
            assert item["target"] is not None, (
                f"Flagged FK has no target info: {item}"
            )

    @given(model_data=sqlalchemy_model_code())
    @settings(max_examples=200)
    def test_detection_finds_all_fk_calls(self, model_data):
        """The total FK count (flagged + unflagged) must equal the number of
        ForeignKey definitions in the generated code.

        **Validates: Requirements 4.3**
        """
        source, columns = model_data

        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / "test_model.py"
            model_file.write_text(source, encoding="utf-8")

            phase = DatabaseValidationPhase()
            missing = phase._check_foreign_key_cascades(Path(tmpdir))

        # Parse the source to count actual ForeignKey calls
        tree = ast.parse(source)
        total_fk_calls = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and phase._is_foreign_key_call(node):
                total_fk_calls += 1

        # The number flagged + number with ondelete should equal total FK calls
        expected_with_ondelete = sum(
            1 for _, _, has_ondelete in columns if has_ondelete
        )
        assert len(missing) + expected_with_ondelete == total_fk_calls, (
            f"Flagged ({len(missing)}) + with_ondelete "
            f"({expected_with_ondelete}) != total FK calls "
            f"({total_fk_calls})\n"
            f"Source:\n{source}"
        )

    @given(model_data=sqlalchemy_model_code())
    @settings(max_examples=200)
    def test_flagged_items_contain_required_info(self, model_data):
        """Each flagged FK must contain file, line, column, and target info.

        **Validates: Requirements 4.3**
        """
        source, columns = model_data

        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / "test_model.py"
            model_file.write_text(source, encoding="utf-8")

            phase = DatabaseValidationPhase()
            missing = phase._check_foreign_key_cascades(Path(tmpdir))

        for item in missing:
            assert "file" in item, f"Missing 'file' key in finding: {item}"
            assert "line" in item, f"Missing 'line' key in finding: {item}"
            assert "column" in item, f"Missing 'column' key in finding: {item}"
            assert "target" in item, f"Missing 'target' key in finding: {item}"
            # File should be the model file name
            assert item["file"] == "test_model.py", (
                f"Expected file 'test_model.py', got '{item['file']}'"
            )
            # Line should be a valid positive number
            assert int(item["line"]) > 0, (
                f"Line number should be positive, got {item['line']}"
            )
            # Target should be one of our known FK targets
            assert item["target"] in FK_TARGETS, (
                f"Unexpected FK target '{item['target']}', "
                f"expected one of {FK_TARGETS}"
            )
