"""Collection of exceptions for error states that involve yarn carriers and yarn management operations.
This module provides comprehensive exception classes for various yarn carrier issues including
hook conflicts, inactive carrier usage, yarn cutting errors, and carrier system modifications that would cause critical operational failures."""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State


class Yarn_Carrier_Exception(Knitting_Machine_Exception):
    """Base class for exceptions related to yarn carrier operations and states.
    This class provides a foundation for all yarn carrier-specific exceptions and includes
    the carrier ID reference for detailed error reporting and debugging of carrier-related operational failures."""

    def __init__(
        self,
        carrier_id: int | Yarn_Carrier_State,
        message: str,
        violation: Violation = Violation.YARN_CARRIER_VIOLATION,
    ) -> None:
        """Initialize a yarn carrier-specific exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID or carrier object involved in the exception condition.
            message (str): The descriptive error message about the carrier state or operation failure.
            violation (Violation, optional): The type of violation associated with this error. Defaults to Violation.YARN_CARRIER_VIOLATION.
        """
        self.carrier_id: Yarn_Carrier_State | int = carrier_id
        super().__init__(message, violation=violation)


class Hooked_Carrier_Exception(Yarn_Carrier_Exception):
    """Exception for attempting hook operations on carriers that are already on the yarn inserting hook.
    This exception occurs when trying to perform an operation that requires the carrier to not be on the insertion hook,
    such as an outhook operation, when the carrier is currently connected to the hook."""

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize a hooked carrier operation exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that is already on the yarn inserting hook.
        """
        super().__init__(
            carrier_id,
            f"Cannot Hook {carrier_id} out because it is on the yarn inserting hook.",
            violation=Violation.HOOKED_CARRIER,
        )


class Blocked_by_Yarn_Inserting_Hook_Exception(Yarn_Carrier_Exception):
    def __init__(self, hooked_carrier_id: int | Yarn_Carrier_State, needle: Needle) -> None:
        super().__init__(
            hooked_carrier_id,
            f"Cannot use {needle} because it is blocked by the yarn inserting hook holding carrier {hooked_carrier_id}.",
            violation=Violation.BlOCKED_BY_HOOK,
        )


class Inserting_Hook_In_Use_Exception(Yarn_Carrier_Exception, ValueError):
    """Exception for attempting to use the yarn inserting hook when it is already occupied by another carrier.
    This exception occurs when trying to perform hook operations while the insertion hook is already in use by a different carrier, preventing conflicts in hook operations.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize an inserting hook in use exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that attempted to use the already occupied insertion hook.
        """
        super().__init__(
            carrier_id,
            f"Cannot bring carrier {carrier_id} out because the yarn inserting hook is in use.",
            violation=Violation.INSERTING_HOOK_IN_USE,
        )


class Use_Inactive_Carrier_Exception(Yarn_Carrier_Exception):
    """Exception for attempting to use carriers that are not in active state.
    This exception occurs when trying to perform knitting operations with a carrier that is not active (still on grippers or otherwise unavailable),
    which would result in no yarn being fed to the needles."""

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize an inactive carrier usage exception.

        Args:
            carrier_id (int | Yarn_Carrier): The inactive carrier that was attempted to be used.
        """
        super().__init__(
            carrier_id, f"Cannot use inactive yarn on carrier {carrier_id}.", violation=Violation.INACTIVE_CARRIER
        )
