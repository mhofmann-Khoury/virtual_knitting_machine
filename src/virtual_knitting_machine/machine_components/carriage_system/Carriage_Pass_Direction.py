"""Enumerator module for possible carriage pass directions on knitting machines.

This module defines the two directions a carriage can move across the needle bed and provides utility functions for
needle positioning, comparison, and sorting operations relative to carriage movement direction.
"""
from __future__ import annotations

import functools
from enum import Enum
from typing import Iterable

from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Carriage_Pass_Direction(Enum):
    """An enumerator for the two directions the carriage can pass on the knitting machine.

    Needles are oriented on the machine left to right in ascending order: Left -> 0 1 2 ... N <- Right.
    This enum provides methods for needle comparison, positioning, and sorting operations relative to carriage movement direction.
    """
    Leftward = "-" # Represents a Leftward decreasing movement of the carriage pass.
    Rightward = "+" # Represents a Rightward increasing movement of the carriage pass.

    def opposite(self) -> Carriage_Pass_Direction:
        """Get the opposite pass direction of this direction.

        Returns:
            Carriage_Pass_Direction: The opposite pass direction of this direction.
        """
        if self is Carriage_Pass_Direction.Leftward:
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def __neg__(self) -> Carriage_Pass_Direction:
        """Get the opposite direction using unary minus operator.

        Returns:
            Carriage_Pass_Direction: The opposite pass direction.
        """
        return self.opposite()

    def __invert__(self) -> Carriage_Pass_Direction:
        """Get the opposite direction using bitwise invert operator.

        Returns:
            Carriage_Pass_Direction: The opposite pass direction.
        """
        return self.opposite()

    def next_needle_position(self, needle_pos: int) -> int:
        """Get the next needle position in the given direction.

        Args:
            needle_pos (int): The needle position that we are looking for the next neighbor of.

        Returns:
            int: The next needle position in the pass direction.
        """
        if self is Carriage_Pass_Direction.Leftward:
            return needle_pos - 1
        else:
            return needle_pos + 1

    def prior_needle_position(self, needle_pos: int) -> int:
        """Get the prior needle position in the given direction.

        Args:
            needle_pos (int): The needle position that we are looking for the prior neighbor of.

        Returns:
            int: The prior needle position in the pass direction.
        """
        if self is Carriage_Pass_Direction.Leftward:
            return needle_pos + 1
        else:
            return needle_pos - 1

    @staticmethod
    def rightward_needles_comparison(first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """Compare two needles for rightward carriage movement ordering.

        Args:
            first_needle (Needle): First needle to test ordering.
            second_needle (Needle): Second needle to test order.
            rack (int, optional): Rack value of machine. Defaults to 0.
            all_needle_rack (bool, optional): True if allowing all_needle knitting on ordering. Defaults to False.

        Returns:
            int: 1 if first_needle is left of second needle (rightward order), 0 if needles are in equal position at given racking, or -1 if first_needle is right of second needle (leftward order).
        """
        return int(-1 * first_needle.at_racking_comparison(second_needle, rack, all_needle_rack))

    @staticmethod
    def leftward_needles_comparison(first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """Compare two needles for leftward carriage movement ordering.

        Args:
            first_needle (Needle): First needle to test ordering.
            second_needle (Needle): Second needle to test order.
            rack (int, optional): Rack value of machine. Defaults to 0.
            all_needle_rack (bool, optional): True if allowing all_needle knitting on ordering. Defaults to False.

        Returns:
            int: -1 if first_needle is to the left of second needle (rightward order),
            0 if needles are in equal position at given racking, or 1 if first_needle is right of second needle (leftward order).
        """
        return int(first_needle.at_racking_comparison(second_needle, rack, all_needle_rack))

    def needle_direction_comparison(self, first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """Compare two needles based on their order in this carriage pass direction.

        Args:
            first_needle (Needle): First needle to test ordering.
            second_needle (Needle): Second needle to test order.
            rack (int, optional): Rack value of machine. Defaults to 0.
            all_needle_rack (bool, optional): True if allowing all_needle knitting on ordering. Defaults to False.

        Returns:
            int: -1 if first_needle comes after second_needle in pass direction, 0 if needles are at equal alignment given the racking, 1 if first needle comes before second_needle in pass direction.
        """
        if self is Carriage_Pass_Direction.Rightward:
            return Carriage_Pass_Direction.rightward_needles_comparison(first_needle, second_needle, rack, all_needle_rack)
        else:
            return Carriage_Pass_Direction.leftward_needles_comparison(first_needle, second_needle, rack, all_needle_rack)

    def needles_are_in_pass_direction(self, first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> bool:
        """Check if the first needle comes before the second needle in the given pass direction.

        Args:
            first_needle (Needle): First needle to test this pass direction.
            second_needle (Needle): Second needle to test this pass direction.
            rack (int, optional): Rack value of machine. Defaults to 0.
            all_needle_rack (bool, optional): True if allowing all_needle knitting on ordering. Defaults to False.

        Returns:
            bool: True if the first needle comes before the second needle in the given pass direction, False otherwise.
        """
        return self.needle_direction_comparison(first_needle, second_needle, rack, all_needle_rack) > 0

    @staticmethod
    def get_direction(dir_str: str) -> Carriage_Pass_Direction:
        """Return a Pass direction enum given a valid string representation.

        Args:
            dir_str (str): String to convert to direction ("-" for Leftward, anything else for Rightward).

        Returns:
            Carriage_Pass_Direction: Pass direction corresponding to the string.
        """
        if dir_str == "-":
            return Carriage_Pass_Direction.Leftward
        else:
            return Carriage_Pass_Direction.Rightward

    def sort_needles(self, needles: Iterable[Needle], racking: int = 0) -> list[Needle]:
        """Return needles sorted in this direction at given racking.

        Args:
            needles (Iterable[Needle]): Needles to be sorted in pass direction.
            racking (int, optional): The racking to sort needles in, sets back bed offset. Defaults to 0.

        Returns:
            list[Needle]: List of needles sorted in the pass direction.
        """
        ascending = self is Carriage_Pass_Direction.Rightward
        position_sorted = sorted(needles,
                                 key=functools.cmp_to_key(lambda x, y: Needle.needle_at_racking_cmp(x, y, racking, all_needle_racking=True)),
                                 reverse=not ascending)
        return position_sorted

    def __str__(self) -> str:
        """Return string representation of the carriage pass direction.

        Returns:
            str: String representation of the direction value.
        """
        return self.value

    def __repr__(self) -> str:
        """Return string representation of the carriage pass direction.

        Returns:
            str: String representation of the direction value.
        """
        return self.value
