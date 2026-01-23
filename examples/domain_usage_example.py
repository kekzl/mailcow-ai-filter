"""Example: Using the Domain Layer

This example demonstrates how to use the new hexagonal architecture
domain layer to create emails, filters, and generate Sieve scripts.
"""

from datetime import datetime
from src.domain.entities.email import Email
from src.domain.entities.sieve_filter import SieveFilter
from src.domain.value_objects.filter_condition import FilterCondition
from src.domain.value_objects.filter_action import FilterAction
from src.domain.value_objects.filter_rule import FilterRule
from src.domain.value_objects.email_pattern import EmailPattern


def example_create_email():
    """Example: Creating an Email entity."""
    print("=" * 60)
    print("Example 1: Creating an Email Entity")
    print("=" * 60)

    email = Email.create(
        sender="john@example.com",
        recipients=["jane@example.com", "bob@example.com"],
        subject="Important: Q4 Budget Review",
        body="Please review the attached Q4 budget document...",
        folder="INBOX",
        received_at=datetime.now(),
    )

    print(f"Email created: {email}")
    print(f"Sender domain: {email.sender.domain}")
    print(f"Is from example.com: {email.is_from_domain('example.com')}")
    print(
        f"Contains 'budget' in subject: {email.contains_keyword_in_subject('budget')}"
    )
    print()


def example_create_filter_conditions():
    """Example: Creating Filter Conditions."""
    print("=" * 60)
    print("Example 2: Creating Filter Conditions")
    print("=" * 60)

    # Method 1: Factory methods
    cond1 = FilterCondition.header_contains("subject", "invoice")
    cond2 = FilterCondition.address_domain_is("from", "amazon.com")

    # Method 2: From pattern string (like AI generates)
    cond3 = FilterCondition.from_pattern("from:@paypal.com")
    cond4 = FilterCondition.from_pattern("subject:newsletter")

    print(f"Condition 1: {cond1}")
    print(f"  Sieve: {cond1.to_sieve()}")
    print()
    print(f"Condition 2: {cond2}")
    print(f"  Sieve: {cond2.to_sieve()}")
    print()
    print(f"Condition 3: {cond3}")
    print(f"  Sieve: {cond3.to_sieve()}")
    print()
    print(f"Condition 4: {cond4}")
    print(f"  Sieve: {cond4.to_sieve()}")
    print()


def example_create_filter_actions():
    """Example: Creating Filter Actions."""
    print("=" * 60)
    print("Example 3: Creating Filter Actions")
    print("=" * 60)

    action1 = FilterAction.fileinto("Shopping")
    action2 = FilterAction.mark_as_read()
    action3 = FilterAction.stop()

    print(f"Action 1: {action1}")
    print(f"  Sieve: {action1.to_sieve()}")
    print()
    print(f"Action 2: {action2}")
    print(f"  Sieve: {action2.to_sieve()}")
    print()
    print(f"Action 3: {action3}")
    print(f"  Sieve: {action3.to_sieve()}")
    print()


def example_create_complete_filter():
    """Example: Creating a complete Sieve filter."""
    print("=" * 60)
    print("Example 4: Creating a Complete Sieve Filter")
    print("=" * 60)

    # Create conditions for shopping emails
    shopping_conditions = [
        FilterCondition.from_pattern("from:@amazon.de"),
        FilterCondition.from_pattern("from:@ebay.de"),
        FilterCondition.from_pattern("subject:order"),
        FilterCondition.from_pattern("subject:versandt"),
    ]

    # Create actions
    shopping_actions = [FilterAction.fileinto("Shopping"), FilterAction.stop()]

    # Create rule
    shopping_rule = FilterRule.create(
        conditions=shopping_conditions,
        actions=shopping_actions,
        logical_operator="anyof",
        name="Shopping",
        description="Online shopping orders and shipping notifications",
    )

    # Create another rule for work emails
    work_conditions = [
        FilterCondition.address_domain_is("from", "company.com"),
        FilterCondition.header_contains("subject", "meeting"),
    ]

    work_actions = [FilterAction.fileinto("Work"), FilterAction.stop()]

    work_rule = FilterRule.create(
        conditions=work_conditions,
        actions=work_actions,
        logical_operator="anyof",
        name="Work",
        description="Work-related emails",
    )

    # Create Sieve filter with both rules
    sieve_filter = SieveFilter.create(
        name="Email Organization",
        description="Automatically organize incoming emails",
        rules=[shopping_rule, work_rule],
    )

    # Validate
    is_valid, errors = sieve_filter.validate()
    print(f"Filter valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    print()

    # Generate Sieve script
    script = sieve_filter.to_sieve_script()
    print("Generated Sieve Script:")
    print("-" * 60)
    print(script)
    print()


def example_email_pattern_matching():
    """Example: Working with Email Patterns."""
    print("=" * 60)
    print("Example 5: Email Pattern Matching")
    print("=" * 60)

    # Create patterns (as would be detected by AI)
    pattern1 = EmailPattern.from_domain("amazon.com", confidence=0.95, sample_count=25)
    pattern2 = EmailPattern.from_subject_keyword(
        "invoice", confidence=0.88, sample_count=18
    )

    print(f"Pattern 1: {pattern1}")
    print(f"  Filter string: {pattern1.to_filter_string()}")
    print(f"  High confidence: {pattern1.is_high_confidence()}")
    print()

    print(f"Pattern 2: {pattern2}")
    print(f"  Filter string: {pattern2.to_filter_string()}")
    print(f"  High confidence: {pattern2.is_high_confidence()}")
    print()

    # Test email against patterns
    email = Email.create(
        sender="orders@amazon.com",
        recipients=["user@example.com"],
        subject="Your Amazon Order Has Shipped",
        body="Your order #12345 has been shipped",
        folder="INBOX",
    )

    print(f"Email: {email}")
    print(f"Matches pattern 1: {email.matches_pattern(pattern1)}")
    print(f"Matches pattern 2: {email.matches_pattern(pattern2)}")
    print()


def main():
    """Run all examples."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Hexagonal Architecture Examples" + " " * 16 + "║")
    print("║" + " " * 18 + "Domain Layer Usage" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    example_create_email()
    example_create_filter_conditions()
    example_create_filter_actions()
    example_create_complete_filter()
    example_email_pattern_matching()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
