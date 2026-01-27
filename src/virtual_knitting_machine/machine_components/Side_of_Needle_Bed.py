"""Module containing the Carriage_Side enumeration for knitting machine carriage positioning.

This module defines the two sides of a knitting machine that the carriage can be positioned on
and provides utility methods for determining appropriate movement directions from each side.
"""

from __future__ import annotations

from enum import Enum

from virtual_knitting_machine.machine_components.needles.slotted_position_protocol import Slotted_Position


class Side_of_Needle_Bed(Enum):
    """Enumeration containing the two sides the machine carriage can be positioned on.

    This enum provides methods for determining opposite sides and appropriate movement directions
    for continuing or reversing carriage movement from each side position.
    """

    Left_Side = "Left_Side"  # The left-side of the needle beds at index 0.
    Right_Side = "Right_Side"  # The right-side of the needle beds at the needle-bed width.

    @property
    def opposite(self) -> Side_of_Needle_Bed:
        """Get the opposite side of the machine from this side.

        Returns:
            Side_of_Needle_Bed: The opposite side of this carriage side.
        """
        if self is Side_of_Needle_Bed.Left_Side:
            return Side_of_Needle_Bed.Right_Side
        else:
            return Side_of_Needle_Bed.Left_Side

    def slot(self, rightmost_slot: int = 540) -> int:
        """
        Args:
            rightmost_slot (int, optional): The number of needles on the needle bed used to determine the rightmost slot value. Defaults to 540.

        Returns:
            int: The slot number associated with this carriage side.
        """
        return -1 if self is Side_of_Needle_Bed.Left_Side else rightmost_slot + 1

    def __neg__(self) -> Side_of_Needle_Bed:
        """Get the opposite side using unary minus operator.

        Returns:
            Side_of_Needle_Bed: The opposite carriage side.
        """
        return self.opposite

    def __invert__(self) -> Side_of_Needle_Bed:
        """Get the opposite side using bitwise invert operator.

        Returns:
            Side_of_Needle_Bed: The opposite carriage side.
        """
        return self.opposite

    def __str__(self) -> str:
        """Return string representation of the carriage side.

        Returns:
            str: String representation of the side value.
        """
        return self.value

    def __repr__(self) -> str:
        """Return string representation of the carriage side.

        Returns:
            str: String representation of the side value.
        """
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: Side_of_Needle_Bed | int | Slotted_Position) -> bool:
        """
        Args:
            other (Side_of_Needle_Bed | int | Slotted_Position): The position on a needle bed to compare to.

        Returns:
            bool: True if this is positioned to the left of the given position.  False otherwise.
        """
        if other is Side_of_Needle_Bed.Left_Side:
            return False
        else:
            return self is Side_of_Needle_Bed.Left_Side
