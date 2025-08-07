"""A module containing warnings related to carriage movements."""

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import Carriage_Side


class Carriage_Off_Edge_Warning(Knitting_Machine_Warning):

    def __init__(self, target_position: int, edge: Carriage_Side, left_most_needle: int, right_most_position: int) -> None:
        self.edge: Carriage_Side = edge
        self.target_position: int = target_position
        if edge is Carriage_Side.Left_Side:
            self.set_position: int = left_most_needle
        else:
            self.set_position: int = right_most_position
        super().__init__(f"Carriage moved off edge {edge} to target position {target_position}. Position set to {self.set_position}")
