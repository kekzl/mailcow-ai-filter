#!/usr/bin/env python3
"""Test script to verify the filter generation improvements."""

import sys
sys.path.insert(0, '/home/kekz/git.home.kekz.org/mailcow-ai-filter')

from src.domain.services.filter_generator import FilterGenerator, CategoryPattern
from src.domain.services.filter_validator import FilterValidator
from src.domain.value_objects.filter_condition import FilterCondition

print("=" * 70)
print("TESTING FILTER GENERATION IMPROVEMENTS")
print("=" * 70)
print()

# Test 1: Comma-separated keywords
print("TEST 1: Comma-separated keywords (subject:order,bestellt)")
print("-" * 70)

pattern = "subject:order,bestellt"
print(f"Pattern: {pattern}")
print()

# Using from_pattern_multi (new method)
conditions = FilterCondition.from_pattern_multi(pattern)
print(f"✅ from_pattern_multi() generated {len(conditions)} conditions:")
for i, cond in enumerate(conditions, 1):
    print(f"  {i}. {cond.to_sieve()}")
print()

# Test 2: Domain validation
print("TEST 2: Domain validation")
print("-" * 70)

test_domains = [
    ("github.com", True),
    ("amazon.de", True),
    ("example.com", False),
    ("test.com", False),
    ("unsorted.com", False),
    ("email.com", False),
    ("bank.com", False),
]

for domain, should_be_valid in test_domains:
    is_valid = FilterCondition.is_valid_domain(domain)
    status = "✅" if is_valid == should_be_valid else "❌"
    expected = "VALID" if should_be_valid else "INVALID"
    result = "VALID" if is_valid else "INVALID"
    print(f"{status} {domain:20s} -> {result:8s} (expected: {expected})")
print()

# Test 3: Filter generation with validation
print("TEST 3: Generate filter with comma-separated patterns")
print("-" * 70)

# Create test categories
categories = [
    CategoryPattern(
        name="Amazon-Orders",
        description="Amazon order confirmations",
        patterns=["from:@amazon.de", "subject:order,bestellt,bestellung"],
        suggested_folder="Shopping/Amazon-Orders",
        confidence=0.95,
        example_subjects=["Order confirmed", "Bestellung bestätigt"],
    ),
    CategoryPattern(
        name="Security-Alerts",
        description="Security notifications",
        patterns=["subject:security,alert,warning"],
        suggested_folder="Security/Alerts",
        confidence=0.90,
        example_subjects=["Security alert", "Warning"],
    ),
]

generator = FilterGenerator(min_confidence=0.5)
sieve_filter = generator.generate_filter_from_categories(categories)

print(f"Generated {len(sieve_filter.rules)} rules")
print()

for i, rule in enumerate(sieve_filter.rules, 1):
    print(f"Rule {i}: {rule.name}")
    print(f"  Conditions ({len(rule.conditions)}):")
    for cond in rule.conditions:
        print(f"    - {cond.to_sieve()}")
    print(f"  Logical operator: {rule.logical_operator}")
    print()

# Test 4: Priority ordering
print("TEST 4: Priority ordering (Security should come before Shopping)")
print("-" * 70)

print("Rule execution order:")
for i, rule in enumerate(sieve_filter.rules, 1):
    priority = generator._get_category_priority(
        CategoryPattern(
            name=rule.name,
            description=rule.description,
            patterns=[],
            suggested_folder="",
            confidence=0.5,
            example_subjects=[],
        )
    )
    print(f"  {i}. {rule.name:25s} (priority: {priority})")
print()

# Test 5: Validation
print("TEST 5: Filter validation")
print("-" * 70)

validator = FilterValidator()
issues = validator.validate_filter(sieve_filter)

if issues:
    print(validator.format_issues_report(issues))
else:
    print("✅ No validation issues found!")
print()

# Test 6: Generate Sieve script
print("TEST 6: Generated Sieve script preview")
print("-" * 70)

sieve_script = sieve_filter.to_sieve_script()
lines = sieve_script.split('\n')
print('\n'.join(lines[:40]))  # Show first 40 lines
if len(lines) > 40:
    print(f"\n... ({len(lines) - 40} more lines)")
print()

print("=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
