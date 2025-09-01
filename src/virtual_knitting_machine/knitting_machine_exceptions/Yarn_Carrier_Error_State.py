"""Collection of exceptions for error states that involve yarn carriers and yarn management operations.
This module provides comprehensive exception classes for various yarn carrier issues including
hook conflicts, inactive carrier usage, yarn cutting errors, and carrier system modifications that would cause critical operational failures."""
from typing import TYPE_CHECKING, Any

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import (
    Knitting_Machine_Exception,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
        Yarn_Carrier,
    )


class Yarn_Carrier_Exception(Knitting_Machine_Exception):
    """Base class for exceptions related to yarn carrier operations and states.
    This class provides a foundation for all yarn carrier-specific exceptions and includes
    the carrier ID reference for detailed error reporting and debugging of carrier-related operational failures."""

    def __init__(self, carrier_id: Any, message: str) -> None:
        """Initialize a yarn carrier-specific exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID or carrier object involved in the exception condition.
            message (str): The descriptive error message about the carrier state or operation failure.
        """
        self.carrier_id: Yarn_Carrier | int = carrier_id
        super().__init__(message)


class Hooked_Carrier_Exception(Yarn_Carrier_Exception):
    """Exception for attempting hook operations on carriers that are already on the yarn inserting hook.
    This exception occurs when trying to perform an operation that requires the carrier to not be on the insertion hook,
    such as an outhook operation, when the carrier is currently connected to the hook."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize a hooked carrier operation exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that is already on the yarn inserting hook.
        """
        super().__init__(carrier_id, f"Cannot Hook {carrier_id} out because it is on the yarn inserting hook.")


class Blocked_by_Yarn_Inserting_Hook_Exception(Yarn_Carrier_Exception):
    def __init__(self, carrier_id: Any, slot: int) -> None:
        self._slot: int = slot
        super().__init__(carrier_id, f"Cannot use carrier {carrier_id} on needle slot {slot} because it is blocked by the yarn inserting hook.")


class Inserting_Hook_In_Use_Exception(Yarn_Carrier_Exception):
    """Exception for attempting to use the yarn inserting hook when it is already occupied by another carrier.
    This exception occurs when trying to perform hook operations while the insertion hook is already in use by a different carrier, preventing conflicts in hook operations."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize an inserting hook in use exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that attempted to use the already occupied insertion hook.
        """
        super().__init__(carrier_id, f"Cannot bring carrier {carrier_id} out because the yarn inserting hook is in use.")


class Use_Inactive_Carrier_Exception(Yarn_Carrier_Exception):
    """Exception for attempting to use carriers that are not in active state.
    This exception occurs when trying to perform knitting operations with a carrier that is not active (still on grippers or otherwise unavailable),
    which would result in no yarn being fed to the needles."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize an inactive carrier usage exception.

        Args:
            carrier_id (int | Yarn_Carrier): The inactive carrier that was attempted to be used.
        """
        super().__init__(carrier_id, f"Cannot use inactive yarn on carrier {carrier_id}.")


class Use_Cut_Yarn_Exception(Use_Inactive_Carrier_Exception):
    """Exception for attempting to use yarn that has been cut from its carrier.
    This exception occurs when trying to perform knitting operations with yarn that has been severed from its carrier,
    making it impossible to continue yarn operations as the yarn is no longer connected to the carrier system."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize a cut yarn usage exception.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID from which the cut yarn originated.
        """
        super().__init__(carrier_id)


class Change_Active_Yarn_Exception(Yarn_Carrier_Exception):
    """Exception for attempting to change yarn properties on carriers that are currently active.
    This exception occurs when trying to modify yarn properties or reassign yarn to a carrier that is actively being used for knitting operations, which could cause yarn consistency issues."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize a change active yarn exception.

        Args:
            carrier_id (int | Yarn_Carrier): The active carrier for which yarn change was attempted.
        """
        super().__init__(carrier_id, f"Cannot change active yarn on carrier {carrier_id}.")


class Change_Active_Carrier_System_Exception(Yarn_Carrier_Exception):
    """Exception for attempting to change the carrier system while carriers are active.
    This exception occurs when trying to modify the number of carriers or replace the carrier system while there are still active carriers in use,
    which would cause loss of active yarn states and system inconsistencies."""

    def __init__(self) -> None:
        """Initialize a change active carrier system exception."""
        super().__init__(-1, f"Cannot change active carrier system.")
