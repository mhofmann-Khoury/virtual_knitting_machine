"""Enumerator module for possible carriage pass directions on knitting machines.

This module defines the two directions a carriage can move across the needle bed and provides utility functions for
needle positioning, comparison, and sorting operations relative to carriage movement direction.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle_Specification


class Carriage_Pass_Direction(Enum):
    """An enumerator for the two directions the carriage can pass on the knitting machine.

    Needles are oriented on the machine left to right in ascending order: Left -> 0 1 2 ... N <- Right.
    This enum provides methods for needle comparison, positioning, and sorting operations relative to carriage movement direction.
    """

    Leftward = "-"  # Represents a Leftward decreasing movement of the carriage pass.
    Rightward = "+"  # Represents a Rightward increasing movement of the carriage pass.

    def opposite(self) -> Carriage_Pass_Direction:
        """Get the opposite pass direction of this direction.

        Returns:
            Carriage_Pass_Direction: The opposite pass direction of this direction.
        """
        if self is Carriage_Pass_Direction.Leftward:
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def sort_needles(
        self, needles: Iterable[Needle_Specification], racking: int | None = None
    ) -> list[Needle_Specification]:
        """Return needles sorted in this direction at given racking.

        Args:
            needles (Iterable[Needle_Specification]): Needles to be sorted in pass direction.
            racking (int, optional):
                The racking to sort needles in, sets back bed offset.
                Defaults to the racking of the first Needle with a specified machine or 0 if no needle on a machine is included.

        Returns:
            list[Needle_Specification]: List of needles sorted in the pass direction.
        """
        if racking is None:
            racking = next((n.machine_racking for n in needles if hasattr(n, "machine_racking")), 0)

        ascending = self is Carriage_Pass_Direction.Rightward

        position_sorted = sorted(
            needles,
            key=lambda n: (n.slot_by_racking(racking), n.is_front),
            reverse=not ascending,
        )
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
        return f"{self.name}<{self.value}"

    def __hash__(self) -> int:
        return hash(self.value)

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
