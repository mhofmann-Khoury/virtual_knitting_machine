from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class ViolationAction(Enum):
    """Enumeration of actions taken in response to violations."""

    RAISE = auto()  # Raise the violation exception
    WARN = auto()  # Warn the user about the violation exception but do not raise it.
    IGNORE = auto()  # Take no action regarding the exception.


@dataclass
class ViolationResponse:
    """A response policy for a violation"""

    action: ViolationAction = ViolationAction.RAISE  # The action to take in response to a violation.
    handle: bool = True  # If True, attempts to handle the violation.
    proceed_with_operation: bool = True  # If True, attempts to proceed with the operation that caused the violation.

    def __post_init__(self) -> None:
        if self.action == ViolationAction.RAISE:
            self.proceed_with_operation = False


class Violation(Enum):
    """Enumeration of all violations of the machine state's requirements that can be handled by custom policies"""

    Machine_State_Violation = auto()  # The default violation type for machine state errors.
    YARN_CARRIER_VIOLATION = auto()  # The default violation type for all errors involving yarn carriers.
    INSERTING_HOOK_IN_USE = (
        auto()
    )  # Violation that the yarn-inserting hook cannot be used by another carrier until it has been released.
    HOOKED_CARRIER = auto()  # Violation that a carrier cannot complete an action while on the yarn-inserting hook.
    BlOCKED_BY_HOOK = auto()  # Violation that a needle is blocked by the yarn inserting hook.
    INACTIVE_CARRIER = auto()  # Violation when using an inactive carrier for an operation.
    INHOOK_RIGHTWARDS = auto()  # Violation raised when the yarn inserting hook activates in the wrong direction.
    MAKE_LOOP_ON_SLIDER = auto()
    RACKING_OUT_OF_RANGE = auto()
    # ... one per physical constraint
