"""Example usage of Domain Services.

This demonstrates how to use the domain services to:
1. Detect patterns in email collections
2. Generate filters from AI patterns
3. Test filters against emails
"""

from datetime import datetime, UTC

from src.domain.entities.email import Email
from src.domain.services.filter_generator import CategoryPattern, FilterGenerator
from src.domain.services.filter_matcher import FilterMatcher
from src.domain.services.pattern_detector import PatternDetector
from src.domain.value_objects.email_address import EmailAddress


def example_pattern_detection():
    """Example: Detecting patterns in email collections."""
    print("=" * 60)
    print("PATTERN DETECTION EXAMPLE")
    print("=" * 60)

    # Create sample email collection
    emails = [
        Email.create(
            sender=EmailAddress("noreply@amazon.com"),
            subject="Your order has been shipped",
            body="Your Amazon order #123 has shipped",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("orders@amazon.com"),
            subject="Order confirmation",
            body="Thank you for your Amazon order",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("newsletter@github.com"),
            subject="GitHub Newsletter - Weekly Digest",
            body="Here's your weekly GitHub digest",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("notifications@github.com"),
            subject="New pull request opened",
            body="A new PR has been opened on your repository",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("support@stripe.com"),
            subject="Payment received",
            body="You received a payment of $100",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
    ]

    # Detect patterns
    detector = PatternDetector(min_frequency=2, min_confidence=0.3)
    patterns = detector.detect_patterns(emails)

    print(f"\nDetected {len(patterns)} patterns:\n")
    for pattern in patterns:
        print(f"Pattern Type: {pattern.pattern_type}")
        print(f"Value: {pattern.value}")
        print(f"Frequency: {pattern.frequency}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Examples: {pattern.example_subjects[:2]}")
        print("-" * 60)

    # Analyze folder distribution
    print("\nFolder Distribution:")
    distribution = detector.analyze_email_distribution(emails)
    for folder, count in distribution.items():
        print(f"  {folder}: {count} emails")

    return patterns, emails


def example_filter_generation():
    """Example: Generating Sieve filters from AI patterns."""
    print("\n" + "=" * 60)
    print("FILTER GENERATION EXAMPLE")
    print("=" * 60)

    # Simulate AI response with category patterns
    ai_response = {
        "categories": [
            {
                "name": "Shopping",
                "description": "Online shopping orders and notifications",
                "patterns": ["from:@amazon.com", "subject:order", "subject:shipped"],
                "suggested_folder": "Shopping",
                "confidence": 0.9,
                "example_subjects": ["Your order has shipped", "Order confirmation"],
            },
            {
                "name": "Development",
                "description": "Development-related notifications",
                "patterns": ["from:@github.com", "subject:pull request"],
                "suggested_folder": "Development",
                "confidence": 0.85,
                "example_subjects": ["New pull request opened", "GitHub Newsletter"],
            },
            {
                "name": "Finance",
                "description": "Financial transactions and notifications",
                "patterns": ["from:@stripe.com", "from:@paypal.com", "subject:payment"],
                "suggested_folder": "Finance",
                "confidence": 0.8,
                "example_subjects": ["Payment received", "Invoice ready"],
            },
        ]
    }

    # Generate filter from AI response
    generator = FilterGenerator(min_confidence=0.7)
    sieve_filter = generator.generate_filter_from_raw_response(ai_response)

    print(f"\nGenerated filter: {sieve_filter.name}")
    print(f"Description: {sieve_filter.description}")
    print(f"Rules: {len(sieve_filter.rules)}\n")

    # Display each rule
    for i, rule in enumerate(sieve_filter.rules, 1):
        print(f"\n{i}. Rule: {rule.name}")
        print(f"   Description: {rule.description}")
        print(f"   Conditions: {len(rule.conditions)}")
        for cond in rule.conditions:
            print(f"     - {cond.to_sieve()}")
        print(f"   Actions: {len(rule.actions)}")
        for action in rule.actions:
            print(f"     - {action.to_sieve()}")

    # Generate complete Sieve script
    print("\n" + "=" * 60)
    print("GENERATED SIEVE SCRIPT")
    print("=" * 60)
    print(sieve_filter.to_sieve_script())

    return sieve_filter


def example_filter_testing(sieve_filter, emails):
    """Example: Testing filters against email collection."""
    print("\n" + "=" * 60)
    print("FILTER TESTING EXAMPLE")
    print("=" * 60)

    # Test filter against emails
    matcher = FilterMatcher()
    test_result = matcher.test_filter(sieve_filter, emails)

    # Display results
    print(f"\nTotal emails tested: {test_result.total_emails}")
    print(f"Matched emails: {test_result.matched_emails}")
    print(f"Match rate: {test_result.match_rate:.1%}\n")

    print("Matches by rule:")
    for rule_name, count in test_result.matches_by_rule.items():
        print(f"  {rule_name}: {count} emails")

    # Find unmatched emails
    print("\nUnmatched emails:")
    unmatched = matcher.find_unmatched_emails(sieve_filter, emails)
    for email in unmatched:
        print(f"  - {email.subject} (from {email.sender.value})")

    # Simulate actions for matched emails
    if test_result.match_results:
        print("\nSimulated actions for first match:")
        first_match = test_result.match_results[0]
        simulated = matcher.simulate_actions(first_match)
        print(f"  Email: {first_match.email.subject}")
        print(f"  Original folder: {simulated['original_folder']}")
        print(f"  New folder: {simulated['new_folder']}")
        print(f"  Mark as read: {simulated['marked_as_read']}")
        print(f"  Stop processing: {simulated['stopped_processing']}")

    # Generate test report
    print("\n" + matcher.generate_test_report(test_result))


def example_direct_pattern_usage():
    """Example: Creating filters from detected patterns directly."""
    print("\n" + "=" * 60)
    print("DIRECT PATTERN TO FILTER EXAMPLE")
    print("=" * 60)

    # Create sample emails
    emails = [
        Email.create(
            sender=EmailAddress("news@newsletter.com"),
            subject="Weekly Newsletter",
            body="Your weekly newsletter",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("updates@newsletter.com"),
            subject="Newsletter Updates",
            body="New newsletter content",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
        Email.create(
            sender=EmailAddress("daily@newsletter.com"),
            subject="Daily Newsletter",
            body="Daily newsletter digest",
            received_date=datetime.now(UTC),
            folder="INBOX",
        ),
    ]

    # Detect patterns
    detector = PatternDetector(min_frequency=2, min_confidence=0.3)
    patterns = detector.detect_patterns(emails)

    print(f"\nDetected {len(patterns)} patterns\n")

    # Convert detected patterns to CategoryPattern objects
    category_patterns = []
    for pattern in patterns[:3]:  # Take top 3
        suggested_folder = detector.suggest_folder_for_pattern(
            detector.group_emails_by_pattern(emails, pattern), pattern
        )

        # Convert detected pattern to category pattern
        if pattern.pattern_type == "sender_domain":
            pattern_str = f"from:@{pattern.value}"
        elif pattern.pattern_type == "subject_keyword":
            pattern_str = f"subject:{pattern.value}"
        else:
            pattern_str = f"from:{pattern.value}"

        category_patterns.append(
            CategoryPattern(
                name=suggested_folder,
                description=f"Emails matching {pattern.pattern_type}: {pattern.value}",
                patterns=[pattern_str],
                suggested_folder=suggested_folder,
                confidence=pattern.confidence,
                example_subjects=pattern.example_subjects,
            )
        )

        print(f"Category: {suggested_folder}")
        print(f"Pattern: {pattern_str}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print("-" * 60)

    # Generate filter from detected patterns
    generator = FilterGenerator(min_confidence=0.3)
    sieve_filter = generator.generate_filter_from_categories(category_patterns)

    print(f"\nGenerated {len(sieve_filter.rules)} rules from detected patterns")
    print("\nSieve Script Preview:")
    print(sieve_filter.to_sieve_script()[:500] + "...")


if __name__ == "__main__":
    # Run all examples
    print("Domain Services Usage Examples")
    print("=" * 60)

    # 1. Pattern Detection
    patterns, emails = example_pattern_detection()

    # 2. Filter Generation
    sieve_filter = example_filter_generation()

    # 3. Filter Testing
    example_filter_testing(sieve_filter, emails)

    # 4. Direct Pattern Usage
    example_direct_pattern_usage()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
