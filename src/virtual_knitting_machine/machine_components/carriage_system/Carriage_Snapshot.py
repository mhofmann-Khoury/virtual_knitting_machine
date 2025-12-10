"""A module containing the Carriage Snapshot Class"""

from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class Carriage_Snapshot:
    """
    A class used to represent a snapshot of the state of the given carriage at the time of instantiation.
    """

    def __init__(self, carriage: Carriage):
        self._carriage: Carriage = carriage
        self._left_needle_position: int = self._carriage.knitting_machine.needle_count - 1
        self._right_needle_position: int = 0
        self._transferring: bool = carriage.transferring
        self._last_direction: Carriage_Pass_Direction = carriage.last_direction
        self._current_needle_position: int = carriage.current_needle_position
        self._position_prior_to_transfers: int = carriage.position_prior_to_transfers
        self._direction_prior_to_transfers: Carriage_Pass_Direction = carriage.direction_prior_to_transfers

    @property
    def transferring(self) -> bool:
        """
        Returns:
            bool: True if the carriage was currently running transfers, False otherwise.
        """
        return self._transferring

    @property
    def current_needle_position(self) -> int:
        """
        Returns:
            int: The  needle position of the carriage at the time of the snapshot.
        """
        return self._current_needle_position

    @property
    def position_prior_to_transfers(self) -> int:
        """
        Returns:
            int: The position of the carriage prior to its last transfer pass.
        """
        return self._position_prior_to_transfers

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The last direction the carriage moved in prior to this snapshot.
        """
        return self._last_direction

    @property
    def reverse_of_last_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The opposite direction of the last carriage movement.
        """
        return self.last_direction.opposite()

    @property
    def direction_prior_to_transfers(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction the carriage was moving prior to the latest transfer pass.
        """
        return self._direction_prior_to_transfers

    @property
    def on_left_side(self) -> bool:
        """
        Returns:
            bool: True if positioned on very left side of machine, False otherwise.
        """
        return self.current_needle_position == self._left_needle_position

    @property
    def on_right_side(self) -> bool:
        """
        Returns:
            bool: True if positioned on very right side of machine, False otherwise.
        """
        return self.current_needle_position == self._right_needle_position

    def possible_directions(self) -> list[Carriage_Pass_Direction]:
        """
        Returns:
            list[Carriage_Pass_Direction]: List of possible directions the carriage could move from this position.
        """
        directions = []
        if not self.on_left_side:
            directions.append(Carriage_Pass_Direction.Leftward)
        if not self.on_right_side:
            directions.append(Carriage_Pass_Direction.Rightward)
        assert len(directions) > 0, "Carriage must have at least 1 direction option."
        return directions

    def left_of(self, needle_position: int) -> bool:
        """
        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if the snapshot carriage position is to the left of the given needle_position, False otherwise.
        """
        return self.current_needle_position < needle_position

    def right_of(self, needle_position: int) -> bool:
        """
        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if the snapshot carriage position is to the right of the given needle_position, False otherwise.
        """
        return needle_position < self.current_needle_position

    def on_position(self, needle_position: int) -> bool:
        """
        Args:
            needle_position (int): Position to compare to.

        Returns:
            bool: True if this snapshot carriage position is on the given needle_position, False otherwise.
        """
        return needle_position == self.current_needle_position

    def direction_to(self, needle_position: int) -> Carriage_Pass_Direction | None:
        """
        Args:
            needle_position (int): Needle position to target the direction towards.

        Returns:
            Carriage_Pass_Direction | None: Direction to move from snapshot position to given needle_position or None if on given position.
        """
        if self.left_of(needle_position):
            return Carriage_Pass_Direction.Rightward
        elif self.right_of(needle_position):
            return Carriage_Pass_Direction.Leftward
        else:
            return None
