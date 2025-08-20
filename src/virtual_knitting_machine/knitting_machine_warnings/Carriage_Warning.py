"""A module containing warnings related to carriage movements and positioning on knitting machines.
This module provides warning classes for carriage position violations such as attempting to move the carriage beyond the machine's physical needle bed boundaries."""

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    Knitting_Machine_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import (
    Carriage_Side,
)


class Carriage_Off_Edge_Warning(Knitting_Machine_Warning):
    """A warning for carriage movements that attempt to position the carriage beyond the machine's edge boundaries.
    This warning occurs when the carriage is instructed to move to a position outside the valid needle range, and the position is automatically corrected to the nearest valid edge position."""

    def __init__(self, target_position: int, edge: Carriage_Side, left_most_needle: int, right_most_position: int) -> None:
        """Initialize a carriage off-edge warning.

        Args:
            target_position (int): The originally requested carriage position that was out of bounds.
            edge (Carriage_Side): The side of the machine where the boundary was exceeded.
            left_most_needle (int): The leftmost valid needle position on the machine.
            right_most_position (int): The rightmost valid needle position on the machine.
        """
        self.edge: Carriage_Side = edge
        self.target_position: int = target_position
        if edge is Carriage_Side.Left_Side:
            self.set_position: int = left_most_needle
        else:
            self.set_position: int = right_most_position
        super().__init__(f"Carriage moved off edge {edge} to target position {target_position}. Position set to {self.set_position}")
