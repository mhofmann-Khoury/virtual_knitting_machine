"""Module containing the Needle_Bed_Position class"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle, Needle_Specification
from virtual_knitting_machine.machine_components.needles.slotted_position_protocol import Slotted_Position
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Needle_Bed_Position(Slotted_Position[Machine_LoopT]):
    """
    A class used to keep track of the position of machine components (i.e., carriers, carriage) relative to the needle beds.
    """

    def __init__(
        self,
        knitting_machine: Knitting_Machine_State[Machine_LoopT, Any],
        parking_position: Side_of_Needle_Bed = Side_of_Needle_Bed.Right_Side,
        stopping_distance: int = 10,
    ) -> None:
        self._knitting_machine: Knitting_Machine_State[Machine_LoopT, Any] = knitting_machine
        self._parking_position: Side_of_Needle_Bed = parking_position
        self._stopping_distance: int = stopping_distance
        self._position: Needle_Specification | Side_of_Needle_Bed = self._parking_position
        self._last_direction: Carriage_Pass_Direction = self.parked_direction.opposite()

    @property
    def knitting_machine(self) -> Knitting_Machine_State[Machine_LoopT, Any]:
        """
        Returns:
            Knitting_Machine_State: The knitting machine that owns this component.
        """
        return self._knitting_machine

    @property
    def position_on_bed(self) -> Needle_Specification | Side_of_Needle_Bed:
        """
        Returns:
            Needle_Specification | Side_of_Needle_Bed: The needle that the object is positioned relative to or the side of the needle bed it is parked on when inactive.
        """
        return self._position

    @property
    def current_bed_side(self) -> Side_of_Needle_Bed | None:
        """
        Returns:
            Side_of_Needle_Bed | None: The current bedside position or None if positioned relative to a needle.
        """
        return self._position if isinstance(self._position, Side_of_Needle_Bed) else None

    @property
    def parking_position(self) -> Side_of_Needle_Bed:
        """
        Returns:
            Side_of_Needle_Bed: The side of the needle bed that the machine component is parked at when it is not active.
        """
        return self._parking_position

    @property
    def parked_slot(self) -> int:
        """
        Returns:
            int: The slot number of the position when it is parked off the needle bed.
        """
        return self.parking_position.slot(self.needle_count_of_machine)

    @property
    def parked_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction of movement from a parked position.
        """
        return (
            Carriage_Pass_Direction.Leftward
            if self._parking_position is Side_of_Needle_Bed.Right_Side
            else Carriage_Pass_Direction.Rightward
        )

    @property
    def needle(self) -> Needle_Specification | None:
        """
        Returns:
            Needle_Specification | None: The needle that this component is positioned relative to or None if the components is parked off the needle bed.
        """
        return self._position if isinstance(self._position, Needle) else None

    @property
    def slot_number(self) -> int:
        """
        Returns:
            int: The slot number of the needle of this position or the slot number of the needle bed.

        Notes:
            When parked on the left side of the bed the slot is -1.
            When parked on the right side of the bed the slot 1 greater than the needle count of the machine.
        """
        if self.needle is not None:
            return self.needle.slot_by_racking(self.machine_racking)
        elif self.current_bed_side is not None:
            return self.current_bed_side.slot(self.needle_count_of_machine)
        else:
            return 0  # Note, shouldn't be hit since position is either needle or bed side.

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The last direction the object moved in.
        """
        return self._last_direction

    @property
    def reverse_of_last_direction(self) -> Carriage_Pass_Direction:
        """Get the reverse of the last direction the carriage moved in.

        Returns:
            Carriage_Pass_Direction: The opposite direction of the last carriage movement.
        """
        return self.last_direction.opposite()

    @property
    def on_bed(self) -> bool:
        """
        Returns:
            bool: True if the machine component is position relative to a needle on the bed. False otherwise.
        """
        return isinstance(self.position_on_bed, Needle)

    @property
    def between_needles(self) -> tuple[Needle_Specification | None, Needle_Specification | None]:
        """
        Returns:
            tuple[Needle_Specification | None, Needle_Specification | None]: The needles to the left and right of the position. None values imply the edge of the needle beds.
        """
        left = None
        right = None
        if self.needle is not None:
            if self._last_direction is Carriage_Pass_Direction.Rightward:
                left, right = self.needle, self.needle + 1
            else:
                left, right = self.needle - 1, self.needle
            if left.slot_by_racking(self.machine_racking) < 0:
                left = None
            if right.slot_by_racking(self.machine_racking) > self.needle_count_of_machine:
                right = None
        elif self.position_on_bed is Side_of_Needle_Bed.Left_Side:
            right = self.knitting_machine.get_specified_needle(is_front=True, position=0)
        elif self.position_on_bed is Side_of_Needle_Bed.Right_Side:
            left = self.knitting_machine.get_specified_needle(is_front=True, position=self.needle_count_of_machine)
        return left, right

    @property
    def conflicting_needle_slot(self) -> int | None:
        """
        Returns:
            int | None: The slot that currently conflicts with this position or None if the carrier is not active.
        """
        if not self.on_bed:
            return None
        elif self.last_direction is Carriage_Pass_Direction.Leftward:
            return self.slot_number - 1
        else:
            return self.slot_number + 1

    @property
    def slot_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range of positions that a component may exist after an ambiguous movement with a stopping distance.
        """
        if not self.on_bed:
            return self.slot_number, self.slot_number
        elif self.last_direction is Carriage_Pass_Direction.Leftward:
            return self.slot_number - self._stopping_distance, self.slot_number
        else:
            return self.slot_number, self.slot_number + self._stopping_distance

    def take_off_bed(self) -> None:
        """
        Sets the position to be parked off the needle bed.
        """
        self.set_position(None)

    def set_position(
        self, needle: Needle_Specification | None, direction: Carriage_Pass_Direction | None = None
    ) -> None:
        """
        Sets the position based on the given needle and current racking of the machine state.

        Args:
            needle (Needle_Specification): The new needle position that the carrier will move to or None if the carrier is moved off the needle bed.
            direction (Carriage_Pass_Direction | None, optional): The specific direction to set the carriage pass direction to.
                Defaults to inferring from the needle position and current state.
        """
        if needle is None:
            if direction is None:
                dir_to_slot = self.direction_to_slot(self.parked_slot)
                self._last_direction = dir_to_slot if dir_to_slot is not None else self.parked_direction
            else:
                self._last_direction = direction
            self._position = self.parking_position
        elif needle is not None:
            if direction is None:
                dir_to_slot = self.direction_to_slot(needle.slot_by_racking(self.machine_racking))
                self._last_direction = dir_to_slot if dir_to_slot is not None else self._last_direction.opposite()
            else:
                self._last_direction = direction
            self._position = needle

    def update_from_position(self, other_position: Needle_Bed_Position) -> None:
        """
        Updates this position to match the given position.
        Args:
            other_position (Needle_Bed_Position): The position to match the needle bed.
        """
        self.set_position(other_position.needle, other_position.last_direction)

    def __eq__(self, other: object) -> bool:
        """
        Args:
            other (Slotted_Component | int):
                The other position or positioned object to compare to.
                If other is not a position, only the slot number is compared.

        Returns:
            bool: True if this position matches the given position.
        """
        if isinstance(other, Needle_Bed_Position):
            return self.position_on_bed == other.position_on_bed and self.last_direction == other.last_direction
        elif isinstance(other, Relative_to_Needle_Bed):
            return self == other.position_on_bed
        elif not self.on_bed:
            return False
        elif isinstance(other, Slotted_Position):
            return self.slot_number == other.slot_number
        elif isinstance(other, int):
            return self.slot_number == other
        else:  # Any other object type comparison
            return False

    def __lt__(self, other: Slotted_Position | int) -> bool:
        """
        Args:
            other (Slotted_Position | int): The slot, needle, or position to compare to.

        Returns:
            bool: True if the slot of this position is to the left of the other position, False otherwise.
        """
        return self.left_of_slot(other)


@runtime_checkable
class Relative_to_Needle_Bed(Slotted_Position[Machine_LoopT], Protocol):
    """Protocol for Machine components which move relative to the needle bed such as the Carriage and carriers."""

    @property
    def position_on_bed(self) -> Needle_Bed_Position[Machine_LoopT]:
        """
        Returns:
            Needle_Bed_Position: The position of the machine component relative to the needle bed.
        """
        ...

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
        return self.position_on_bed.slot_number

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The last direction the object moved in.
        """
        return self.position_on_bed.last_direction
