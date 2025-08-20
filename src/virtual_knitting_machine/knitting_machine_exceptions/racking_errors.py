"""Module containing exceptions raised that involve racking operations and constraints.
This module provides exception classes for racking-related critical errors including attempts to exceed the machine's maximum racking capabilities,
which would cause physical damage or operational failures on real knitting machines."""

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import (
    Knitting_Machine_Exception,
)


class Max_Rack_Exception(Knitting_Machine_Exception):
    """Exception for racking operations that exceed the machine's maximum racking capability.
    This exception occurs when attempting to set a racking value that exceeds the physical limitations of the knitting machine,
    preventing potential mechanical damage and ensuring operation within safe parameters."""

    def __init__(self, racking: float, max_rack: float) -> None:
        """Initialize a maximum rack exceeded exception.

        Args:
            racking (float): The requested racking value that exceeded the maximum.
            max_rack (float): The maximum allowed racking value for this machine.
        """
        self.max_rack: float = max_rack
        self.racking: float = racking
        super().__init__(f"Cannot perform racking of {racking}. Max rack allowed is {max_rack}")
