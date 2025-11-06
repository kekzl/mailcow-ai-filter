"""PatternDetector domain service - detects patterns in email collections."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

from ..entities.email import Email
from ..value_objects.email_pattern import EmailPattern


@dataclass
class DetectedPattern:
    """A pattern detected in email analysis."""

    pattern_type: str  # "sender_domain", "subject_keyword", "sender_address"
    value: str
    frequency: int
    email_count: int
    example_subjects: list[str]
    confidence: float


class PatternDetector:
    """Domain service for detecting patterns in email collections.

    Analyzes email collections to identify recurring patterns such as:
    - Common sender domains
    - Frequent subject keywords
    - Specific sender addresses
    """

    def __init__(
        self,
        min_frequency: int = 3,
        min_confidence: float = 0.5,
        max_examples: int = 5,
    ) -> None:
        """Initialize the pattern detector.

        Args:
            min_frequency: Minimum occurrences to consider a pattern
            min_confidence: Minimum confidence score to include pattern
            max_examples: Maximum example subjects to include per pattern
        """
        self.min_frequency = min_frequency
        self.min_confidence = min_confidence
        self.max_examples = max_examples

    def detect_patterns(self, emails: Sequence[Email]) -> list[DetectedPattern]:
        """Detect all patterns in email collection.

        Args:
            emails: Collection of Email entities to analyze

        Returns:
            List of detected patterns sorted by confidence
        """
        if not emails:
            return []

        patterns = []

        # Detect sender domain patterns
        patterns.extend(self._detect_sender_domain_patterns(emails))

        # Detect subject keyword patterns
        patterns.extend(self._detect_subject_keyword_patterns(emails))

        # Detect specific sender patterns
        patterns.extend(self._detect_sender_address_patterns(emails))

        # Filter by confidence and sort
        valid_patterns = [p for p in patterns if p.confidence >= self.min_confidence]
        valid_patterns.sort(key=lambda p: p.confidence, reverse=True)

        return valid_patterns

    def _detect_sender_domain_patterns(
        self, emails: Sequence[Email]
    ) -> list[DetectedPattern]:
        """Detect patterns based on sender domains.

        Args:
            emails: Email collection to analyze

        Returns:
            List of domain-based patterns
        """
        domain_data: dict[str, dict] = defaultdict(
            lambda: {"count": 0, "subjects": []}
        )

        for email in emails:
            domain = email.sender.domain
            domain_data[domain]["count"] += 1
            if len(domain_data[domain]["subjects"]) < self.max_examples:
                domain_data[domain]["subjects"].append(email.subject)

        patterns = []
        total_emails = len(emails)

        for domain, data in domain_data.items():
            count = data["count"]
            if count >= self.min_frequency:
                # Calculate confidence based on frequency
                confidence = min(1.0, count / (total_emails * 0.1))

                patterns.append(
                    DetectedPattern(
                        pattern_type="sender_domain",
                        value=domain,
                        frequency=count,
                        email_count=count,
                        example_subjects=data["subjects"][: self.max_examples],
                        confidence=confidence,
                    )
                )

        return patterns

    def _detect_subject_keyword_patterns(
        self, emails: Sequence[Email]
    ) -> list[DetectedPattern]:
        """Detect patterns based on subject keywords.

        Args:
            emails: Email collection to analyze

        Returns:
            List of keyword-based patterns
        """
        keyword_data: dict[str, dict] = defaultdict(
            lambda: {"count": 0, "subjects": []}
        )

        # Common words to ignore
        stop_words = {
            "re",
            "fwd",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "out",
            "if",
            "about",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
        }

        for email in emails:
            # Extract words from subject (lowercase, alphanumeric only)
            words = [
                word.lower()
                for word in email.subject.split()
                if len(word) >= 3 and word.lower() not in stop_words
            ]

            # Track each unique word
            unique_words = set(words)
            for word in unique_words:
                keyword_data[word]["count"] += 1
                if len(keyword_data[word]["subjects"]) < self.max_examples:
                    keyword_data[word]["subjects"].append(email.subject)

        patterns = []
        total_emails = len(emails)

        for keyword, data in keyword_data.items():
            count = data["count"]
            if count >= self.min_frequency:
                # Calculate confidence based on frequency
                confidence = min(1.0, count / (total_emails * 0.15))

                patterns.append(
                    DetectedPattern(
                        pattern_type="subject_keyword",
                        value=keyword,
                        frequency=count,
                        email_count=count,
                        example_subjects=data["subjects"][: self.max_examples],
                        confidence=confidence,
                    )
                )

        return patterns

    def _detect_sender_address_patterns(
        self, emails: Sequence[Email]
    ) -> list[DetectedPattern]:
        """Detect patterns based on specific sender addresses.

        Args:
            emails: Email collection to analyze

        Returns:
            List of sender address-based patterns
        """
        sender_data: dict[str, dict] = defaultdict(
            lambda: {"count": 0, "subjects": []}
        )

        for email in emails:
            sender = email.sender.value
            sender_data[sender]["count"] += 1
            if len(sender_data[sender]["subjects"]) < self.max_examples:
                sender_data[sender]["subjects"].append(email.subject)

        patterns = []
        total_emails = len(emails)

        for sender, data in sender_data.items():
            count = data["count"]
            # Use higher threshold for specific senders
            if count >= self.min_frequency + 2:
                # Calculate confidence based on frequency
                confidence = min(1.0, count / (total_emails * 0.08))

                patterns.append(
                    DetectedPattern(
                        pattern_type="sender_address",
                        value=sender,
                        frequency=count,
                        email_count=count,
                        example_subjects=data["subjects"][: self.max_examples],
                        confidence=confidence,
                    )
                )

        return patterns

    def group_emails_by_pattern(
        self, emails: Sequence[Email], pattern: DetectedPattern
    ) -> list[Email]:
        """Get all emails matching a specific pattern.

        Args:
            emails: Email collection to filter
            pattern: Pattern to match against

        Returns:
            List of emails matching the pattern
        """
        matching_emails = []

        for email in emails:
            matches = False

            if pattern.pattern_type == "sender_domain":
                matches = email.sender.domain == pattern.value
            elif pattern.pattern_type == "subject_keyword":
                matches = pattern.value.lower() in email.subject.lower()
            elif pattern.pattern_type == "sender_address":
                matches = email.sender.value == pattern.value

            if matches:
                matching_emails.append(email)

        return matching_emails

    def analyze_email_distribution(
        self, emails: Sequence[Email]
    ) -> dict[str, int]:
        """Analyze distribution of emails across folders.

        Args:
            emails: Email collection to analyze

        Returns:
            Dictionary mapping folder names to email counts
        """
        folder_counts: dict[str, int] = Counter(email.folder for email in emails)
        return dict(folder_counts)

    def suggest_folder_for_pattern(
        self, emails: Sequence[Email], pattern: DetectedPattern
    ) -> str:
        """Suggest a folder name based on pattern and email distribution.

        Args:
            emails: Email collection matching the pattern
            pattern: The detected pattern

        Returns:
            Suggested folder name
        """
        if not emails:
            return "Uncategorized"

        # Count existing folders
        folder_distribution = self.analyze_email_distribution(emails)

        # If most emails are already in one folder, suggest that
        if folder_distribution:
            most_common_folder = max(
                folder_distribution.items(), key=lambda x: x[1]
            )[0]

            # Avoid suggesting INBOX or system folders
            if most_common_folder not in ["INBOX", "Trash", "Spam", "Junk", "Sent"]:
                return most_common_folder

        # Generate folder name based on pattern type
        if pattern.pattern_type == "sender_domain":
            # Extract company/service name from domain
            domain_parts = pattern.value.split(".")
            if len(domain_parts) >= 2:
                return domain_parts[-2].capitalize()

        # Default to "Filtered"
        return "Filtered"
