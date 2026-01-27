"""Module containing the Slotted_Position protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


@runtime_checkable
class Slotted_Position(Protocol):
    """Protocol for machine components that have a known position relative to a needle bed slot"""

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
        ...

    def aligned_with_slot(self, slot: int | Slotted_Position) -> bool:
        """
        Args:
            slot (int | Slotted_Position): The slot to compare to.

        Returns:
            bool: True if this is positioned at the same slot, False otherwise.
        """
        slot = slot if isinstance(slot, int) else slot.slot_number
        return self.slot_number == slot

    def left_of_slot(self, slot: int | Slotted_Position) -> bool:
        """
        Args:
            slot (int | Slotted_Position): The slot to compare to.

        Returns:
            bool: True if this is positioned left of the given slot, False otherwise.
        """
        slot = slot if isinstance(slot, int) else slot.slot_number
        return self.slot_number < slot

    def right_of_slot(self, slot: int | Slotted_Position) -> bool:
        """
        Args:
            slot (int | Slotted_Position): The slot to compare to.

        Returns:
            bool: True if this is positioned right of the given slot, False otherwise.
        """
        slot = slot if isinstance(slot, int) else slot.slot_number
        return self.slot_number > slot

    def direction_to_slot(self, slot: int | Slotted_Position) -> Carriage_Pass_Direction | None:
        """
        Args:
            slot (int): The slot to find a direction towards.
        Returns:
            Carriage_Pass_Direction | None: The direction of carriage movement from this component to the slot or None if the slots are aligned.
        """
        slot = slot if isinstance(slot, int) else slot.slot_number
        if self.aligned_with_slot(slot):
            return None
        elif self.left_of_slot(slot):
            return Carriage_Pass_Direction.Rightward
        else:
            return Carriage_Pass_Direction.Leftward

    def in_pass_direction(self, slot: int | Slotted_Position, direction: Carriage_Pass_Direction) -> bool:
        """
        Args:
            slot (int | Slotted_Position): The slot following this slot in a carriage pass movement.
            direction (Carriage_Pass_Direction): The direction to test.

        Returns:
            bool: True if the given slot is after this slot in the given direction. False otherwise.
        """
        dir_to_slot = self.direction_to_slot(slot)
        return direction is dir_to_slot
