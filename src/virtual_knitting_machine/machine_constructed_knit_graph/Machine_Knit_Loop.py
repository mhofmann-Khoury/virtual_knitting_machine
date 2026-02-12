"""Module containing the Machine_Knit_Loop class for representing loops created during machine knitting operations.

This module extends the base Loop class to capture machine-specific information including
needle history, transfer operations, and machine state tracking for loops created by virtual knitting machines.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import Slider_Loop_Exception

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
    from virtual_knitting_machine.machine_components.needles.Needle import Needle, Needle_Specification
    from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn


class Machine_Knit_Loop(Loop):
    """An extension of the base Loop structure to capture information about the machine knitting process that created it.

    This class tracks the complete needle history of a loop including creation, transfers, and drop operations,
    providing detailed machine state information for each loop throughout its lifecycle on the knitting machine.

    Attributes:
        needle_history (list[Needle | None]): The list of needles in the order that they held loops. The last element will be None if the loop is dropped from a needle.
    """

    _Machine_Loop_Count: int = (
        0  # The number of loops that have been made since the beginning of the machine knitting session.
    )

    def __init__(
        self,
        source_needle: Needle[Self],
        yarn: Machine_Knit_Yarn[Self],
        loop_id: int | None = None,
        **_loop_kwargs: Any,
    ) -> None:
        """Initialize a machine knit loop with yarn and source needle information.

        Args:
            source_needle (Needle): The needle this loop was created on.
            yarn (Machine_Knit_Yarn[Self]): The yarn this loop is part of.
            loop_id (int, optional): A unique identifier for the loop, must be non-negative. Defaults to the next id of the knitgraph that owns the given yarn.

        Raises:
            Slider_Loop_Exception: If attempting to create a loop on a slider needle.
        """
        self._loop_count_on_machine: int = Machine_Knit_Loop._Machine_Loop_Count
        super().__init__(yarn, loop_id)
        Machine_Knit_Loop._Machine_Loop_Count += 1  # next instance will be a later loop.
        self.yarn: Machine_Knit_Yarn[Self] = yarn  # redeclare yarn with correct typing.
        self.needle_history: list[Needle[Self]] = [source_needle]
        self._dropped: bool = False
        if self.source_needle.is_slider:
            raise Slider_Loop_Exception(self.source_needle)

    @property
    def knitting_machine(self) -> Knitting_Machine_State[Self, Any]:
        """
        Returns:
            Knitting_Machine_State[Self, Any]: The knitting machine state that made this loop.
        """
        return self.source_needle.knitting_machine

    @property
    def loop_count_on_machine(self) -> int:
        """
        Returns:
            int: The number of loops that had been created prior to forming this loop. Use this for a time-series comparison of loops across yarns.
        """
        return self._loop_count_on_machine

    @property
    def holding_needle(self) -> Needle[Self] | None:
        """Get the needle currently holding this loop or None if not on a needle.

        Returns:
            Needle | None: The needle currently holding this loop or None if not on a needle.
        """
        if self.dropped:
            return None
        return self.last_needle

    @property
    def last_needle(self) -> Needle[Self]:
        """Get the last needle that held this loop before it was dropped.

        Returns:
            Needle: The last needle that held this loop before it was dropped.
        """
        return self.needle_history[-1]

    @property
    def on_needle(self) -> bool:
        """Check if loop is currently on a holding needle.

        Returns:
            bool: True if loop is currently on a holding needle (i.e., has not been dropped), False otherwise.
        """
        return not self.dropped

    @property
    def dropped(self) -> bool:
        """Check if loop has been dropped from a holding needle.

        Returns:
            bool: True if loop has been dropped from a holding needle, False otherwise.
        """
        return self._dropped

    @property
    def source_needle(self) -> Needle[Self]:
        """Get the needle this loop was created on.

        Returns:
            Needle: The needle this loop was created on.
        """
        return self.needle_history[0]

    @property
    def pull_direction(self) -> Pull_Direction:
        """
        Returns:
            Pull_Direction: The direction that the loop was formed in based on its source needle.
        """
        return Pull_Direction.BtF if self.source_needle.is_front else Pull_Direction.FtB

    @property
    def returns_to_original_needle(self) -> bool:
        """
        Returns:
            bool: True if this loop returns to its source needle. False otherwise.

        Notes:
            This does not imply that the loop never left the source needle.
            The loop may still be held by a needle and moved (changing this property).
            If the loop has been dropped, this property will be frozen in the state of the last needle that held this loop before the drop.
        """
        return self.source_needle == self.last_needle

    @property
    def left_original_needle(self) -> bool:
        """
        Returns:
            bool: True if at any point this loop was held on a needle other than its source needle.
        """
        return len(self.needle_history) > 1 and any(self.source_needle != n for n in self.needle_history[1:])

    def transfer_loop(self, target_needle: Needle_Specification) -> None:
        """Add target needle to the end of needle history for loop transfer operation.

        Args:
            target_needle (Needle): The needle the loop is transferred to.

        """
        target_on_machine = self.knitting_machine[target_needle]
        self.needle_history.append(target_on_machine)  # type: ignore[arg-type]

    def drop(self) -> None:
        """Mark the loop as dropped by adding None to end of needle history."""
        self._dropped = True

    def reverse_drop(self) -> None:
        """Removes dropped status from this loop. Used for transferring needles without recording a dropped action."""
        self._dropped = False

    def __hash__(self) -> int:
        """
        Returns:
            int: A hash value of the tuple of the loop id, the yarn, and the source needle.
        """
        return hash((self.loop_id, self.yarn, self.source_needle))

    def __eq__(self, other: object) -> bool:
        """
        Args:
            other (Machine_Knit_Loop): The machine knit loop to compare to.

        Returns:
            bool: True if these loops have the same id and source carrier needle, False otherwise.
        """
        if isinstance(other, Loop) and not super().__eq__(other):
            return False
        elif isinstance(other, Machine_Knit_Loop):
            return self.yarn.carrier.carrier_id == other.yarn.carrier.carrier_id
        else:
            return False

    def __lt__(self, other: Loop | int) -> bool:
        """Compare loop_id with another loop or integer for ordering.

        Args:
            other (Loop | int): The other loop or integer to compare with.

        Returns:
            bool: True if this loop's id is less than the other's id.
        """
        if isinstance(other, int):
            return self.loop_id < other
        elif isinstance(other, Machine_Knit_Loop) and self.yarn != other.yarn:
            return self.loop_count_on_machine < other.loop_count_on_machine
        else:
            return self.loop_id < other.loop_id
