"""FilterMatcher domain service - tests filters against emails."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..entities.email import Email
from ..entities.sieve_filter import SieveFilter
from ..value_objects.filter_action import FilterAction
from ..value_objects.filter_rule import FilterRule


@dataclass
class MatchResult:
    """Result of matching an email against a filter rule."""

    email: Email
    rule: FilterRule
    matched: bool
    actions: list[FilterAction]


@dataclass
class FilterTestResult:
    """Complete test result for a filter against email collection."""

    filter: SieveFilter
    total_emails: int
    matched_emails: int
    match_rate: float
    matches_by_rule: dict[str, int]
    match_results: list[MatchResult]


class FilterMatcher:
    """Domain service for testing filters against emails.

    Provides functionality to:
    - Test if emails match filter rules
    - Simulate filter application
    - Generate test reports
    """

    def test_filter(self, sieve_filter: SieveFilter, emails: Sequence[Email]) -> FilterTestResult:
        """Test a complete filter against email collection.

        Args:
            sieve_filter: The filter to test
            emails: Collection of emails to test against

        Returns:
            Complete test result with statistics
        """
        if not emails:
            return FilterTestResult(
                filter=sieve_filter,
                total_emails=0,
                matched_emails=0,
                match_rate=0.0,
                matches_by_rule={},
                match_results=[],
            )

        match_results = []
        matches_by_rule: dict[str, int] = {rule.name: 0 for rule in sieve_filter.rules}

        for email in emails:
            for rule in sieve_filter.rules:
                if not rule.enabled:
                    continue

                matched = self._test_rule_against_email(rule, email)

                if matched:
                    matches_by_rule[rule.name] += 1
                    match_results.append(
                        MatchResult(
                            email=email,
                            rule=rule,
                            matched=True,
                            actions=rule.actions,
                        )
                    )
                    # Stop processing if rule has stop action
                    if any(action.action_type == "stop" for action in rule.actions):
                        break

        matched_emails = len(match_results)
        match_rate = matched_emails / len(emails) if emails else 0.0

        return FilterTestResult(
            filter=sieve_filter,
            total_emails=len(emails),
            matched_emails=matched_emails,
            match_rate=match_rate,
            matches_by_rule=matches_by_rule,
            match_results=match_results,
        )

    def _test_rule_against_email(self, rule: FilterRule, email: Email) -> bool:
        """Test if a single rule matches an email.

        Args:
            rule: Filter rule to test
            email: Email to test against

        Returns:
            True if email matches rule conditions
        """
        if not rule.conditions:
            return False

        # Check all conditions based on match_all setting
        if rule.match_all:
            # ALL conditions must match (AND logic)
            return all(self._test_condition(cond, email) for cond in rule.conditions)
        else:
            # ANY condition can match (OR logic)
            return any(self._test_condition(cond, email) for cond in rule.conditions)

    def _test_condition(self, condition, email: Email) -> bool:
        """Test if a single condition matches an email.

        Args:
            condition: Filter condition to test
            email: Email to test against

        Returns:
            True if condition matches
        """
        # Import here to avoid circular dependency
        from ..value_objects.filter_condition import MatchType

        field_value = self._get_email_field_value(email, condition.field)

        if field_value is None:
            return False

        # Handle different match types
        if condition.match_type == MatchType.IS:
            return field_value.lower() == condition.value.lower()

        elif condition.match_type == MatchType.CONTAINS:
            return condition.value.lower() in field_value.lower()

        elif condition.match_type == MatchType.MATCHES:
            # Simple wildcard matching (* and ?)
            import re

            pattern = condition.value.replace("*", ".*").replace("?", ".")
            return bool(re.match(pattern, field_value, re.IGNORECASE))

        return False

    def _get_email_field_value(self, email: Email, field: str) -> str | None:
        """Extract field value from email.

        Args:
            email: Email entity
            field: Field name (from, to, subject, etc.)

        Returns:
            Field value or None if field doesn't exist
        """
        field_lower = field.lower()

        if field_lower == "from":
            return email.sender.value
        elif field_lower == "subject":
            return email.subject
        elif field_lower == "to":
            # For simplicity, just return empty string
            # In full implementation, would need to store recipients
            return ""
        elif field_lower == "body":
            return email.body or ""

        return None

    def find_unmatched_emails(
        self, sieve_filter: SieveFilter, emails: Sequence[Email]
    ) -> list[Email]:
        """Find emails that don't match any filter rules.

        Args:
            sieve_filter: Filter to test
            emails: Email collection

        Returns:
            List of emails that don't match any rule
        """
        unmatched = []

        for email in emails:
            matched_any = False
            for rule in sieve_filter.rules:
                if not rule.enabled:
                    continue

                if self._test_rule_against_email(rule, email):
                    matched_any = True
                    break

            if not matched_any:
                unmatched.append(email)

        return unmatched

    def simulate_actions(self, match_result: MatchResult) -> dict[str, str | bool]:
        """Simulate what would happen when filter actions are applied.

        Args:
            match_result: Result of matching an email

        Returns:
            Dictionary describing simulated actions
        """
        simulated = {
            "original_folder": match_result.email.folder,
            "marked_as_read": False,
            "stopped_processing": False,
            "new_folder": match_result.email.folder,
        }

        for action in match_result.actions:
            if action.action_type == "fileinto":
                simulated["new_folder"] = action.value
            elif action.action_type == "mark_as_read":
                simulated["marked_as_read"] = True
            elif action.action_type == "stop":
                simulated["stopped_processing"] = True

        return simulated

    def generate_test_report(self, test_result: FilterTestResult) -> str:
        """Generate human-readable test report.

        Args:
            test_result: Test result to report on

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("FILTER TEST REPORT")
        lines.append("=" * 60)
        lines.append(f"Filter: {test_result.filter.name}")
        lines.append(f"Total Emails: {test_result.total_emails}")
        lines.append(f"Matched Emails: {test_result.matched_emails}")
        lines.append(f"Match Rate: {test_result.match_rate:.1%}")
        lines.append("")

        lines.append("Matches by Rule:")
        lines.append("-" * 60)
        for rule_name, count in test_result.matches_by_rule.items():
            lines.append(f"  {rule_name}: {count} emails")

        if test_result.match_results:
            lines.append("")
            lines.append("Sample Matches:")
            lines.append("-" * 60)
            for i, match in enumerate(test_result.match_results[:5], 1):
                lines.append(f"  {i}. [{match.rule.name}] {match.email.subject[:50]}")

        lines.append("=" * 60)
        return "\n".join(lines)
