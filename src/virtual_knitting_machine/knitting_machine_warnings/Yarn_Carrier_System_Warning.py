"""A module containing warnings related to the yarn carrier system and yarn management operations.
This module provides comprehensive warning classes for various yarn carrier issues including
state mismatches, duplicate definitions, hook operation errors, and float length violations during machine knitting operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Specification

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State


class Yarn_Carrier_Warning(Knitting_Machine_Warning):
    """Base class for warnings related to yarn carrier operations and states.
    This class provides a foundation for all yarn carrier-specific warnings and includes the carrier ID reference for detailed error reporting and system state tracking.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State, message: str, ignore_instruction: bool = False) -> None:
        """Initialize a yarn carrier-specific warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier ID or carrier object involved in the warning condition.
            message (str): The descriptive warning message about the carrier state or operation.
            ignore_instruction (bool, optional): Whether this warning indicates that the operation should be ignored. Defaults to False.
        """
        self.carrier_id: Yarn_Carrier_State | int = carrier_id
        super().__init__(message, ignore_instruction)


class In_Active_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring in a carrier that is already active.
    This warning occurs when an 'in' operation is performed on a carrier that is already in active state, indicating redundant operations or state tracking issues.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize an 'in' active carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier that is already active but was requested to be brought in.
        """
        super().__init__(
            carrier_id, f"Tried to bring in {carrier_id} but it is already active", ignore_instruction=True
        )


class In_Loose_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring in a loose carrier without proper hook operations.
    This warning occurs when trying to bring in a carrier that has loose yarn, suggesting that an in-hook operation should be used instead for proper yarn management.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize an 'in' loose carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The loose carrier that was attempted to be brought in.
        """
        super().__init__(
            carrier_id,
            f"Tried to bring in {carrier_id} but carrier is loose. Try in-hooking {carrier_id}",
            ignore_instruction=False,
        )


class Out_Inactive_Carrier_Warning(Yarn_Carrier_Warning):
    """A warning for attempting to bring out a carrier that is not currently active.
    This warning occurs when an 'out' operation is performed on a carrier that is already inactive, indicating redundant operations or state tracking issues.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State) -> None:
        """Initialize an 'out' inactive carrier warning.

        Args:
            carrier_id (int | Yarn_Carrier): The inactive carrier that was requested to be brought out.
        """
        super().__init__(
            carrier_id, f"Cannot bring carrier {carrier_id} out because it is not active.", ignore_instruction=True
        )


class Duplicate_Carriers_In_Set(Yarn_Carrier_Warning):
    """A warning for duplicate carrier IDs found in carrier sets.
    This warning occurs when a carrier set is created with duplicate carrier IDs, and the system automatically removes the duplicates to maintain set integrity.
    """

    def __init__(self, carrier_id: int | Yarn_Carrier_State, carrier_set: list[int]) -> None:
        """Initialize a duplicate carriers in set warning.

        Args:
            carrier_id (int | Yarn_Carrier): The duplicate carrier ID that was removed.
            carrier_set (list[int]): The original carrier set containing duplicates.
        """
        self.carrier_set: list[int] = carrier_set
        super().__init__(
            carrier_id, f"Removed last duplicate {carrier_id} form {carrier_set}", ignore_instruction=False
        )


class Long_Float_Warning(Yarn_Carrier_Warning):
    """A warning for float segments that exceed the maximum allowed length.
    This warning occurs when yarn floats between needles exceed the specified maximum float length, which may cause knitting issues or affect fabric quality.
    """

    def __init__(
        self,
        carrier_id: int | Yarn_Carrier_State,
        prior_needle: Needle_Specification,
        next_needle: Needle_Specification,
        max_float_len: int,
    ) -> None:
        """Initialize a long float warning.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier creating the long float.
            prior_needle (Needle_Specification): The needle where the float begins.
            next_needle (Needle_Specification): The needle where the float ends.
            max_float_len (int): The maximum allowed float length that was exceeded.
        """
        self.prior_needle: Needle_Specification = prior_needle
        self.next_needle: Needle_Specification = next_needle
        self.max_float_len: int = max_float_len
        super().__init__(
            carrier_id,
            f"Long float greater than {self.max_float_len} formed between {self.prior_needle} and {self.next_needle}.",
            ignore_instruction=False,
        )
