"""A module containing the Needle class and related functions for virtual knitting machine operations.

This module provides the core Needle class which represents individual needles on a knitting machine.
Needles can be on the front or back bed and can hold loops for knitting operations. The module includes
functionality for loop management, needle positioning, and various knitting operations.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, Protocol, Self, TypeGuard, TypeVar, cast, runtime_checkable

from knit_graphs.Pull_Direction import Pull_Direction

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Xfer_Dropped_Loop_Warning

#
from virtual_knitting_machine.machine_components.needles.slotted_position_protocol import Slotted_Position
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


@runtime_checkable
class Needle_Specification(Protocol):
    """Protocol for the positional details of a Needle object."""

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this needle is on the front bed.
        """
        ...

    @property
    def position(self) -> int:
        """
        Returns:
            int: The index on the machine bed of the needle.
        """
        ...

    def opposite(self) -> Self:
        """
        Returns:
            Needle_Specification: The needle on the opposite bed at the same position.
        """
        ...

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if the needle is on the back bed. False, otherwise.
        """
        return not self.is_front

    @property
    def is_slider(self) -> bool:
        """
        Returns:
            bool: True if the needle is a slider, False otherwise.
        """
        return False

    @property
    def pull_direction(self) -> Pull_Direction:
        """Get the direction this needle pulls loops during knit operations.

        Returns:
            Pull_Direction:
                BtF (Back to Front) for front needles, FtB (Front to Back) for back needles.
        """
        if self.is_front:
            return Pull_Direction.BtF
        else:
            return Pull_Direction.FtB

    def slot_by_racking(self, racking: int) -> int:
        """
        The slot number indicates the front-bed alignment of the given needle.
        For front bed needles this is equivalent to the position.
        For back bed needles this is dependent on the racking alignment of the beds.

        Args:
            racking (int): The racking alignment to determine the slot number from.

        Returns:
            int: The slot number of the given component for the given racking.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.position if self.is_front else self.position + racking

    def offset(self, offset: int) -> Self:
        """Get a needle offset by the specified amount on the same bed.

        Args:
            offset (int): The amount to offset the needle position.

        Returns:
            Needle: The needle offset spaces away on the same bed.
        """
        ...

    def __str__(self) -> str:
        """Return string representation of the needle.

        Returns:
            str: String representation (e.g., 'f5' for front needle at position 5, 'bs2' for back slider at position 2).
        """
        s = "s" if self.is_slider else ""
        if self.is_front:
            return f"f{s}{self.position}"
        else:
            return f"b{s}{self.position}"

    def __repr__(self) -> str:
        """Return string representation of the needle.

        Returns:
            str: String representation of the needle.
        """
        return str(self)

    def __hash__(self) -> int:
        """Return hash value for the needle.

        Returns:
            int: Hash value based on position, bed side, and slider state.
        """
        return hash((self.is_front, self.position, self.is_slider))

    def __lt__(self, other: Needle_Specification | Slotted_Position | int | float) -> bool:
        """Compare if this needle is less than another needle or number.

        Args:
            other (Needle | int | float): The other needle or number to compare with.

        Returns:
            bool:
                True if this needle's position is less than the other value.
                If the needles are at the same location but in opposite positions (back vs. front),
                the front needle is considered less than the back.
                This orders needles as front-to-back in a leftward carriage pass.
        """
        if int(self) < int(other):  # ints, needle_specifications, slotted positions, floats
            return True
        elif isinstance(other, float):  # rare case of float that floored to same value.
            return self.position < other
        return (
            isinstance(other, Needle_Specification) and self.is_front and not other.is_front
        )  # Equal position needles are ordered front then back in a leftward direction.

    def __eq__(self, other: object) -> bool:
        """Check equality with another needle.

        Args:
            other (Needle): The other needle to compare with.

        Returns:
            bool: True if needles are equal (same bed, position, and slider status).
        """
        return (
            isinstance(other, Needle_Specification)
            and self.__class__ == other.__class__
            and self.is_front == other.is_front
            and self.is_slider == other.is_slider
            and self.position == other.position
        )

    def __int__(self) -> int:
        """
        Returns:
            int: The needle position.
        """
        return self.position

    def __add__(self, other: Needle_Specification | int) -> Self:
        """Add another needle's position or an integer to this needle's position.

        Args:
            other (Needle_Specification | int): The needle or integer to add.

        Returns:
            Needle: New needle with the sum position on the same bed.
        """
        offset = other if isinstance(other, int) else other.position
        return self.offset(offset)

    def __radd__(self, other: int) -> Self:
        """Right-hand add operation.

        Args:
            other (int): The integer to add.

        Returns:
            Needle: New needle with the sum position on the same bed.
        """
        return self.offset(other)

    def __sub__(self, other: Needle_Specification | int) -> Self:
        """Subtract another needle's position or an integer from this needle's position.

        Args:
            other (Needle | int): The needle or integer to subtract.

        Returns:
            Needle: New needle with the difference position on the same bed.
        """
        offset = other if isinstance(other, int) else other.position
        return self.offset(-1 * offset)


