"""Module containing the Carriage Side Enum"""
from __future__ import annotations
from enum import Enum

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class Carriage_Side(Enum):
    """Enum containing the two sides the machine carriage can move to."""
    Left_Side = "Left_Side"
    Right_Side = "Right_Side"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value

    def opposite(self) -> Carriage_Side:
        """
        :return: the opposite pass direction of this
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Side.Right_Side
        else:
            return Carriage_Side.Left_Side

    def reverse_direction(self) -> Carriage_Pass_Direction:
        """
        :return: Direction that will reverse the carriage from this side position.
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def current_direction(self) -> Carriage_Pass_Direction:
        """
        :return: Directions that will continue the carriage pass moving in the current direction.
        """
        if self is Carriage_Side.Left_Side:
            return Carriage_Pass_Direction.Leftward
        else:
            return Carriage_Pass_Direction.Rightward

    def __neg__(self) -> Carriage_Side:
        return self.opposite()

    def __invert__(self) -> Carriage_Side:
        return self.opposite()
