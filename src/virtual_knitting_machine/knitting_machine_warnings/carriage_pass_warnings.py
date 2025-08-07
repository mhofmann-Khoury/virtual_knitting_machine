"""A Module containing warnings about carriage passes."""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class Reordered_Knitting_Pass_Warning(Knitting_Machine_Warning):

    def __init__(self, direction: Carriage_Pass_Direction, carriage_pass: Carriage_Pass):
        self.direction: Carriage_Pass_Direction = direction
        self.carriage_pass: Carriage_Pass = carriage_pass
        super().__init__(f"Reordered knitting carriage pass will change float order", ignore_instructions=False)
