"""A Module containing warnings about carriage passes."""
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning


class Reordered_Knitting_Pass_Warning(Knitting_Machine_Warning):

    def __init__(self, direction, carriage_pass):
        self.direction = direction
        self.carriage_pass = carriage_pass
        super().__init__(f"Reordered knitting carriage pass will change float order", ignore_instructions=False)
