"""Module containing common machine knitting exceptions that involve needles and needle operations.
This module provides exception classes for various needle-related critical errors including
slider operations, loop transfers, alignment issues, and needle state violations that prevent successful knitting operations."""
from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import (
    Knitting_Machine_Exception,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Needle_Exception(Knitting_Machine_Exception):
    """Base class for exceptions related to specific needle operations and states.
    This class provides a foundation for all needle-specific exceptions and includes the needle reference for detailed error reporting and debugging of needle-related operational failures."""

    def __init__(self, needle: Needle, message: str) -> None:
        """Initialize a needle-specific exception.

        Args:
            needle (Needle): The needle involved in the exception condition.
            message (str): The descriptive error message about the needle state or operation failure.
        """
        self.needle = needle
        super().__init__(message)


class Slider_Loop_Exception(Needle_Exception):
    """Exception for attempting to form loops on slider needles.
    This exception occurs when trying to create a new loop on a slider needle,
    which is not allowed as slider needles can only hold and transfer loops but cannot be used for loop formation operations."""

    def __init__(self, needle: Needle) -> None:
        """Initialize a slider loop formation exception.

        Args:
            needle (Needle): The slider needle on which loop formation was attempted.
        """
        super().__init__(needle, f"Slider {needle} cannot form a new loop")


class Clear_Needle_Exception(Needle_Exception):
    """Exception for attempting to use needles when sliders are not clear.
    This exception occurs when trying to perform knitting operations while slider needles still hold loops, which must be cleared before standard knitting operations can proceed."""

    def __init__(self, needle: Needle) -> None:
        """Initialize a clear needle requirement exception.

        Args:
            needle (Needle): The needle that cannot be used due to unclear sliders.
        """
        super().__init__(needle, f"Cannot use {needle} until sliders are clear")


class Xfer_Dropped_Loop_Exception(Needle_Exception):
    """Exception for attempting to transfer dropped loops to target needles.
    This exception occurs when trying to transfer a loop that has already been dropped from the machine, which is not physically possible as the loop is no longer held by any needle."""

    def __init__(self, needle: Needle) -> None:
        """Initialize a transfer dropped loop exception.

        Args:
            needle (Needle): The target needle where transfer of a dropped loop was attempted.
        """
        super().__init__(needle, f"Cannot transfer dropped loop to target needle {needle}")


class Misaligned_Needle_Exception(Needle_Exception):
    """Exception for operations attempted between needles that are not properly aligned at the current racking.
    This exception occurs when trying to perform transfer or other cross-bed operations between needles that are not aligned according to the machine's current racking configuration."""

    def __init__(self, start_needle: Needle, target_needle: Needle) -> None:
        """Initialize a misaligned needle exception.

        Args:
            start_needle (Needle): The starting needle for the attempted operation.
            target_needle (Needle): The target needle that is not aligned with the start needle.
        """
        self.target_needle = target_needle
        super().__init__(start_needle, f"Needles {start_needle} and {target_needle} are not aligned.")

    @property
    def start_needle(self) -> Needle:
        """Get the starting needle for the misaligned operation.

        Returns:
            Needle: Property used to have multiple names for start needle.
        """
        return self.needle
