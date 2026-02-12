"""A module containing the Carriage class for managing carriage position and movements in virtual knitting machines.
This module provides functionality for tracking carriage position, validating movements, and managing transfer operations on knitting machines."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

from virtual_knitting_machine.machine_components.needle_bed_position import Needle_Bed_Position, Relative_to_Needle_Bed
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Specification
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
        Carriage_Pass_Direction,
    )

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Carriage_State(Relative_to_Needle_Bed[Machine_LoopT], Protocol):
    """Protocol defining readable attributes of carriages."""

    @property
    def last_set_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction the carriage was last explicitly moved in (i.e., knits, tucks, splits).
        """
        ...


class Carriage(Carriage_State[Machine_LoopT]):
    """A class for tracking the carriage's position and managing possible movements on a knitting machine.

    The carriage is responsible for moving across the needle bed and performing knitting operations.
    This class manages position validation, movement direction tracking, and transfer operation states.

    """

    def __init__(self, knitting_machine: Knitting_Machine[Machine_LoopT]) -> None:
        """Initialize a new carriage with specified position range and starting direction.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine this carriage belongs to.
        """
        self._knitting_machine: Knitting_Machine[Machine_LoopT] = knitting_machine
        self._position: Needle_Bed_Position = Needle_Bed_Position(
            self.knitting_machine, parking_position=Side_of_Needle_Bed.Left_Side, stopping_distance=0
        )
        self._last_set_direction: Carriage_Pass_Direction = self._position.last_direction

    @property
    def knitting_machine(self) -> Knitting_Machine[Machine_LoopT]:
        """
        Returns:
            Knitting_Machine: The knitting machine that owns this carriage.
        """
        return self._knitting_machine

    @property
    def position_on_bed(self) -> Needle_Bed_Position[Machine_LoopT]:
        """
        Returns:
            Needle_Bed_Position: The position of the carriage relative to the needle bed.
        """
        return self._position

    @property
    def last_set_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction the carriage was moving prior to the current transfer pass.
        """
        return self._last_set_direction

    def move_in_direction(self, needle: Needle_Specification, direction: Carriage_Pass_Direction) -> None:
        """
        Move the carriage to the target needle in the specified direction.
        Updates the last_set_direction to the given direction.
        Args:
            needle (Needle): The needle to move to.
            direction (Carriage_Pass_Direction): The direction of the movement.
        """
        self._position.set_position(needle, direction)
        self._last_set_direction = direction

    def move_to_needle(self, needle: Needle_Specification) -> None:
        """Move the carriage to the target needle in the inferred direction.

        Args:
            needle (Needle): The needle to move the carriage to.

        Notes:
            Does not update last_set_direction. Last set direction can be used to infer explicit movements rather than implied directions for drops and xfers.
        """
        self._position.set_position(needle)
