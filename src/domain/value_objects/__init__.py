"""Value objects - Immutable objects defined by their attributes."""

from .email_address import EmailAddress
from .email_pattern import EmailPattern
from .filter_action import FilterAction
from .filter_condition import FilterCondition
from .filter_rule import FilterRule

__all__ = [
    "EmailAddress",
    "FilterRule",
    "FilterCondition",
    "FilterAction",
    "EmailPattern",
]
