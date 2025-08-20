"""A module containing the Carriage class for managing carriage position and movements in virtual knitting machines.
This module provides functionality for tracking carriage position, validating movements, and managing transfer operations on knitting machines."""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_warnings.Carriage_Warning import (
    Carriage_Off_Edge_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import (
    Carriage_Side,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine


class Carriage:
    """A class for tracking the carriage's position and managing possible movements on a knitting machine.

    The carriage is responsible for moving across the needle bed and performing knitting operations.
    This class manages position validation, movement direction tracking, and transfer operation states.

    Attributes:
        knitting_machine (Knitting_Machine): The Knitting machine this carriage belongs to.

    """

    def __init__(self, knitting_machine: Knitting_Machine, right_needle_position: int, left_needle_position: int = 0) -> None:
        """Initialize a new carriage with specified position range and starting direction.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine this carriage belongs to.
            right_needle_position (int): The rightmost needle position the carriage can reach.
            left_needle_position (int, optional): The leftmost needle position the carriage can reach. Defaults to 0.

        Raises:
            AssertionError: If left_needle_position is not less than right_needle_position.
        """
        self.knitting_machine: Knitting_Machine = knitting_machine
        if left_needle_position > right_needle_position:  # Swaps positions if they are not in the right order.
            hold_r = right_needle_position
            right_needle_position = left_needle_position
            left_needle_position = hold_r
        self._left_needle_position: int = left_needle_position
        self._right_needle_position: int = right_needle_position
        self._last_direction: Carriage_Pass_Direction = Carriage_Pass_Direction.Leftward
        self._current_needle_position: int = self._left_needle_position
        self._transferring: bool = False
        self._position_prior_to_transfers: int = self.current_needle_position
        self._direction_prior_to_transfers: Carriage_Pass_Direction = self.last_direction
        if self.last_direction is Carriage_Pass_Direction.Rightward:
            self.current_needle_position = self._right_needle_position

    @property
    def transferring(self) -> bool:
        """Check if carriage is currently running transfers.

        Returns:
            bool: True if carriage is currently running transfers, False otherwise.
        """
        return self._transferring

    @transferring.setter
    def transferring(self, is_transferring: bool) -> None:
        """Set the transfer state of the carriage and restore position if ending transfers.

        Args:
            is_transferring (bool): True to start transfers, False to end transfers.
        """
        self._transferring = is_transferring
        if not self._transferring:
            self.move_to(self._position_prior_to_transfers)
            self.last_direction = self._direction_prior_to_transfers

    @property
    def current_needle_position(self) -> int:
        """Get the front bed aligned position of the carriage at this time.

        Returns:
            int: The current needle position of the carriage.
        """
        return self._current_needle_position

    @current_needle_position.setter
    def current_needle_position(self, new_position: int) -> None:
        """Set the current needle position and update transfer state tracking.

        Args:
            new_position (int): The new position for the carriage.
        """
        self._current_needle_position = new_position
        if not self.transferring:
            self._position_prior_to_transfers = new_position

    @property
    def reverse_of_last_direction(self) -> Carriage_Pass_Direction:
        """Get the reverse of the last direction the carriage moved in.

        Returns:
            Carriage_Pass_Direction: The opposite direction of the last carriage movement.
        """
        return self.last_direction.opposite()

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """Get the last direction the carriage moved in.

        Returns:
            Carriage_Pass_Direction: The last direction the carriage moved in.
        """
        return self._last_direction

    @last_direction.setter
    def last_direction(self, new_direction: Carriage_Pass_Direction) -> None:
        """Set the last direction the carriage moved and update transfer state tracking.

        Args:
            new_direction (Carriage_Pass_Direction): The new direction to set as last direction.
        """
        self._last_direction = new_direction
        if not self.transferring:
            self._direction_prior_to_transfers = new_direction

    @property
    def on_left_side(self) -> bool:
        """Check if carriage is positioned on the very left side of the machine.

        Returns:
            bool: True if positioned on very left side of machine, False otherwise.
        """
        return self.current_needle_position == self._left_needle_position

    @property
    def on_right_side(self) -> bool:
        """Check if carriage is positioned on the very right side of the machine.

        Returns:
            bool: True if positioned on very right side of machine, False otherwise.
        """
        return self.current_needle_position == self._right_needle_position

    def possible_directions(self) -> list[Carriage_Pass_Direction]:
        """Get list of possible directions the carriage can move from this position.

        Returns:
            list[Carriage_Pass_Direction]: List of possible directions the carriage can move from this position.

        Raises:
            AssertionError: If no directions are available (should never happen with valid carriage range).
        """
        directions = []
        if not self.on_left_side:
            directions.append(Carriage_Pass_Direction.Leftward)
        if not self.on_right_side:
            directions.append(Carriage_Pass_Direction.Rightward)
        assert len(directions) > 0, f"Carriage must have at least 1 direction option."
        return directions

    def left_of(self, needle_position: int) -> bool:
        """Check if the current carriage position is to the left of the given needle position.

        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if the current carriage position is to the left of the given needle_position, False otherwise.
        """
        return self.current_needle_position < needle_position

    def right_of(self, needle_position: int) -> bool:
        """Check if the current carriage position is to the right of the given needle position.

        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if the current carriage position is to the right of the given needle_position, False otherwise.
        """
        return needle_position < self.current_needle_position

    def on_position(self, needle_position: int) -> bool:
        """Check if the carriage position is exactly on the given needle position.

        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if this carriage position is on the given needle_position, False otherwise.
        """
        return needle_position == self.current_needle_position

    def direction_to(self, needle_position: int) -> Carriage_Pass_Direction | None:
        """Get the direction needed to move from current position to given needle position.

        Args:
            needle_position (int): Needle position to target the direction towards.

        Returns:
            Carriage_Pass_Direction | None: Direction to move from current position to given needle_position or None if on given position.
        """
        if self.left_of(needle_position):
            return Carriage_Pass_Direction.Rightward
        elif self.right_of(needle_position):
            return Carriage_Pass_Direction.Leftward
        else:
            return None

    def move(self, direction: Carriage_Pass_Direction, end_position: int) -> None:
        """Update current needle position based on given target and direction with validation.

        Args:
            direction (Carriage_Pass_Direction): Direction to move the carriage in.
            end_position (int): The position to move the carriage to.

        Warns:
            Carriage_Off_Edge_Warning: If the target needle is off the edge of the bed, will update the current needle to the edge.
        """
        direction_to_position = self.direction_to(end_position)
        if (direction_to_position is not direction) and (direction_to_position is not None):
            self.move_to(end_position)
        if end_position < self._left_needle_position:
            warnings.warn(Carriage_Off_Edge_Warning(end_position, Carriage_Side.Left_Side, self._left_needle_position, self._right_needle_position))
            end_position = self._left_needle_position
        elif end_position > self._right_needle_position:
            warnings.warn(Carriage_Off_Edge_Warning(end_position, Carriage_Side.Right_Side, self._left_needle_position, self._right_needle_position))
            end_position = self._right_needle_position
        self.current_needle_position = end_position
        self.last_direction = direction

    def move_to(self, end_position: int) -> None:
        """Move the carriage, regardless of current position, to end position.

        Args:
            end_position (int): New position of carriage.
        """
        direction_of_move = self.direction_to(end_position)
        if direction_of_move is not None:
            self.move(direction_of_move, end_position)

    def move_in_reverse_direction(self, end_position: int) -> None:
        """Move in reverse of last direction to given end position.

        Args:
            end_position (int): Position to move to.
        """
        self.move(self.reverse_of_last_direction, end_position)

    def move_in_current_direction(self, end_position: int) -> None:
        """Move in the current direction to given end position.

        Args:
            end_position (int): Position to move to.
        """
        self.move(self.last_direction, end_position)
