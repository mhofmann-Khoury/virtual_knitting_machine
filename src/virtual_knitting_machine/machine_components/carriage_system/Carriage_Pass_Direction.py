"""Enumerator of possible pass directions"""
import functools
from enum import Enum
from typing import Iterable

from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Carriage_Pass_Direction(Enum):
    """
    An enumerator for the two directions the carriage can pass on the machine.
    Needles are oriented on the machine left to right in ascending order:
    Left -> 0 1 2 ... N <- Right
    """
    Leftward = "-"
    Rightward = "+"

    def opposite(self):
        """
        :return: the opposite pass direction of this
        """
        if self is Carriage_Pass_Direction.Leftward:
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def __neg__(self):
        return self.opposite()

    def __invert__(self):
        return self.opposite()

    def next_needle_position(self, needle_pos: int):
        """
        Gets the next needle in a given direction
        :param needle_pos: the needle that we are looking for the next neighbor of
        :return: the next needle position in the pass direction
        """
        if self is Carriage_Pass_Direction.Leftward:
            return needle_pos - 1
        else:
            return needle_pos + 1

    def prior_needle_position(self, needle_pos: int):
        """
        Gets the prior needle in a given direction
        :param needle_pos: the needle that we are looking for the prior neighbor of
        :return: the prior needle position in the pass direction
        """
        if self is Carriage_Pass_Direction.Leftward:
            return needle_pos + 1
        else:
            return needle_pos - 1

    @staticmethod
    def rightward_needles_comparison(first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """
        :param first_needle: first needle to test ordering
        :param second_needle: second needle to test order
        :param rack: rack value of machine
        :param all_needle_rack: True if allowing all_needle knitting on ordering
        :return: 1 first_needle is left of second needle (rightward order),
            0 needles are in equal position at given racking,
            or -1 first_needle is right of second needle (leftward order).
        """
        return -1 * first_needle.at_racking_comparison(second_needle, rack, all_needle_rack)

    @staticmethod
    def leftward_needles_comparison(first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """
        :param first_needle: first needle to test ordering
        :param second_needle: second needle to test order
        :param rack: rack value of machine
        :param all_needle_rack: True if allowing all_needle knitting on ordering
        :return: -1 first_needle is to the left of second needle (rightward order),
            0 needles are in equal position at given racking,
            or 1 first_needle is right of second needle (leftward order).
        """
        return first_needle.at_racking_comparison(second_needle, rack, all_needle_rack)

    def needle_direction_comparison(self, first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> int:
        """
        :param first_needle: first needle to test ordering.
        :param second_needle: Second needle to test order.
        :param rack: Rack value of machine.
        :param all_needle_rack: True if allowing all_needle knitting on ordering.
        :return: -1 if first_needle is first needle comes after second_needle in pass direction,
        0 if needles are at equal alignment given the racking,
        1 if first needle comes before second_needle in pass direction.
        """
        if self is Carriage_Pass_Direction.Rightward:
            return Carriage_Pass_Direction.rightward_needles_comparison(first_needle, second_needle, rack, all_needle_rack)
        else:
            return Carriage_Pass_Direction.leftward_needles_comparison(first_needle, second_needle, rack, all_needle_rack)

    def needles_are_in_pass_direction(self, first_needle: Needle, second_needle: Needle, rack: int = 0, all_needle_rack: bool = False) -> bool:
        """
        :param rack:
        :param all_needle_rack:
        :param first_needle: First needle to test this pass direction.
        :param second_needle: Second needle to test this pass direction.
        :return: True if the first needle comes before the second needle in the given pass direction.
        """
        return self.needle_direction_comparison(first_needle, second_needle, rack, all_needle_rack) > 0

    @staticmethod
    def get_direction(dir_str):
        """
        Returns a Pass direction enum given a valid string.
        :param dir_str: String to convert to direction
        :return: Pass direction by string
        """
        if dir_str == "-":
            return Carriage_Pass_Direction.Leftward
        else:
            return Carriage_Pass_Direction.Rightward

    def sort_needles(self, needles: Iterable[Needle], racking: int = 0) -> list[Needle]:
        """
        Return needles sorted in direction at given racking
        :param racking: The racking to sort needles in. Sets back bed offset
        :param needles: needles to be sorted in pass direction.
        :return: List of needles sorted in the pass direction
        """
        ascending = self is Carriage_Pass_Direction.Rightward
        position_sorted = sorted(needles,
                                 key=functools.cmp_to_key(lambda x, y: Needle.needle_at_racking_cmp(x, y, racking, all_needle_racking=True)),
                                 reverse=not ascending)
        return position_sorted

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
