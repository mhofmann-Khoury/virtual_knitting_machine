"""A module containing warnings about carriage passes and their potential impact on knitting operations.
This module provides warning classes for carriage pass reordering issues that may affect float ordering and knitting structure during machine operations."""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class Reordered_Knitting_Pass_Warning(Knitting_Machine_Warning):
    """A warning for carriage passes that have been reordered and may change float ordering.
    This warning indicates that the knitting carriage pass has been reordered from its original sequence, which may affect the final float structure and knitting outcome."""

    def __init__(self, direction: Carriage_Pass_Direction, carriage_pass: Carriage_Pass) -> None:
        """Initialize a reordered knitting pass warning.

        Args:
            direction (Carriage_Pass_Direction): The direction of the reordered carriage pass.
            carriage_pass (Carriage_Pass): The carriage pass that has been reordered.
        """
        self.direction: Carriage_Pass_Direction = direction
        self.carriage_pass: Carriage_Pass = carriage_pass
        super().__init__(f"Reordered knitting carriage pass will change float order", ignore_instructions=False)
