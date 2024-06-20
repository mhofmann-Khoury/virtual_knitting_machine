"""A module containing warnings related to carriage movements."""

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import Carriage_Side


class Carriage_Warning(Knitting_Machine_Warning):

    def __init__(self, carriage, message: str):
        self.carriage = carriage
        super().__init__(message)


class Carriage_Off_Edge_Warning(Carriage_Warning):

    def __init__(self, carriage, target_position: int, edge: Carriage_Side, left_most_needle: int, right_most_position: int):
        self.edge = edge
        self.target_position = target_position
        if edge is Carriage_Side.Left_Side:
            self.set_position = left_most_needle
        else:
            self.set_position = right_most_position
        super().__init__(carriage, f"Carriage moved off edge {edge} to target position {target_position}. Position set to {self.set_position}")


class Carriage_Return_Warning(Carriage_Warning):
    def __init__(self, carriage, current_position: int, target_position: int, given_direction: Carriage_Pass_Direction):
        self.current_position = current_position
        self.given_direction = given_direction
        self.target_position = target_position
        super().__init__(carriage, f"Cannot move from {current_position} to {target_position} in direction {given_direction}.\n\tNo-op Carriage return added to position before {target_position}.")
