"""Module containing the Carriage_Side enumeration for knitting machine carriage positioning.

This module defines the two sides of a knitting machine that the carriage can be positioned on
and provides utility methods for determining appropriate movement directions from each side.
"""
from __future__ import annotations

from enum import Enum

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)


class Carriage_Side(Enum):
    """Enumeration containing the two sides the machine carriage can be positioned on.

    This enum provides methods for determining opposite sides and appropriate movement directions
    for continuing or reversing carriage movement from each side position.
    """
    Left_Side = "Left_Side" # The left-side of the needle beds at index 0.
    Right_Side = "Right_Side" # The right-side of the needle beds at the needle-bed width.

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

    def opposite(self) -> Carriage_Side:
        """Get the opposite side of the machine from this side.

        Returns:
            Carriage_Side: The opposite side of this carriage side.
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Side.Right_Side
        else:
            return Carriage_Side.Left_Side

    def reverse_direction(self) -> Carriage_Pass_Direction:
        """Get the direction that will reverse the carriage away from this side position.

        Returns:
            Carriage_Pass_Direction: Direction that will reverse the carriage from this side position.
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def current_direction(self) -> Carriage_Pass_Direction:
        """Get the direction that will continue the carriage pass moving toward this side.

        Returns:
            Carriage_Pass_Direction: Direction that will continue the carriage pass moving in the current direction toward this side.
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Pass_Direction.Leftward
        else:
            return Carriage_Pass_Direction.Rightward

    def __neg__(self) -> Carriage_Side:
        """Get the opposite side using unary minus operator.

        Returns:
            Carriage_Side: The opposite carriage side.
        """
        return self.opposite()

    def __invert__(self) -> Carriage_Side:
        """Get the opposite side using bitwise invert operator.

        Returns:
            Carriage_Side: The opposite carriage side.
        """
        return self.opposite()
