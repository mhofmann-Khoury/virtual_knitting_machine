"""A module containing warnings related to yarn carrier operations and hook management.
This module provides warning classes for carrier operation mismatches and hook state inconsistencies during yarn insertion and release operations on knitting machines."""
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    Yarn_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)


class Mismatched_Releasehook_Warning(Yarn_Carrier_Warning):
    """A warning for release hook operations that do not match the currently hooked carrier.
    This warning occurs when a release hook operation is requested for a carrier that is not currently connected to the insertion hook, and the system releases the actually hooked yarn instead."""

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        """Initialize a mismatched release hook warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID that was incorrectly requested for release hook operation.
        """
        super().__init__(carrier_id,
                         f"Requested Releasehook with {carrier_id} but that was not on hook. Releasing existing yarn",
                         ignore_instruction=False)
