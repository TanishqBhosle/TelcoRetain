"""Phase 8: Recommendation Engine Validation.

Validates the recommendation engine implementation including offer matching
signature, offer type coverage, personalization logic, and low-risk path
handling.

Checks:
- match_offers() signature takes churn_probability and risk_category
- Offer types include "discount", "data_bonus", "plan_upgrade"
- Branching logic uses customer.arpu and risk_category
- Low-risk path produces minimal offers
"""

import ast
import re
from pathlib import Path

from audit.models import AuditFinding, PhaseResult, Severity
from audit.phase import AuditPhase
from audit.utils.static_analyzer import StaticAnalyzer


class RecommendationEngineValidationPhase(AuditPhase):
    """Phase 8: Recommendation Engine Validation.

    Inspects the recommendation engine code to verify that offer generation
    rules reference churn prediction outputs, include required offer types,
    personalize based on customer attributes, and handle low-risk customers
    appropriately.
    """

    name = "Recommendation Engine Validation"
    description = (
        "Validates the recommendation engine for correct input references, "
        "offer type coverage, personalization logic, and low-risk handling."
    )

    # Required parameters for match_offers
    REQUIRED_PARAMS = {"churn_probability", "risk_category"}

    # Required offer types
    REQUIRED_OFFER_TYPES = {"discount", "data_bonus", "plan_upgrade"}

    async def execute(self, workspace_root: Path) -> PhaseResult:
        """Execute recommendation engine validation checks.

        Args:
            workspace_root: Path to the root of the project being audited.

        Returns:
            PhaseResult with findings from all recommendation checks.
        """
        findings: list[AuditFinding] = []
        total_checks = 4
        passed_checks = 0

        ml_dir = workspace_root / "backend" / "ml"
        services_dir = workspace_root / "backend" / "app" / "services"

        # Check 1: match_offers() signature takes churn_probability and risk_category
        signature_ok = self._check_match_offers_signature(ml_dir, services_dir)
        if signature_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="REC-001",
                    title="match_offers() missing churn prediction inputs",
                    severity=Severity.MEDIUM,
                    description=(
                        "Could not verify that the match_offers() function "
                        "signature includes both 'churn_probability' and "
                        "'risk_category' as parameters. The recommendation "
                        "engine must reference churn prediction outputs as "
                        "inputs for offer generation."
                    ),
                    recommendation=(
                        "Ensure match_offers() accepts 'churn_probability' "
                        "(float) and 'risk_category' (str) parameters to "
                        "connect offer generation with churn predictions."
                    ),
                )
            )

        # Check 2: Offer types include "discount", "data_bonus", "plan_upgrade"
        offer_types_ok = self._check_offer_types(ml_dir, services_dir)
        if offer_types_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="REC-002",
                    title="Missing required offer types in recommendation engine",
                    severity=Severity.MEDIUM,
                    description=(
                        "The recommendation engine does not include all "
                        "required offer types. Expected at least: 'discount', "
                        "'data_bonus', and 'plan_upgrade'. The README claims "
                        "support for discounts, data bonuses, and loyalty "
                        "rewards/plan upgrades."
                    ),
                    recommendation=(
                        "Ensure the recommendation engine generates offers "
                        "covering at least three types: 'discount', "
                        "'data_bonus', and 'plan_upgrade'."
                    ),
                )
            )

        # Check 3: Branching logic uses customer.arpu and risk_category
        personalization_ok = self._check_personalization_logic(
            ml_dir, services_dir
        )
        if personalization_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="REC-003",
                    title="Generic-only offer logic without personalization",
                    severity=Severity.HIGH,
                    description=(
                        "The recommendation engine does not branch on "
                        "customer profile attributes (ARPU, risk category) "
                        "to personalize offers. All customers receive the "
                        "same generic offers regardless of their profile."
                    ),
                    recommendation=(
                        "Implement branching logic that uses customer.arpu "
                        "and risk_category to generate different offer sets "
                        "for different customer profiles (e.g., high-value "
                        "customers get plan upgrades, high-risk get discounts)."
                    ),
                )
            )

        # Check 4: Low-risk path produces minimal offers
        low_risk_ok = self._check_low_risk_handling(ml_dir, services_dir)
        if low_risk_ok:
            passed_checks += 1
        else:
            findings.append(
                AuditFinding(
                    phase=self.name,
                    check_id="REC-004",
                    title="Inappropriate high-value offers for low-risk customers",
                    severity=Severity.MEDIUM,
                    description=(
                        "The recommendation engine does not differentiate "
                        "between high-risk and low-risk customers when "
                        "assigning offer impact levels. Low-risk customers "
                        "(low churn probability, non-HIGH risk category) "
                        "should receive minimal or no high-impact offers."
                    ),
                    recommendation=(
                        "Add conditional logic that limits or omits "
                        "high-impact discount offers for customers with "
                        "low churn probability (< 0.7) and non-HIGH "
                        "risk category."
                    ),
                )
            )

        return PhaseResult(
            phase_name=self.name,
            total_checks=total_checks,
            passed_checks=passed_checks,
            findings=findings,
        )

    def _check_match_offers_signature(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify match_offers() takes churn_probability and risk_category.

        AST-parses recommendation engine files to find a function named
        match_offers and checks that its parameter list includes both
        'churn_probability' and 'risk_category'.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if match_offers signature includes both required params.
        """
        search_dirs = [ml_dir, services_dir]

        for directory in search_dirs:
            if not directory.exists():
                continue

            py_files = list(directory.rglob("*.py"))
            for py_file in py_files:
                if not py_file.is_file():
                    continue
                try:
                    tree = StaticAnalyzer.parse_python_module(py_file)
                except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                    continue

                functions = StaticAnalyzer.find_function_definitions(tree)
                for func in functions:
                    if func.name == "match_offers":
                        param_names = {arg.arg for arg in func.args.args}
                        if self.REQUIRED_PARAMS.issubset(param_names):
                            return True

        return False

    def _check_offer_types(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify offer_type values include required types.

        Searches recommendation engine code for string literals matching
        the required offer types: "discount", "data_bonus", "plan_upgrade".

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if all required offer types are found in the codebase.
        """
        search_dirs = [ml_dir, services_dir]
        found_types: set[str] = set()

        for directory in search_dirs:
            if not directory.exists():
                continue

            for offer_type in self.REQUIRED_OFFER_TYPES:
                pattern = rf'["\']({re.escape(offer_type)})["\']'
                matches = StaticAnalyzer.grep_pattern(
                    directory, pattern, [".py"]
                )
                if matches:
                    found_types.add(offer_type)

        return self.REQUIRED_OFFER_TYPES.issubset(found_types)

    def _check_personalization_logic(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify branching logic uses customer.arpu and risk_category.

        Checks that the recommendation engine personalizes offers based
        on customer attributes by looking for conditional branches that
        reference both ARPU and risk_category.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if personalization logic branching on ARPU and
            risk_category is found.
        """
        search_dirs = [ml_dir, services_dir]
        has_arpu_branch = False
        has_risk_branch = False

        for directory in search_dirs:
            if not directory.exists():
                continue

            # Check for ARPU-based branching
            arpu_patterns = [
                r"arpu",
                r"customer\.arpu",
                r"high_value",
            ]
            for pattern in arpu_patterns:
                matches = StaticAnalyzer.grep_pattern(
                    directory, pattern, [".py"]
                )
                for _, _, line in matches:
                    # Look for conditional logic using arpu
                    if any(
                        kw in line
                        for kw in ["if", ">=", "<=", ">", "<", "=="]
                    ):
                        has_arpu_branch = True
                        break
                if has_arpu_branch:
                    break

            # Check for risk_category-based branching
            risk_patterns = [
                r"risk_category",
                r'["\']HIGH["\']',
                r'["\']MEDIUM["\']',
                r'["\']LOW["\']',
            ]
            for pattern in risk_patterns:
                matches = StaticAnalyzer.grep_pattern(
                    directory, pattern, [".py"]
                )
                for _, _, line in matches:
                    if any(
                        kw in line
                        for kw in ["if", "==", "!=", "in"]
                    ):
                        has_risk_branch = True
                        break
                if has_risk_branch:
                    break

        return has_arpu_branch and has_risk_branch

    def _check_low_risk_handling(
        self, ml_dir: Path, services_dir: Path
    ) -> bool:
        """Verify low-risk customers receive minimal offers.

        Checks that the recommendation logic conditionally gates
        high-impact offers behind risk thresholds, ensuring low-risk
        customers (low churn_probability, non-HIGH risk_category) do not
        receive aggressive retention offers.

        Args:
            ml_dir: Path to the ML directory.
            services_dir: Path to the services directory.

        Returns:
            True if the code gates high-impact offers behind risk
            conditions.
        """
        search_dirs = [ml_dir, services_dir]
        has_conditional_discount = False
        has_risk_gating = False

        for directory in search_dirs:
            if not directory.exists():
                continue

            py_files = list(directory.rglob("*.py"))
            for py_file in py_files:
                if not py_file.is_file():
                    continue

                # Look for recommendation-related files
                file_name = py_file.name.lower()
                if not any(
                    kw in file_name
                    for kw in ["recommend", "engine", "offer", "retention"]
                ):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                try:
                    tree = StaticAnalyzer.parse_python_module(py_file)
                except (SyntaxError, FileNotFoundError):
                    continue

                # Look for conditional blocks that gate discount/high-impact
                # offers behind risk checks
                for node in ast.walk(tree):
                    if isinstance(node, ast.If):
                        # Check if the condition references risk thresholds
                        condition_source = ast.dump(node.test)
                        body_source = ast.dump(ast.Module(body=node.body, type_ignores=[]))

                        # Check for risk_category == "HIGH" or
                        # churn_probability >= threshold as conditions
                        if any(
                            kw in condition_source
                            for kw in [
                                "risk_category",
                                "churn_probability",
                                "HIGH",
                            ]
                        ):
                            has_risk_gating = True

                        # Check if the gated block contains discount offer
                        if has_risk_gating and any(
                            kw in body_source
                            for kw in ["discount", "HIGH"]
                        ):
                            has_conditional_discount = True

                # Also check via pattern matching for simple cases
                # Pattern: if risk_category == "HIGH" ... discount
                lines = content.splitlines()
                in_risk_block = False
                for line in lines:
                    if re.search(
                        r'if.*(?:risk_category.*==.*"HIGH"|churn_probability.*>=)',
                        line,
                    ):
                        in_risk_block = True
                    elif in_risk_block and "discount" in line:
                        has_conditional_discount = True
                        break
                    elif in_risk_block and re.match(
                        r"^\s*(else|elif|def|class|return)", line
                    ):
                        in_risk_block = False

        return has_conditional_discount and has_risk_gating