class Needle_Position(Needle_Specification):
    def __init__(self, is_front: bool, position: int, is_slider: bool) -> None:
        self._is_slider: bool = is_slider
        self._position: int = position
        self._is_front: bool = is_front

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this needle is on the front bed.
        """
        return self._is_front

    @property
    def position(self) -> int:
        """
        Returns:
            int: The index on the machine bed of the needle.
        """
        return self._position

    @property
    def is_slider(self) -> bool:
        """
        Returns:
            bool: True if the needle is a slider, False otherwise.
        """
        return self._is_slider

    def opposite(self) -> Self:
        """
        Returns:
            Needle_Specification: The needle on the opposite bed at the same position.
        """
        return self.__class__(not self.is_front, self.position, self.is_slider)

    def offset(self, offset: int) -> Self:
        """Get a needle offset by the specified amount on the same bed.

        Args:
            offset (int): The amount to offset the needle position.

        Returns:
            Needle: The needle offset spaces away on the same bed.
        """
        return self.__class__(self.is_front, self.position + offset, not self.is_slider)


class Needle(Needle_Specification, Slotted_Position[Machine_LoopT]):
    """A class for managing individual needles on a knitting machine.

    This class represents a needle on either the front or back bed of a knitting machine.
    Each needle can hold multiple loops and provides methods for knitting operations,
    loop transfers, and position calculations.

    Attributes:
        held_loops (list[Machine_Knit_Loop]): List of loops currently held by this needle.
    """

    def __init__(
        self,
        is_front: bool,
        position: int,
        knitting_machine: Knitting_Machine_State[Machine_LoopT, Any],
    ) -> None:
        """Initialize a new needle.

        Args:
            is_front (bool): True if this is a front bed needle, False for back bed.
            position (int): The needle index/position on the machine bed.
            knitting_machine (Knitting_Machine_State): The machine that owns this needle.
        """
        self._gauge: int = 0
        self._is_front: bool = is_front
        self._position: int = int(position)
        self.held_loops: list[Machine_LoopT] = []
        self._knitting_machine: Knitting_Machine_State[Machine_LoopT, Any] = knitting_machine

    @property
    def gauged_layers(self) -> int:
        """
        Returns:
            int: The gauge (number of layers) currently knitting in.
        """
        return self.knitting_machine.gauged_layers

    @property
    def sheet(self) -> int:
        """
        Returns:
            int: The position of the sheet in the gauge.
        """
        return self._position % self.gauged_layers

    @property
    def position_in_sheet(self) -> int:
        """
        Returns:
            int: The position of this needle in the sheet in the current gauged-schema.
        """
        return self._position // self.gauged_layers

    @property
    def knitting_machine(self) -> Knitting_Machine_State[Machine_LoopT, Any]:
        return self._knitting_machine

    @property
    def gauge_neighbors(self) -> list[Self]:
        """
        Returns:
            list[Sheet_Needle]: List of needles that neighbor this loop in sheets at the current gauge layering.
        """
        neighbors = []
        for i in range(self.sheet - 1, -1, -1):
            neighbors.append(self + i)
        for i in range(self.sheet + 1, self.gauged_layers):
            neighbors.append(self + i)
        return neighbors

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this needle is on the front bed.
        """
        return self._is_front

    @property
    def position(self) -> int:
        """
        Returns:
            int: The index on the machine bed of the needle.
        """
        return self._position

    @property
    def slot_number(self) -> int:
        """
        The slot number indicates the front-bed alignment of the given needle.
        For front bed needles this is equivalent to the position.
        For back bed needles this is dependent on the racking alignment of the beds.

        Returns:
            int: The slot number of the given component for the given racking.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.position if self.is_front else self.position + self.machine_racking

    @property
    def has_loops(self) -> bool:
        """Check if the needle is currently holding any loops.

        Returns:
            bool: True if needle is holding loops, False otherwise.
        """
        return len(self.held_loops) > 0

    def opposite(self) -> Self:
        """
        Returns:
            Needle: The needle on the opposite bed at the same position.
        """
        return cast(Self, self.knitting_machine.get_specified_needle(not self.is_front, self.position, self.is_slider))

    def offset(self, offset: int) -> Self:
        """Get a needle offset by the specified amount on the same bed.

        Args:
            offset (int): The amount to offset the needle position.

        Returns:
            Needle: The needle offset spaces away on the same bed.
        """
        return cast(
            Self, self.knitting_machine.get_specified_needle(self.is_front, self.position + offset, self.is_slider)
        )

    def main_needle(self) -> Needle[Machine_LoopT]:
        """Get the non-slider needle at this needle position.

        Returns:
            Needle: The non-slider needle at this needle position.
        """
        if not self.is_slider:
            return self
        else:
            return self.knitting_machine.get_specified_needle(self.is_front, self.position, is_slider=False)

    def active_floats(self) -> dict[Machine_LoopT, Machine_LoopT]:
        """Get active floats connecting to loops on this needle.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]:
                Dictionary of loops that are active keyed to active yarn-wise neighbors.
                Each key-value pair represents a directed float where key comes before value on the yarns in the system.
        """
        active_floats = {}
        for loop in self.held_loops:
            next_loop = loop.next_loop_on_yarn
            if next_loop is not None and next_loop.on_needle:
                active_floats[loop] = next_loop
            prior_loop = loop.prior_loop_on_yarn
            if prior_loop is not None and prior_loop.on_needle:
                active_floats[prior_loop] = loop
        return active_floats

    def float_overlaps_needle(self, u: Machine_LoopT, v: Machine_LoopT) -> bool:
        """Check if a float between two loops overlaps this needle's position.

        Args:
            u (Machine_Knit_Loop): Machine_Knit_Loop at start of float.
            v (Machine_Knit_Loop): Machine_Knit_Loop at end of float.

        Returns:
            bool: True if the float between u and v overlaps the position of this needle.
        """
        if u.holding_needle is None or v.holding_needle is None:
            return False
        left_position = min(u.holding_needle.position, v.holding_needle.position)
        right_position = max(u.holding_needle.position, v.holding_needle.position)
        return bool(left_position <= self.position <= right_position)

    def add_loop(self, loop: Machine_LoopT) -> None:
        """Add a loop to the set of currently held loops.

        Args:
            loop (Machine_Knit_Loop): Loop to add onto needle.
        """
        self.held_loops.append(loop)
        loop.yarn.active_loops[loop] = self

    def add_loops(self, loops: Sequence[Machine_LoopT]) -> None:
        """Add multiple loops to the held set.

        Args:
            loops (Sequence[Machine_Knit_Loop]): List of loops to place onto needle.
        """
        for l in loops:
            self.add_loop(l)

    def transfer_loops(self, target_needle: Needle[Machine_LoopT]) -> list[Machine_LoopT]:
        """Transfer all loops from this needle to a target needle.

        Args:
            target_needle (Needle): Needle to transfer loops to.

        Returns:
            list[Machine_Knit_Loop]: Loops that were transferred.
        """
        xfer_loops = self.held_loops
        for loop in xfer_loops:
            if loop.dropped:
                warnings.warn(
                    Xfer_Dropped_Loop_Warning(target_needle),
                    stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
                )
                continue
            loop.transfer_loop(target_needle)
        self.held_loops = []
        target_needle.add_loops(xfer_loops)
        return xfer_loops

    def drop(self) -> list[Machine_LoopT]:
        """Drop all held loops by releasing them from the needle.

        Returns:
            list[Machine_Knit_Loop]: The loops that were dropped.
        """
        old_loops = self.held_loops
        for loop in old_loops:
            del loop.yarn.active_loops[loop]
            loop.drop()
        self.held_loops = []
        return old_loops

    @staticmethod
    def needle_position_from_sheet_and_gauge(sheet_pos: int, sheet: int, gauge: int) -> int:
        """
        Args:
            sheet_pos (int): The position in the sheet.
            sheet (int): The sheet being used.
            gauge (int): The number of sheets supported by the gauge.

        Returns:
            int: The position of the needle on the bed based on the given information about its position in a sheet.
        """
        return sheet + sheet_pos * gauge

    @staticmethod
    def iterates_over_needles(needles: Iterable[Needle_Specification]) -> TypeGuard[Needle]:
        """
        Args:
            needles (Iterable[Needle_Specification]): The needles to iterate over and determine that they are all Needles.

        Returns:
            bool, TypeGuard[Needle]: Returns true if all elements in needles are needle objects. Typing system will recognize this guarantee.
        """
        return all(isinstance(n, Needle) for n in needles)

    def __rsub__(self, other: int) -> Self:
        """Right-hand subtract operation.

        Args:
            other (int): The integer to subtract from.

        Returns:
            Needle: New needle with the difference position on the same bed.
        """
        return cast(
            Self, self.knitting_machine.get_specified_needle(self.is_front, other - self.position, self.is_slider)
        )
