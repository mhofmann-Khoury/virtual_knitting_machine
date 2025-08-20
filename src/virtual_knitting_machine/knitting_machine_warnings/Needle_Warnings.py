"""A module containing warnings related to needle operations and states on knitting machines.
This module provides warning classes for various needle-related issues including loop capacity violations, transfer operations on empty needles, and knitting operations on needles without loops."""
from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    Knitting_Machine_Warning,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle



class Needle_Warning(Knitting_Machine_Warning):
    """Base class for warnings related to specific needle operations and states.
    This class provides a foundation for all needle-specific warnings and includes the needle reference for detailed error reporting and debugging."""

    def __init__(self, needle: Needle, message: str) -> None:
        """Initialize a needle-specific warning.

        Args:
            needle (Needle): The needle involved in the warning condition.
            message (str): The descriptive warning message about the needle state or operation.
        """
        self.needle: Needle = needle
        super().__init__(message)


class Needle_Holds_Too_Many_Loops(Needle_Warning):
    """A warning for needles that have reached their maximum loop holding capacity.
    This warning occurs when attempting to add loops to a needle that is already at or near its maximum capacity as defined by the machine specification."""

    def __init__(self, needle: Needle, max_loop_allowance: int) -> None:
        """Initialize a needle capacity exceeded warning.

        Args:
            needle (Needle): The needle that has exceeded its loop holding capacity.
            max_loop_allowance (int): The maximum number of loops the needle is allowed to hold.
        """
        self.max_loop_allowance: int = max_loop_allowance
        super().__init__(needle, f"{needle} has reached maximum hold with loops {needle.held_loops} >= {max_loop_allowance}")


class Transfer_From_Empty_Needle(Needle_Warning):
    """A warning for transfer operations attempted on needles that do not hold any loops.
    This warning indicates that a transfer operation was requested from an empty needle, which may not produce the expected knitting results."""

    def __init__(self, needle: Needle) -> None:
        """Initialize a transfer from empty needle warning.

        Args:
            needle (Needle): The empty needle from which a transfer was attempted.
        """
        super().__init__(needle, f"Transferring from empty needle {needle}")


class Knit_on_Empty_Needle_Warning(Needle_Warning):
    """A warning for knitting operations attempted on needles that do not hold any loops.
    This warning indicates that a knitting operation was requested on an empty needle, which may produce unexpected results or indicate a programming error in the knitting sequence."""

    def __init__(self, needle: Needle) -> None:
        """Initialize a knit on empty needle warning.

        Args:
            needle (Needle): The empty needle on which a knit operation was attempted.
        """
        super().__init__(needle, f"Knitting on empty needle {needle}")
