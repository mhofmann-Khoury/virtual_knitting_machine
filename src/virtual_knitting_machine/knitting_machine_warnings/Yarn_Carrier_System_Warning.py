"""A module containing warnings related to the yarn carrier system and yarn management operations.
This module provides comprehensive warning classes for various yarn carrier issues including
state mismatches, duplicate definitions, hook operation errors, and float length violations during machine knitting operations."""
from typing import TYPE_CHECKING, Any

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    Knitting_Machine_Warning,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
        Yarn_Carrier,
    )


class Yarn_Carrier_Warning(Knitting_Machine_Warning):
    """Base class for warnings related to yarn carrier operations and states.
    This class provides a foundation for all yarn carrier-specific warnings and includes the carrier ID reference for detailed error reporting and system state tracking."""

    def __init__(self, carrier_id: Any, message: str, ignore_instruction: bool = False) -> None:
        """Initialize a yarn carrier-specific warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID or carrier object involved in the warning condition.
            message (str): The descriptive warning message about the carrier state or operation.
            ignore_instruction (bool, optional): Whether this warning indicates that the operation should be ignored. Defaults to False.
        """
        self.carrier_id: Yarn_Carrier | int = carrier_id
        super().__init__(message, ignore_instruction)


class Multiple_Yarn_Definitions_Warning(Yarn_Carrier_Warning):
    """A warning for multiple yarn property definitions on the same carrier.
    This warning occurs when yarn properties are defined multiple times for a single carrier, which may indicate conflicting yarn specifications or redundant operations."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize a multiple yarn definitions warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that has multiple yarn definitions.
        """
        super().__init__(carrier_id, f"Multiple definitions for yarn on carrier {carrier_id}", ignore_instruction=True)


class Release_Wrong_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for release hook operations targeting the wrong carrier.
    This warning occurs when attempting to release a carrier from the yarn inserting hook when that carrier is not currently hooked,
    providing information about which carrier is actually on the hook."""

    def __init__(self, carrier_id: Any, hooked_carrier_id: Any) -> None:
        """Initialize a wrong carrier release warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that was incorrectly requested for release.
            hooked_carrier_id (int | None | Yarn_Carrier): The carrier that is actually on the yarn inserting hook, or None if no carrier is hooked.
        """
        self.hooked_carrier_id: Yarn_Carrier | None | int = hooked_carrier_id
        current_carrier_statement = f"Carrier {self.hooked_carrier_id} is on Yarn-Inserting_Hook"
        if self.hooked_carrier_id is None:
            current_carrier_statement = f"No carrier is on the Yarn-Inserting Hook."
        super().__init__(carrier_id, f"Tried to release carrier {carrier_id} which is not on yarn-inserting hook.\n\t{current_carrier_statement}", ignore_instruction=True)


class Loose_Release_Warning(Yarn_Carrier_Warning):
    """A warning for releasing loose yarn carriers with mismatched loop counts.
    This warning occurs when a loose yarn release operation is performed with a different number of stabilizing loops than requested, indicating potential yarn state inconsistencies."""

    def __init__(self, carrier_id: Any, loops_before_release: int, loose_loop_count: int) -> None:
        """Initialize a loose release warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier being released with loose yarn.
            loops_before_release (int): The actual number of stabilizing loops before the release operation.
            loose_loop_count (int): The number of loose loops that were requested for the release.
        """
        self.loops_before_release: int = loops_before_release
        self.loose_loop_count: int = loose_loop_count
        super().__init__(carrier_id, f"Released loose yarn on carrier {carrier_id} with {loops_before_release} stabling loops but requested {loose_loop_count}.")


class Defined_Active_Yarn_Warning(Yarn_Carrier_Warning):
    """A warning for defining yarn properties on an already active carrier.
    This warning occurs when yarn properties are defined for a carrier that is already in active use, which may cause unexpected yarn behavior or state conflicts."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize a defined active yarn warning.

        Args:
            carrier_id (int | Yarn_Carrier): The active carrier for which yarn was being defined.
        """
        super().__init__(carrier_id, f"Defined active yarn on carrier {carrier_id}", ignore_instruction=True)


class In_Active_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring in a carrier that is already active.
    This warning occurs when an 'in' operation is performed on a carrier that is already in active state, indicating redundant operations or state tracking issues."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize an 'in' active carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that is already active but was requested to be brought in.
        """
        super().__init__(carrier_id, f"Tried to bring in {carrier_id} but it is already active", ignore_instruction=True)


class In_Loose_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring in a loose carrier without proper hook operations.
    This warning occurs when trying to bring in a carrier that has loose yarn, suggesting that an in-hook operation should be used instead for proper yarn management."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize an 'in' loose carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The loose carrier that was attempted to be brought in.
        """
        super().__init__(carrier_id, f"Tried to bring in {carrier_id} but carrier is loose. Try in-hooking {carrier_id}", ignore_instruction=False)


class Out_Inactive_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring out a carrier that is not currently active.
    This warning occurs when an 'out' operation is performed on a carrier that is already inactive, indicating redundant operations or state tracking issues."""

    def __init__(self, carrier_id: Any) -> None:
        """Initialize an 'out' inactive carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The inactive carrier that was requested to be brought out.
        """
        super().__init__(carrier_id, f"Cannot bring carrier {carrier_id} out because it is not active.", ignore_instruction=True)


class Duplicate_Carriers_In_Set(Yarn_Carrier_Warning):
    """A warning for duplicate carrier IDs found in carrier sets.
    This warning occurs when a carrier set is created with duplicate carrier IDs, and the system automatically removes the duplicates to maintain set integrity."""

    def __init__(self, carrier_id: Any, carrier_set: list[int]) -> None:
        """Initialize a duplicate carriers in set warning.

        Args:
            carrier_id (int | Yarn_Carrier): The duplicate carrier ID that was removed.
            carrier_set (list[int]): The original carrier set containing duplicates.
        """
        self.carrier_set: list[int] = carrier_set
        super().__init__(carrier_id, f"Removed last duplicate {carrier_id} form {carrier_set}", ignore_instruction=False)


class Long_Float_Warning(Yarn_Carrier_Warning):
    """A warning for float segments that exceed the maximum allowed length.
    This warning occurs when yarn floats between needles exceed the specified maximum float length, which may cause knitting issues or affect fabric quality."""

    def __init__(self, carrier_id: Any, prior_needle: Needle, next_needle: Needle, max_float_len: int) -> None:
        """Initialize a long float warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier creating the long float.
            prior_needle (Needle): The needle where the float begins.
            next_needle (Needle): The needle where the float ends.
            max_float_len (int): The maximum allowed float length that was exceeded.
        """
        self.prior_needle: Needle = prior_needle
        self.next_needle: Needle = next_needle
        self.max_float_len: int = max_float_len
        super().__init__(carrier_id, f"Long float greater than {self.max_float_len} formed between {self.prior_needle} and {self.next_needle}.", ignore_instruction=False)
