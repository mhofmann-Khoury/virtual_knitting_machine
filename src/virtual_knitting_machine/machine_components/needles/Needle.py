"""A module containing the Needle class and related functions for virtual knitting machine operations.

This module provides the core Needle class which represents individual needles on a knitting machine.
Needles can be on the front or back bed and can hold loops for knitting operations. The module includes
functionality for loop management, needle positioning, and various knitting operations.
"""
from __future__ import annotations

from knit_graphs.Pull_Direction import Pull_Direction

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)


class Needle:
    """A class for managing individual needles on a knitting machine.

    This class represents a needle on either the front or back bed of a knitting machine.
    Each needle can hold multiple loops and provides methods for knitting operations,
    loop transfers, and position calculations.

    Attributes:
        held_loops (list[Machine_Knit_Loop]): List of loops currently held by this needle.
    """

    def __init__(self, is_front: bool, position: int) -> None:
        """Initialize a new needle.

        Args:
            is_front (bool): True if this is a front bed needle, False for back bed.
            position (int): The needle index/position on the machine bed.
        """
        self._is_front: bool = is_front
        self._position: int = int(position)
        self.held_loops: list[Machine_Knit_Loop] = []

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

    @property
    def is_front(self) -> bool:
        """Check if needle is on the front bed.

        Returns:
            bool: True if needle is on front bed, False otherwise.
        """
        return self._is_front

    @property
    def position(self) -> int:
        """Get the index position of the needle on the machine bed.

        Returns:
            int: The index on the machine bed of the needle.
        """
        return self._position

    @property
    def has_loops(self) -> bool:
        """Check if the needle is currently holding any loops.

        Returns:
            bool: True if needle is holding loops, False otherwise.
        """
        return len(self.held_loops) > 0

    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """Get active floats connecting to loops on this needle.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]:
                Dictionary of loops that are active keyed to active yarn-wise neighbors.
                Each key-value pair represents a directed float where key comes before value on the yarns in the system.
        """
        active_floats = {}
        for loop in self.held_loops:
            next_loop = loop.next_loop_on_yarn()
            if next_loop is not None and next_loop.on_needle:
                active_floats[loop] = next_loop
            prior_loop = loop.prior_loop_on_yarn()
            if prior_loop is not None and prior_loop.on_needle:
                active_floats[prior_loop] = loop
        return active_floats

    def float_overlaps_needle(self, u: Machine_Knit_Loop, v: Machine_Knit_Loop) -> bool:
        """Check if a float between two loops overlaps this needle's position.

        Args:
            u (Machine_Knit_Loop): Machine_Knit_Loop at start of float.
            v (Machine_Knit_Loop): Machine_Knit_Loop at end of float.

        Returns:
            bool: True if the float between u and v overlaps the position of this needle.
        """
        if not u.on_needle or not v.on_needle:
            return False
        left_position = min(u.holding_needle.position, v.holding_needle.position)
        right_position = max(u.holding_needle.position, v.holding_needle.position)
        return bool(left_position <= self.position <= right_position)

    def add_loop(self, loop: Machine_Knit_Loop) -> None:
        """Add a loop to the set of currently held loops.

        Args:
            loop (Machine_Knit_Loop): Loop to add onto needle.
        """
        self.held_loops.append(loop)
        loop.yarn.active_loops[loop] = self

    def add_loops(self, loops: list[Machine_Knit_Loop]) -> None:
        """Add multiple loops to the held set.

        Args:
            loops (list[Machine_Knit_Loop]): List of loops to place onto needle.
        """
        for l in loops:
            self.add_loop(l)

    def transfer_loops(self, target_needle: Needle) -> list[Machine_Knit_Loop]:
        """Transfer all loops from this needle to a target needle.

        Args:
            target_needle (Needle): Needle to transfer loops to.

        Returns:
            list[Machine_Knit_Loop]: Loops that were transferred.
        """
        xfer_loops = self.held_loops
        for loop in xfer_loops:
            loop.transfer_loop(target_needle)
        self.held_loops = []
        target_needle.add_loops(xfer_loops)
        return xfer_loops

    def drop(self) -> list[Machine_Knit_Loop]:
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

    @property
    def is_back(self) -> bool:
        """Check if needle is on the back bed.

        Returns:
            bool: True if needle is on the back bed, False otherwise.
        """
        return not self.is_front

    def opposite(self) -> Needle:
        """Get the needle on the opposite bed at the same position.

        Returns:
            Needle: The needle on the opposite bed at the same position.
        """
        return self.__class__(is_front=not self.is_front, position=self.position)

    def offset(self, offset: int) -> Needle:
        """Get a needle offset by the specified amount on the same bed.

        Args:
            offset (int): The amount to offset the needle position.

        Returns:
            Needle: The needle offset spaces away on the same bed.
        """
        return self + offset

    def racked_position_on_front(self, rack: int) -> int:
        """Get the position of the needle on the front bed at a given racking.

        Args:
            rack (int): The racking value.

        Returns:
            int:
                The front needle position given a racking (no change for front bed needles).
        """
        if self.is_front:
            return self.position
        else:
            return self.position + rack

    def main_needle(self) -> Needle:
        """Get the non-slider needle at this needle position.

        Returns:
            Needle:
                The non-slider needle at this needle position.
                If this is not a slider needle, this instance is returned.
        """
        if not self.is_slider:
            return self
        return Needle(is_front=self.is_front, position=self.position)

    def __str__(self) -> str:
        """Return string representation of the needle.

        Returns:
            str: String representation (e.g., 'f5' for front needle at position 5).
        """
        if self.is_front:
            return f"f{self.position}"
        else:
            return f"b{self.position}"

    def __repr__(self) -> str:
        """Return string representation of the needle.

        Returns:
            str: String representation of the needle.
        """
        return str(self)

    def __hash__(self) -> int:
        """Return hash value for the needle.

        Returns:
            int: Hash value based on position (negative for back needles).
        """
        if self.is_back:
            return -1 * self.position
        return self.position

    def __lt__(self, other: Needle | int | float) -> bool:
        """Compare if this needle is less than another needle or number.

        Args:
            other (Needle | int | float): The other needle or number to compare with.

        Returns:
            bool:
                True if this needle's position is less than the other value.
                If the needles are at the same location but in opposite positions (back vs. front),
                the front needle is considered less than the back.
                This orders needles as front-to-back in a leftward carriage pass.

        Raises:
            TypeError: If other is not a Needle or number.
        """
        if isinstance(other, Needle) and self.is_front and not other.is_front:
            return True  # Equal position needles are ordered front then back in a leftward direction.
        else:
            try:
                return self.position < int(other)
            except ValueError:
                raise TypeError(f"Expected comparison to Needle or number but got {other}")

    def __int__(self) -> int:
        """Return integer representation of the needle position.

        Returns:
            int: The needle position.
        """
        return self.position

    def __index__(self) -> int:
        """Return index representation of the needle position.

        Returns:
            int: The needle position as an index.
        """
        return int(self)

    def at_racking_comparison(self, other: Needle, rack: int = 0, all_needle_racking: bool = False) -> int:
        """Compare needle positions at a given racking.

        Args:
            other (Needle): The other needle to compare positions with.
            rack (int, optional): Racking value to compare between. Defaults to 0.
            all_needle_racking (bool, optional):
                If true, account for front back alignment in all needle knitting. Defaults to False.

        Returns:
            int: 1 if self > other, 0 if equal, -1 if self < other.

        Note:
            At an all needle racking, the front needle is always < the back needle, regardless of direction.
        """
        self_pos = self.racked_position_on_front(rack)
        other_pos = other.racked_position_on_front(rack)
        if self_pos < other_pos:
            return -1
        elif self_pos > other_pos:
            return 1
        else:  # same position at racking
            if not all_needle_racking or self.is_front == other.is_front:  # same needle
                return 0
            elif self.is_front:  # Self is on the front, implies other is on the back. Front comes before back in all_needle alignment
                return -1
            else:  # implies self is on the back and other is on the front.
                return 1

    @staticmethod
    def needle_at_racking_cmp(n1: Needle, n2: Needle, racking: int = 0, all_needle_racking: bool = False) -> int:
        """Static method to compare two needles at a given racking.

        Args:
            n1 (Needle): First needle in comparison.
            n2 (Needle): Second needle in comparison.
            racking (int, optional): Racking value to compare between. Defaults to 0.
            all_needle_racking (bool, optional):
                If true, account for front back alignment in all needle knitting. Defaults to False.

        Returns:
            int: 1 if n1 > n2, 0 if equal, -1 if n1 < n2.

        Note:
            At an all needle racking, the front needle is always < the back needle, regardless of direction.
        """
        return n1.at_racking_comparison(n2, racking, all_needle_racking)

    def __add__(self, other: Needle | int) -> Needle:
        """Add another needle's position or an integer to this needle's position.

        Args:
            other (Needle | int): The needle or integer to add.

        Returns:
            Needle: New needle with the sum position on the same bed.
        """
        position = other
        if isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, int(self.position + position))

    def __radd__(self, other: Needle | int) -> Needle:
        """Right-hand add operation.

        Args:
            other (Needle | int): The needle or integer to add.

        Returns:
            Needle: New needle with the sum position on the same bed.
        """
        position = other
        if isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, int(self.position + position))

    def __sub__(self, other: Needle | int) -> Needle:
        """Subtract another needle's position or an integer from this needle's position.

        Args:
            other (Needle | int): The needle or integer to subtract.

        Returns:
            Needle: New needle with the difference position on the same bed.
        """
        position = other
        if isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, int(self.position - position))

    def __rsub__(self, other: Needle | int) -> Needle:
        """Right-hand subtract operation.

        Args:
            other (Needle | int): The needle or integer to subtract from.

        Returns:
            Needle: New needle with the difference position on the same bed.
        """
        position = other
        if isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, int(position - self.position))

    def __lshift__(self, other: Needle | int) -> Needle:
        """Left shift operation (equivalent to subtraction).

        Args:
            other (Needle | int): The needle or integer to shift by.

        Returns:
            Needle: New needle shifted left (position decreased).
        """
        return self - other

    def __rshift__(self, other: Needle | int) -> Needle:
        """Right shift operation (equivalent to addition).

        Args:
            other (Needle | int): The needle or integer to shift by.

        Returns:
            Needle: New needle shifted right (position increased).
        """
        return self + other

    def __rlshift__(self, other: Needle | int) -> Needle:
        """Right-hand left shift operation.

        Args:
            other (Needle | int): The needle or integer to shift.

        Returns:
            Needle: New needle with shifted position.
        """
        return other - self

    def __rrshift__(self, other: Needle | int) -> Needle:
        """Right-hand right shift operation.

        Args:
            other (Needle | int): The needle or integer to shift.

        Returns:
            Needle: New needle with shifted position.
        """
        return other + self

    def __eq__(self, other: Needle) -> bool:
        """Check equality with another needle.

        Args:
            other (Needle): The other needle to compare with.

        Returns:
            bool: True if needles are equal (same bed, position, and slider status).
        """
        return self.is_front == other.is_front and self.is_slider == other.is_slider and self.position == other.position

    @property
    def is_slider(self) -> bool:
        """Check if the needle is a slider needle.

        Returns:
            bool: True if the needle is a slider, False otherwise.
        """
        return False
