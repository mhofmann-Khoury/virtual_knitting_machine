"""Module containing the base class for knitting machine exceptions.
This module provides the foundational exception class that all knitting machine-specific exceptions inherit from,
standardizing error message formatting and handling behavior across the virtual knitting machine system for critical error states."""

from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation


class Knitting_Machine_Exception(Exception):
    """Superclass for all exceptions that would put the virtual knitting machine in an error state.
    This class provides standardized exception message formatting and serves as the base for all
    machine-specific exceptions that indicate critical operational failures requiring immediate attention and program termination.
    """

    def __init__(self, message: str, violation: Violation = Violation.Machine_State_Violation) -> None:
        """Initialize a knitting machine exception with formatted message.

        Args:
            message (str): The descriptive error message about the machine state or operation failure.
            violation (Violation, optional): The type of violation that caused the exception. Defaults to Violation.Machine_State_Violation.
        """
        self.message = f"{self.__class__.__name__}: {message}"
        self.violation: Violation = violation
        super().__init__(self.message)
