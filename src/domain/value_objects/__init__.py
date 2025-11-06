"""Value objects - Immutable objects defined by their attributes."""

from .email_address import EmailAddress
from .filter_rule import FilterRule
from .filter_condition import FilterCondition
from .filter_action import FilterAction
from .email_pattern import EmailPattern

__all__ = [
    "EmailAddress",
    "FilterRule",
    "FilterCondition",
    "FilterAction",
    "EmailPattern",
]
