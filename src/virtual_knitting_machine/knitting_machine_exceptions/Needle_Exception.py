"""Module containing common machine knitting exceptions that involve needles and needle operations.
This module provides exception classes for various needle-related critical errors including
slider operations, loop transfers, alignment issues, and needle state violations that prevent successful knitting operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Needle_Exception(Knitting_Machine_Exception):
    """Base class for exceptions related to specific needle operations and states.
    This class provides a foundation for all needle-specific exceptions and includes the needle reference for detailed error reporting and debugging of needle-related operational failures.
    """

    def __init__(self, needle: Needle, message: str, violation: Violation = Violation.Machine_State_Violation) -> None:
        """Initialize a needle-specific exception.

        Args:
            needle (Needle): The needle involved in the exception condition.
            message (str): The descriptive error message about the needle state or operation failure.
        """
        self.needle = needle
        super().__init__(message, violation)


class Slider_Loop_Exception(Needle_Exception):
    """Exception for attempting to form loops on slider needles.
    This exception occurs when trying to create a new loop on a slider needle,
    which is not allowed as slider needles can only hold and transfer loops but cannot be used for loop formation operations.
    """

    def __init__(self, needle: Needle) -> None:
        """Initialize a slider loop formation exception.

        Args:
            needle (Needle): The slider needle on which loop formation was attempted.
        """
        super().__init__(needle, f"Slider {needle} cannot form a new loop", violation=Violation.MAKE_LOOP_ON_SLIDER)
