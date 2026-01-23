"""FilterGenerator domain service - converts AI patterns to Sieve filters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..entities.sieve_filter import SieveFilter
from ..value_objects.filter_action import FilterAction
from ..value_objects.filter_condition import FilterCondition
from ..value_objects.filter_rule import FilterRule


@dataclass
class CategoryPattern:
    """Raw category pattern from AI analysis.

    Supports hierarchical categories with optional subcategories.
    Top-level categories may have empty patterns if all rules
    are in subcategories.
    """

    name: str
    description: str
    patterns: list[str]
    suggested_folder: str
    confidence: float
    example_subjects: list[str]
    subcategories: list[CategoryPattern] | None = None


class FilterGenerator:
    """Domain service for generating Sieve filters from AI patterns.

    This service translates AI-detected email patterns into structured
    Sieve filter rules, applying domain knowledge about filter construction
    and validation.
    """

    def __init__(self, min_confidence: float = 0.5) -> None:
        """Initialize the filter generator.

        Args:
            min_confidence: Minimum confidence threshold for including patterns
        """
        self.min_confidence = min_confidence

    def generate_filter_from_categories(
        self, categories: list[CategoryPattern]
    ) -> SieveFilter:
        """Generate a complete Sieve filter from AI-detected categories.

        Args:
            categories: List of category patterns from AI analysis

        Returns:
            SieveFilter entity with all rules

        Raises:
            ValueError: If no valid categories are provided
        """
        if not categories:
            raise ValueError("No categories provided for filter generation")

        # Filter by confidence threshold
        valid_categories = [
            cat for cat in categories if cat.confidence >= self.min_confidence
        ]

        if not valid_categories:
            raise ValueError(
                f"No categories meet minimum confidence threshold of {self.min_confidence}"
            )

        # Sort categories by priority (security > finance > work > social > promotions)
        sorted_categories = sorted(valid_categories, key=self._get_category_priority)

        rules = []
        for category in sorted_categories:
            # Process category itself if it has patterns
            rule = self._create_rule_from_category(category)
            if rule:
                rules.append(rule)

            # Process subcategories recursively (also sorted by priority)
            if category.subcategories:
                sorted_subcats = sorted(
                    [
                        sc
                        for sc in category.subcategories
                        if sc.confidence >= self.min_confidence
                    ],
                    key=self._get_category_priority,
                )
                for subcat in sorted_subcats:
                    sub_rule = self._create_rule_from_category(subcat)
                    if sub_rule:
                        rules.append(sub_rule)

        if not rules:
            raise ValueError("Failed to generate any valid rules from categories")

        return SieveFilter.create(
            name="AI-Generated Email Filters",
            description=f"Automatically generated filters for {len(rules)} categories",
            rules=rules,
        )

    def _get_category_priority(self, category: CategoryPattern) -> int:
        """Determine priority of a category (lower number = higher priority).

        Priority order:
        1. Security/Alerts (0-9)
        2. Finance/Banking (10-19)
        3. Work/Professional (20-29)
        4. Shopping/Orders (30-39)
        5. Social Media (40-49)
        6. Newsletters/Promotions (50-59)
        7. Others (60+)

        Args:
            category: Category to prioritize

        Returns:
            Priority number (lower = higher priority)
        """
        name_lower = category.name.lower()
        desc_lower = category.description.lower()
        combined = f"{name_lower} {desc_lower}"

        # Security/Alerts - highest priority
        security_keywords = [
            "security",
            "alert",
            "warning",
            "critical",
            "urgent",
            "notification",
        ]
        if any(kw in combined for kw in security_keywords):
            return 0

        # Finance/Banking
        finance_keywords = [
            "finance",
            "bank",
            "payment",
            "invoice",
            "receipt",
            "bill",
            "paypal",
            "stripe",
        ]
        if any(kw in combined for kw in finance_keywords):
            return 10

        # Work/Professional
        work_keywords = [
            "work",
            "github",
            "gitlab",
            "ci/cd",
            "ci-cd",
            "code",
            "deploy",
            "meeting",
            "slack",
        ]
        if any(kw in combined for kw in work_keywords):
            return 20

        # Shopping/Orders
        shopping_keywords = [
            "shop",
            "order",
            "shipping",
            "delivery",
            "amazon",
            "ebay",
            "purchase",
        ]
        if any(kw in combined for kw in shopping_keywords):
            return 30

        # Social Media
        social_keywords = [
            "social",
            "facebook",
            "twitter",
            "linkedin",
            "instagram",
            "message",
        ]
        if any(kw in combined for kw in social_keywords):
            return 40

        # Newsletters/Promotions
        promo_keywords = [
            "newsletter",
            "promotion",
            "marketing",
            "ad",
            "offer",
            "subscribe",
        ]
        if any(kw in combined for kw in promo_keywords):
            return 50

        # Others (lowest priority)
        return 60

    def _create_rule_from_category(
        self, category: CategoryPattern
    ) -> FilterRule | None:
        """Create a single filter rule from a category pattern.

        Args:
            category: Category pattern with patterns and metadata

        Returns:
            FilterRule if valid patterns exist, None otherwise
        """
        if not category.patterns:
            return None

        # Convert pattern strings to FilterCondition objects
        # Use from_pattern_multi() to properly handle comma-separated keywords
        conditions = []
        for pattern in category.patterns:
            try:
                # from_pattern_multi() returns a list (may be single or multiple conditions)
                pattern_conditions = FilterCondition.from_pattern_multi(pattern)
                conditions.extend(pattern_conditions)
            except ValueError:
                # Skip invalid patterns
                continue

        if not conditions:
            return None

        # Create actions: file into folder and stop processing
        actions = [
            FilterAction.fileinto(category.suggested_folder),
            FilterAction.stop(),
        ]

        # Use 'anyof' (OR) logic when multiple conditions are present
        # This ensures "subject:order,bestellt" becomes (order OR bestellt)
        logical_operator = "anyof" if len(conditions) > 1 else "anyof"

        return FilterRule.create(
            name=category.name,
            description=category.description,
            conditions=conditions,
            actions=actions,
            logical_operator=logical_operator,
        )

    def generate_filter_from_raw_response(
        self, ai_response: dict[str, Any]
    ) -> SieveFilter:
        """Generate filter from raw AI JSON response.

        Args:
            ai_response: Raw JSON response from AI containing categories

        Returns:
            SieveFilter entity

        Raises:
            ValueError: If response format is invalid
        """
        if "categories" not in ai_response:
            raise ValueError("AI response missing 'categories' field")

        categories = []
        for cat_dict in ai_response["categories"]:
            try:
                category = self._parse_category(cat_dict)
                if category:
                    categories.append(category)
            except (KeyError, TypeError):
                # Skip malformed categories
                continue

        return self.generate_filter_from_categories(categories)

    def _parse_category(self, cat_dict: dict[str, Any]) -> CategoryPattern | None:
        """Parse a category dictionary (with optional subcategories) recursively.

        Args:
            cat_dict: Dictionary containing category data

        Returns:
            CategoryPattern with subcategories or None if invalid
        """
        # Parse subcategories if present
        subcategories = None
        if "subcategories" in cat_dict and cat_dict["subcategories"]:
            subcategories = []
            for subcat_dict in cat_dict["subcategories"]:
                subcat = self._parse_category(subcat_dict)
                if subcat:
                    subcategories.append(subcat)

        return CategoryPattern(
            name=cat_dict.get("name", "Unknown"),
            description=cat_dict.get("description", ""),
            patterns=cat_dict.get("patterns", []),
            suggested_folder=cat_dict.get(
                "suggested_folder", cat_dict.get("name", "Unknown")
            ),
            confidence=cat_dict.get("confidence", 0.5),
            example_subjects=cat_dict.get("example_subjects", []),
            subcategories=subcategories if subcategories else None,
        )

    def validate_patterns(self, patterns: list[str]) -> list[str]:
        """Validate and filter pattern strings.

        Args:
            patterns: List of pattern strings to validate

        Returns:
            List of valid pattern strings
        """
        valid_patterns = []
        for pattern in patterns:
            try:
                # Try to create a condition to validate the pattern
                FilterCondition.from_pattern(pattern)
                valid_patterns.append(pattern)
            except ValueError:
                # Skip invalid patterns
                continue
        return valid_patterns
