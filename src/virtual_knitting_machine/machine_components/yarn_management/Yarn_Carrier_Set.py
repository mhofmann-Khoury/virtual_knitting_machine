"""Representation module for yarn carrier sets on knitting machines.
This module provides the Yarn_Carrier_Set class which represents a collection of yarn carriers that can be operated together in knitting operations.
It manages multiple carriers as a single unit for positioning and operations."""

from __future__ import annotations

import warnings
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, overload

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Duplicate_Carriers_In_Set
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import (
        Yarn_Insertion_System,
        Yarn_Insertion_System_State,
    )


class Yarn_Carrier_Set(Sequence[int]):
    """A structure to represent a collection of yarn carriers that operate together as a single unit.
    This class manages multiple carriers for coordinated operations, positioning, and state management.
    It provides methods for accessing carrier positions, managing duplicates, and converting to various representation formats.
    """

    def __init__(
        self,
        carrier_ids: (
            Sequence[int | Yarn_Carrier_State] | Sequence[int] | Sequence[Yarn_Carrier_State] | int | Yarn_Carrier_State
        ),
    ) -> None:
        """Initialize a yarn carrier set with one or more carrier identifiers.

        Args:
            carrier_ids (Sequence[int | Yarn_Carrier_State] | int | Yarn_Carrier_State): The carrier IDs for this yarn carrier set, can be a single carrier or list of carriers.

        Warns:
            Duplicate_Carriers_In_Set: If duplicate carrier IDs are found in the input list.
        """
        if isinstance(carrier_ids, Sequence):
            int_carrier_ids: list[int] = [int(cid) for cid in carrier_ids]
            duplicates = set()
            self._carrier_ids: list[int] = []
            for c in int_carrier_ids:
                if c in duplicates:
                    warnings.warn(
                        Duplicate_Carriers_In_Set(c, int_carrier_ids),
                        stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
                    )
                else:
                    duplicates.add(c)
                    self._carrier_ids.append(c)
        else:
            self._carrier_ids: list[int] = [int(carrier_ids)]

    def get_carriers(self, carrier_system: Yarn_Insertion_System_State) -> list[Yarn_Carrier_State]:
        """Get the actual carrier objects that correspond to the IDs in this carrier set.

        Args:
            carrier_system (Yarn_Insertion_System): Carrier system referenced by set.

        Returns:
            list[Yarn_Carrier]: Carriers that correspond to the ids in the carrier set.
        """
        carriers = carrier_system[self]
        return carriers

    def position_carriers_at_needle(
        self,
        carrier_system: Yarn_Insertion_System,
        needle: Needle | None,
        direction: Carriage_Pass_Direction | None = None,
    ) -> None:
        """Set the position of all involved carriers to the given position.

        Args:
            carrier_system (Yarn_Insertion_System): Carrier system referenced by set.
            needle (int | None): The needle to move the carrier set to, if None this means the carrier is not active.
            direction (Carriage_Pass_Direction, optional): The direction of the carrier movement. If this is not provided, the direction will be inferred.
        """
        for cid in self:
            carrier_system.position_carrier_at_needle(cid, needle, direction)

    @property
    def carrier_ids(self) -> list[int]:
        """Get the list of carrier IDs in this set.

        Returns:
            list[int]: The ID list of this carrier set.
        """
        return self._carrier_ids

    @property
    def many_carriers(self) -> bool:
        """Check if this carrier set involves multiple carriers.

        Returns:
            bool: True if this carrier set involves multiple carriers, False if single carrier.
        """
        return len(self.carrier_ids) > 1

    def __str__(self) -> str:
        """Return string representation of the carrier set.

        Returns:
            str: String representation showing all carrier IDs separated by spaces.
        """
        carriers = str(self.carrier_ids[0])
        for cid in self.carrier_ids[1:]:
            carriers += f" {cid}"
        return carriers

    def __hash__(self) -> int:
        """Return hash value for the carrier set.

        Returns:
            int: Hash value based on single carrier ID or string representation for multiple carriers.
        """
        if len(self.carrier_ids) == 1:
            return self.carrier_ids[0]
        else:
            return hash(str(self))

    def __repr__(self) -> str:
        """Return string representation of the carrier set.

        Returns:
            str: String representation of the carrier set.
        """
        return str(self)

    def __eq__(self, other: object) -> bool:
        """Check equality with another carrier set, carrier, or list of carriers.

        Args:
            other (None | Yarn_Carrier | int | list[Yarn_Carrier | int] | Yarn_Carrier_Set): The object to compare with.

        Returns:
            bool: True if the carrier sets contain the same carrier IDs, False otherwise.
        """
        if other is None:
            return False
        elif isinstance(other, (Yarn_Carrier_State, int)):
            if len(self.carrier_ids) != 1:
                return False
            return self.carrier_ids[0] == int(other)
        elif isinstance(other, (list, Yarn_Carrier_Set)):
            if len(self) != len(other):
                return False
            return not any(c != int(other_c) for c, other_c in zip(self, other, strict=False))
        else:
            return False

    def __iter__(self) -> Iterator[int]:
        """Iterate over the carrier IDs in this set.

        Returns:
            Iterator[int]: Iterator over carrier IDs.
        """
        return iter(self.carrier_ids)

    @overload
    def __getitem__(self, index: int) -> int: ...

    @overload
    def __getitem__(self, index: slice) -> list[int]: ...

    def __getitem__(self, item: int | slice) -> int | list[int]:
        """Get carrier ID(s) by index or slice.

        Args:
            item (int | slice | Yarn_Carrier): Index, slice, or carrier to get ID for.

        Returns:
            int | list[int]: Carrier ID or list of carrier IDs.
        """
        return self.carrier_ids[item]

    def __len__(self) -> int:
        """Get the number of carriers in this set.

        Returns:
            int: Number of carriers in the set.
        """
        return len(self.carrier_ids)

    def __contains__(self, carrier_id: object) -> bool:
        """Check if a carrier ID is contained in this set.

        Args:
            carrier_id (int | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State]): Carrier ID to check for membership. If a sequence is provided, all members are checked for.

        Returns:
            bool: True if carrier ID(s) is in this set, False otherwise.
        """
        if isinstance(carrier_id, Sequence):
            return all(c in self for c in carrier_id)
        elif isinstance(carrier_id, (int, Yarn_Carrier_State)):
            return int(carrier_id) in self.carrier_ids
        else:
            return False

    def carrier_DAT_ID(self) -> int:
        """Generate a number used in DAT files to represent the carrier set.

        Returns:
            int: Number used in DAT files to represent the carrier set.
        """
        carrier_id = 0
        for place, carrier in enumerate(reversed(self.carrier_ids)):
            multiplier = 10**place
            carrier_val = multiplier * carrier
            carrier_id += carrier_val
        return carrier_id
