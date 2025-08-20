"""Module containing the Machine_Knit_Loop class for representing loops created during machine knitting operations.

This module extends the base Loop class to capture machine-specific information including
needle history, transfer operations, and machine state tracking for loops created by virtual knitting machines.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from knit_graphs.Loop import Loop
from knit_graphs.Yarn import Yarn

from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import (
    Slider_Loop_Exception,
    Xfer_Dropped_Loop_Exception,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Machine_Knit_Loop(Loop):
    """An extension of the base Loop structure to capture information about the machine knitting process that created it.

    This class tracks the complete needle history of a loop including creation, transfers, and drop operations,
    providing detailed machine state information for each loop throughout its lifecycle on the knitting machine.

    Attributes:
        needle_history (list[Needle | None]): The list of needles in the order that they held loops. The last element will be None if the loop is dropped from a needle.
    """

    def __init__(self, loop_id: int, yarn: Yarn, source_needle: Needle) -> None:
        """Initialize a machine knit loop with yarn and source needle information.

        Args:
            loop_id (int): Unique identifier for this loop.
            yarn (Yarn): The yarn this loop is part of.
            source_needle (Needle): The needle this loop was created on.

        Raises:
            Slider_Loop_Exception: If attempting to create a loop on a slider needle.
        """
        super().__init__(loop_id, yarn)
        self.needle_history: list[Needle | None] = [source_needle]
        if self.source_needle.is_slider:
            raise Slider_Loop_Exception(self.holding_needle)

    @property
    def holding_needle(self) -> Needle | None:
        """Get the needle currently holding this loop or None if not on a needle.

        Returns:
            Needle | None: The needle currently holding this loop or None if not on a needle.
        """
        return self.needle_history[-1]

    @property
    def last_needle(self) -> Needle:
        """Get the last needle that held this loop before it was dropped.

        Returns:
            Needle: The last needle that held this loop before it was dropped.

        Raises:
            AssertionError: If no needle history exists (should never happen for machine knit loops).
        """
        for n in reversed(self.needle_history):
            if n is not None:
                return n
        assert False, f"Machine knit loops must have at least a source needle."

    @property
    def on_needle(self) -> bool:
        """Check if loop is currently on a holding needle.

        Returns:
            bool: True if loop is currently on a holding needle, False otherwise.
        """
        return self.holding_needle is not None

    @property
    def dropped(self) -> bool:
        """Check if loop is not on a holding needle (has been dropped).

        Returns:
            bool: True if loop is not on a holding needle, False otherwise.
        """
        return not self.on_needle

    @property
    def source_needle(self) -> Needle:
        """Get the needle this loop was created on.

        Returns:
            Needle: The needle this loop was created on.
        """
        return self.needle_history[0]

    def transfer_loop(self, target_needle: Needle) -> None:
        """Add target needle to the end of needle history for loop transfer operation.

        Args:
            target_needle (Needle): The needle the loop is transferred to.

        Raises:
            Xfer_Dropped_Loop_Exception: If attempting to transfer a dropped loop.
        """
        if self.dropped:
            raise Xfer_Dropped_Loop_Exception(target_needle)
        self.needle_history.append(target_needle)

    def drop(self) -> None:
        """Mark the loop as dropped by adding None to end of needle history."""
        self.needle_history.append(None)

    def reverse_drop(self) -> None:
        """Removes dropped status from this loop. Used for transferring needles without recording a dropped action."""
        if self.dropped:
            self.needle_history.pop(-1)
