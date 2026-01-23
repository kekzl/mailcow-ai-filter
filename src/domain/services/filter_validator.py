"""FilterValidator domain service - validates and lints Sieve filter rules."""

from __future__ import annotations

from dataclasses import dataclass

from ..entities.sieve_filter import SieveFilter
from ..value_objects.filter_condition import (
    GENERIC_DOMAINS,
    INVALID_DOMAINS,
)
from ..value_objects.filter_rule import FilterRule


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a filter rule."""

    severity: str  # "error", "warning", "info"
    rule_name: str
    message: str
    suggestion: str | None = None


class FilterValidator:
    """Domain service for validating and linting Sieve filter rules.

    This service analyzes generated filter rules and identifies common
    errors, inefficiencies, and potential improvements.
    """

    def validate_filter(self, sieve_filter: SieveFilter) -> list[ValidationIssue]:
        """Validate a complete Sieve filter and return issues.

        Args:
            sieve_filter: Filter to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Check for empty filter
        if not sieve_filter.rules:
            issues.append(
                ValidationIssue(
                    severity="error",
                    rule_name="Filter",
                    message="Filter has no rules",
                    suggestion="Add at least one filter rule",
                )
            )
            return issues

        # Validate each rule
        for rule in sieve_filter.rules:
            issues.extend(self.validate_rule(rule))

        # Check for overlapping rules
        issues.extend(self._check_rule_overlap(sieve_filter.rules))

        return issues

    def validate_rule(self, rule: FilterRule) -> list[ValidationIssue]:
        """Validate a single filter rule.

        Args:
            rule: Rule to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Check for placeholder domains
        issues.extend(self._check_placeholder_domains(rule))

        # Check for generic domains
        issues.extend(self._check_generic_domains(rule))

        # Check for comma-separated values (old bug)
        issues.extend(self._check_comma_in_values(rule))

        # Check for empty conditions
        if not rule.conditions:
            issues.append(
                ValidationIssue(
                    severity="error",
                    rule_name=rule.name or "Unnamed",
                    message="Rule has no conditions",
                    suggestion="Add at least one condition to match emails",
                )
            )

        # Check for empty actions
        if not rule.actions:
            issues.append(
                ValidationIssue(
                    severity="error",
                    rule_name=rule.name or "Unnamed",
                    message="Rule has no actions",
                    suggestion="Add at least one action (e.g., fileinto)",
                )
            )

        return issues

    def _check_placeholder_domains(self, rule: FilterRule) -> list[ValidationIssue]:
        """Check for placeholder domains in rule conditions.

        Args:
            rule: Rule to check

        Returns:
            List of issues found
        """
        issues = []

        for condition in rule.conditions:
            if condition.condition_type.value == "address_domain":
                domain = condition.value.lower()
                if domain in INVALID_DOMAINS:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            rule_name=rule.name or "Unnamed",
                            message=f"Placeholder domain detected: {domain}",
                            suggestion=f"Replace '{domain}' with a real domain from your emails",
                        )
                    )

        return issues

    def _check_generic_domains(self, rule: FilterRule) -> list[ValidationIssue]:
        """Check for overly generic domains in rule conditions.

        Args:
            rule: Rule to check

        Returns:
            List of issues found
        """
        issues = []

        for condition in rule.conditions:
            if condition.condition_type.value == "address_domain":
                domain = condition.value.lower()
                if domain in GENERIC_DOMAINS:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            rule_name=rule.name or "Unnamed",
                            message=f"Overly generic domain: {domain}",
                            suggestion=f"Domain '{domain}' is too generic and may match unintended emails",
                        )
                    )

        return issues

    def _check_comma_in_values(self, rule: FilterRule) -> list[ValidationIssue]:
        """Check for comma-separated values (indicates old bug).

        Args:
            rule: Rule to check

        Returns:
            List of issues found
        """
        issues = []

        for condition in rule.conditions:
            if "," in condition.value:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        rule_name=rule.name or "Unnamed",
                        message=f"Comma found in condition value: '{condition.value}'",
                        suggestion=(
                            f"Split '{condition.value}' into multiple conditions. "
                            "Use anyof logic to match ANY of the keywords."
                        ),
                    )
                )

        return issues

    def _check_rule_overlap(self, rules: list[FilterRule]) -> list[ValidationIssue]:
        """Check for overlapping rules that might conflict.

        Args:
            rules: List of rules to check

        Returns:
            List of issues found
        """
        issues = []

        # Group rules by target folders
        folder_conditions: dict[str, list[tuple[FilterRule, set[str]]]] = {}

        for rule in rules:
            # Extract target folder from fileinto action
            target_folder = None
            for action in rule.actions:
                if hasattr(action, "folder"):
                    target_folder = action.folder
                    break

            if not target_folder:
                continue

            # Extract domains from conditions
            domains = set()
            for condition in rule.conditions:
                if condition.condition_type.value == "address_domain":
                    domains.add(condition.value.lower())

            if target_folder not in folder_conditions:
                folder_conditions[target_folder] = []
            folder_conditions[target_folder].append((rule, domains))

        # Check for same domain in multiple folders
        domain_to_folders: dict[str, list[str]] = {}
        for folder, rule_domains_list in folder_conditions.items():
            for rule, domains in rule_domains_list:
                for domain in domains:
                    if domain not in domain_to_folders:
                        domain_to_folders[domain] = []
                    if folder not in domain_to_folders[domain]:
                        domain_to_folders[domain].append(folder)

        # Report domains used in multiple folders
        for domain, folders in domain_to_folders.items():
            if len(folders) > 1:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        rule_name="Multiple Rules",
                        message=f"Domain '{domain}' used in multiple folders: {', '.join(folders)}",
                        suggestion="This may cause emails to be sorted into the first matching folder only",
                    )
                )

        return issues

    def format_issues_report(self, issues: list[ValidationIssue]) -> str:
        """Format validation issues into a human-readable report.

        Args:
            issues: List of validation issues

        Returns:
            Formatted report string
        """
        if not issues:
            return "✅ No validation issues found!"

        # Group by severity
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        infos = [i for i in issues if i.severity == "info"]

        report = []
        report.append("=" * 60)
        report.append("SIEVE FILTER VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")

        if errors:
            report.append(f"❌ ERRORS ({len(errors)}):")
            report.append("")
            for i, issue in enumerate(errors, 1):
                report.append(f"{i}. [{issue.rule_name}] {issue.message}")
                if issue.suggestion:
                    report.append(f"   💡 {issue.suggestion}")
                report.append("")

        if warnings:
            report.append(f"⚠️  WARNINGS ({len(warnings)}):")
            report.append("")
            for i, issue in enumerate(warnings, 1):
                report.append(f"{i}. [{issue.rule_name}] {issue.message}")
                if issue.suggestion:
                    report.append(f"   💡 {issue.suggestion}")
                report.append("")

        if infos:
            report.append(f"ℹ️  INFO ({len(infos)}):")
            report.append("")
            for i, issue in enumerate(infos, 1):
                report.append(f"{i}. [{issue.rule_name}] {issue.message}")
                if issue.suggestion:
                    report.append(f"   💡 {issue.suggestion}")
                report.append("")

        report.append("=" * 60)
        report.append(
            f"Total: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info"
        )
        report.append("=" * 60)

        return "\n".join(report)
