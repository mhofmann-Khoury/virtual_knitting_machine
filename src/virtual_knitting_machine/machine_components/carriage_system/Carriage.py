"""A module containing the Carriage class."""
import warnings

from virtual_knitting_machine.knitting_machine_warnings.Carriage_Warning import Carriage_Return_Warning, Carriage_Off_Edge_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import Carriage_Side


class Carriage:
    """
        Keep track of the Carriage's position and possible movements.
    """

    def __init__(self, knitting_machine, right_needle_position: int, left_needle_position: int = 0, last_carriage_direction: Carriage_Pass_Direction = Carriage_Pass_Direction.Leftward):
        self.knitting_machine = knitting_machine
        assert left_needle_position < right_needle_position, f"Carriage must have range of motion."
        self._left_needle_position: int = left_needle_position
        self._right_needle_position: int = right_needle_position
        self._last_direction: Carriage_Pass_Direction = last_carriage_direction
        self._current_needle_position: int = self._left_needle_position
        self._transferring: bool = False
        self._position_prior_to_transfers = self.current_needle_position
        self._direction_prior_to_transfers = self.last_direction
        if self.last_direction is Carriage_Pass_Direction.Rightward:
            self.current_needle_position = self._right_needle_position

    @property
    def transferring(self) -> bool:
        """
        :return: True if carriage is currently running transfers.
        """
        return self._transferring

    @transferring.setter
    def transferring(self, is_transferring: bool):
        self._transferring = is_transferring
        if not self._transferring:
            self.move_to(self._position_prior_to_transfers)
            self.last_direction = self._direction_prior_to_transfers

    @property
    def current_needle_position(self) -> int:
        """
        :return: The front bed aligned position of the carriage at this time.
        """
        return self._current_needle_position

    @current_needle_position.setter
    def current_needle_position(self, new_position: int):
        self._current_needle_position = new_position
        if not self.transferring:
            self._position_prior_to_transfers = new_position

    @property
    def reverse_of_last_direction(self) -> Carriage_Pass_Direction:
        """
        :return: Reverse of the last direction the carriage moved in.
        """
        return self.last_direction.opposite()

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """
        :return: Last direction the carriage moved in.
        """
        return self._last_direction

    @last_direction.setter
    def last_direction(self, new_direction: Carriage_Pass_Direction):
        self._last_direction = new_direction
        if not self.transferring:
            self._direction_prior_to_transfers = new_direction

    @property
    def on_left_side(self) -> bool:
        """
        :return: True if positioned on very left side of machine.
        """
        return self.current_needle_position == self._left_needle_position

    @property
    def on_right_side(self) -> bool:
        """
        :return: True if position on very right side of machine.
        """
        return self.current_needle_position == self._right_needle_position

    def possible_directions(self) -> list[Carriage_Pass_Direction]:
        """
        :return: list of possible directions the carriage can move from this position.
        """
        directions = []
        if not self.on_left_side:
            directions.append(Carriage_Pass_Direction.Leftward)
        if not self.on_right_side:
            directions.append(Carriage_Pass_Direction.Rightward)
        assert len(directions) > 0, f"Carriage must have at least 1 direction option."
        return directions

    def left_of(self, needle_position: int) -> bool:
        """
        :param needle_position: Position to compare to.
        :return: True if the current carriage position is to the left of the given needle_position, False otherwise.
        """
        return self.current_needle_position < needle_position

    def right_of(self, needle_position: int) -> bool:
        """
        :param needle_position: Position to compare to.
        :return: True if the current carriage position is to the right of the given needle_position, False otherwise.
        """
        return needle_position < self.current_needle_position

    def on_position(self, needle_position: int) -> bool:
        """
        :param needle_position: Position to compare to.
        :return: True if this carriage position is on the given needle_position, False otherwise.
        """
        return needle_position == self.current_needle_position

    def direction_to(self, needle_position: int) -> Carriage_Pass_Direction | None:
        """
        :param needle_position: needle_position to target the direction towards.
        :return: Direction to move from current position to given needle_position or None if on given position.
        """
        if self.left_of(needle_position):
            return Carriage_Pass_Direction.Rightward
        elif self.right_of(needle_position):
            return Carriage_Pass_Direction.Leftward

    def move(self, direction: Carriage_Pass_Direction, end_position: int):
        """
        Updates current needle position based on given target a direction. 
        Will raise errors if movement is not possible from the current position.
        Will raise a warning if the target needle is off the edge of the bed. It will update the current needle to the edge.
        :param direction: Direction to move the carriage in.
        :param end_position: The position to move the carriage to.
        """
        if direction not in self.possible_directions():
            warnings.warn(Carriage_Return_Warning(self, self.current_needle_position, end_position, direction))
            # raise Carriage_Cannot_Move_In_Direction(self, direction)
        direction_to_position = self.direction_to(end_position)
        if (direction_to_position is not direction) and (direction_to_position is not None):
            # warnings.warn(Carriage_Return_Warning(self, self.current_needle_position, end_position, direction))
            self.move_to(end_position)
        if end_position < self._left_needle_position:
            warnings.warn(Carriage_Off_Edge_Warning(self, end_position, Carriage_Side.Left_Side, self._left_needle_position, self._right_needle_position))
            end_position = self._left_needle_position
        elif end_position > self._right_needle_position:
            warnings.warn(Carriage_Off_Edge_Warning(self, end_position, Carriage_Side.Right_Side, self._left_needle_position, self._right_needle_position))
            end_position = self._right_needle_position
        self.current_needle_position = end_position
        self.last_direction = direction

    def move_to(self, end_position: int):
        """
        Move the carriage, regardless of current position, to end position.
        :param end_position: New position of carriage.
        """
        direction_of_move = self.direction_to(end_position)
        if direction_of_move is not None:
            self.move(direction_of_move, end_position)

    def move_in_reverse_direction(self, end_position: int):
        """
        Move in reverse of last direction to given end position.
        :param end_position: Position to move to.
        """
        self.move(self.reverse_of_last_direction, end_position)

    def move_in_current_direction(self, end_position: int):
        """
        Move in the current direction to given end position.
        :param end_position: Position to move to.
        """
        self.move(self.last_direction, end_position)
