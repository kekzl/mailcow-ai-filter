"""FilterAction value object for Sieve filter actions."""

from dataclasses import dataclass
from enum import Enum
from typing import Self


class ActionType(Enum):
    """Types of actions that can be performed on emails."""

    FILEINTO = "fileinto"  # Move to folder
    REDIRECT = "redirect"  # Forward to address
    DISCARD = "discard"  # Delete email
    KEEP = "keep"  # Keep in inbox
    STOP = "stop"  # Stop processing rules
    SETFLAG = "setflag"  # Set IMAP flag
    ADDFLAG = "addflag"  # Add IMAP flag


@dataclass(frozen=True, slots=True)
class FilterAction:
    """Immutable filter action to perform on matched emails.

    Represents a single action in a Sieve filter rule.
    Examples:
        - File into "Work" folder
        - Mark as read
        - Stop processing further rules
    """

    action_type: ActionType
    parameter: str | None = None

    def __post_init__(self) -> None:
        """Validate action on construction."""
        if self.action_type in (ActionType.FILEINTO, ActionType.REDIRECT):
            if not self.parameter:
                raise ValueError(f"{self.action_type.value} requires a parameter")

    @classmethod
    def fileinto(cls, folder: str) -> Self:
        """Factory method to create fileinto action."""
        return cls(action_type=ActionType.FILEINTO, parameter=folder)

    @classmethod
    def stop(cls) -> Self:
        """Factory method to create stop action."""
        return cls(action_type=ActionType.STOP)

    @classmethod
    def mark_as_read(cls) -> Self:
        """Factory method to mark email as read."""
        return cls(action_type=ActionType.SETFLAG, parameter="\\Seen")

    @classmethod
    def keep(cls) -> Self:
        """Factory method to keep email in inbox."""
        return cls(action_type=ActionType.KEEP)

    def to_sieve(self) -> str:
        """Convert action to Sieve script syntax."""
        if self.action_type == ActionType.FILEINTO:
            return f'fileinto "{self.parameter}";'
        elif self.action_type == ActionType.SETFLAG:
            return f'setflag "{self.parameter}";'
        elif self.action_type == ActionType.STOP:
            return "stop;"
        elif self.action_type == ActionType.KEEP:
            return "keep;"
        elif self.action_type == ActionType.DISCARD:
            return "discard;"
        elif self.action_type == ActionType.REDIRECT:
            return f'redirect "{self.parameter}";'
        else:
            return f"# Unsupported action: {self.action_type}"

    def __str__(self) -> str:
        if self.parameter:
            return f"{self.action_type.value}({self.parameter})"
        return self.action_type.value
