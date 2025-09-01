"""A module containing Yarn Insertion System classes for managing yarn carriers on knitting machines.
This module provides the Yarn_Insertion_System class which manages the complete yarn carrier system including
carrier states, insertion hook operations, position tracking, and loop creation operations."""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, cast

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Blocked_by_Yarn_Inserting_Hook_Exception,
    Hooked_Carrier_Exception,
    Inserting_Hook_In_Use_Exception,
    Use_Inactive_Carrier_Exception,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    In_Loose_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine


class Yarn_Insertion_System:
    """A class for managing the complete state of the yarn insertion system including all yarn carriers on the knitting machine.
    This system handles carrier positioning, activation states, insertion hook operations, and coordinates loop creation across multiple carriers.
    It provides comprehensive management of yarn carrier operations including bring-in, hook operations, and float management.

    Attributes:
        knitting_machine (Knitting_Machine): The knitting machine this system belongs to.
        carriers (list[Yarn_Carrier]): The list of yarn carriers in this insertion system. The carriers are ordered from 1 to the number of carriers in the system.
    """

    def __init__(self, knitting_machine: Knitting_Machine, carrier_count: int = 10) -> None:
        """Initialize the yarn insertion system with specified number of carriers.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine this system belongs to.
            carrier_count (int, optional): Number of yarn carriers to create. Defaults to 10.
        """
        self.knitting_machine: Knitting_Machine = knitting_machine
        self.carriers: list[Yarn_Carrier] = [Yarn_Carrier(i, knit_graph=self.knitting_machine.knit_graph) for i in range(1, carrier_count + 1)]
        self._hook_position: None | int = None
        self._hook_input_direction: None | Carriage_Pass_Direction = None
        self._searching_for_position: bool = False
        self._hooked_carrier: Yarn_Carrier | None = None

    @property
    def hook_input_direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            None | Carriage_Pass_Direction: The direction that the carrier was moving when the yarn-inserting hook was use. None if the yarn-inserting hook is not active.
        """
        return self._hook_input_direction

    @hook_input_direction.setter
    def hook_input_direction(self, direction: Carriage_Pass_Direction | None) -> None:
        """
        Sets the direction of movement for the yarn-inserting hook.
        Args:
            direction (Carriage_Pass_Direction | None): The direction of the yarn-inserting hook's motion or None if the hook is being released.

        Raises:
             ValueError: If the direction is Rightward. The direction must be a Leftward direction.
        """
        if direction is None:
            self._hook_input_direction = None
        elif direction is Carriage_Pass_Direction.Rightward:
            raise ValueError("Yarn Inserting Hook must start in a leftward direction")
        else:
            self._hook_input_direction = direction

    @property
    def hooked_carrier(self) -> Yarn_Carrier | None:
        """
        Returns:
            (Yarn_Carrier | None): The yarn-carrier currently on the yarn-inserting-hook or None if the hook is not active.
        """
        return self._hooked_carrier

    @property
    def searching_for_position(self) -> bool:
        """Check if the inserting hook is active but at an undefined position.

        Returns:
            bool: True if the inserting hook is active but at an undefined position, False otherwise.
        """
        if self.inserting_hook_available:
            return False
        return self._searching_for_position

    @property
    def carrier_ids(self) -> list[int]:
        """Get list of all carrier IDs in the carrier system.

        Returns:
            list[int]: List of carrier ids in the carrier system.
        """
        return [int(c) for c in self.carriers]

    def position_carrier(self, carrier_id: int | Yarn_Carrier, position: int | Needle | None, direction: Carriage_Pass_Direction | None = None) -> None:
        """Update the position of a specific carrier.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier to update.
            position (int | Needle | None): The position of the carrier.
            direction (Carriage_Pass_Direction, optional): The direction of the carrier movement. If this is not provided, the direction will be inferred.
        """
        carrier = self[carrier_id]
        assert isinstance(carrier, Yarn_Carrier)
        if position is not None:
            if self.conflicts_with_inserting_hook(position):
                raise Blocked_by_Yarn_Inserting_Hook_Exception(carrier, int(position))
        carrier.position = position
        if direction is not None:
            carrier.last_direction = direction

    @property
    def inserting_hook_available(self) -> bool:
        """Check if the yarn inserting hook can be used.

        Returns:
            bool: True if the yarn inserting hook can be used, False if in use.
        """
        return self.hooked_carrier is None

    @property
    def active_carriers(self) -> set[Yarn_Carrier]:
        """Get set of carriers that are currently active (off the grippers).

        Returns:
            set[Yarn_Carrier]: Set of carriers that are currently active (off the grippers).
        """
        return {c for c in self.carriers if c.is_active}

    def conflicts_with_inserting_hook(self, needle_position: Needle | int | None) -> bool:
        """Check if a needle position conflicts with the inserting hook position.

        Args:
            needle_position (Needle | int | None): The needle position to check for compliance, or None if the position is moving a carrier off the machine.

        Returns:
            bool: True if inserting hook conflicts with a needle slot because the slot is to the right of the hook's current position. False otherwise.
        """
        if needle_position is None or self.inserting_hook_available:
            return False  # Non-position does not conflict with yarn-inserting hook.
        assert isinstance(self._hook_position, int)
        return bool(self._hook_position <= int(needle_position))

    def missing_carriers(self, carrier_ids: list[int | Yarn_Carrier]) -> list[int]:
        """Get list of carrier IDs that are not currently active.

        Args:
            carrier_ids (list[int | Yarn_Carrier]): The carrier set to check for the inactive carriers.

        Returns:
            list[int]: List of carrier ids that are not active (i.e., on grippers).
        """
        return [cid for cid in carrier_ids if not cast(Yarn_Carrier, self[cid]).is_active]

    def is_active(self, carrier_ids: list[int | Yarn_Carrier]) -> bool:
        """Check if all carriers in the given set are active (not on the gripper).

        Args:
            carrier_ids (list[int | Yarn_Carrier]): List of carrier IDs to check.

        Returns:
            bool: True if all carriers in set are active (not-on the gripper), Note: If an empty list of carriers is given, this will return true because the empty set is active.
        """
        if len(carrier_ids) == 0:
            return True  # No ids given, so the null set is active
        return len(self.missing_carriers(carrier_ids)) == 0

    def yarn_is_loose(self, carrier_id: int | Yarn_Carrier) -> bool:
        """Check if yarn in carrier is loose (not on the inserting hook or tuck/knit on bed).

        Args:
            carrier_id (int | Yarn_Carrier): The carrier to check for loose yarn.

        Returns:
            bool: True if any yarn in yarn carrier set is loose (not on the inserting hook or tuck/knit on bed), False otherwise.
        """
        return cast(Yarn_Carrier, self[carrier_id]).yarn.last_needle() is None

    def bring_in(self, carrier_id: int | Yarn_Carrier) -> None:
        """Bring in a yarn carrier without insertion hook (tail to gripper), yarn is considered loose until knit.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to bring in.

        Warns:
            In_Active_Carrier_Warning: If carrier is already active.
            In_Loose_Carrier_Warning: If carrier yarn is loose (not connected).
        """
        carrier = self[carrier_id]
        assert isinstance(carrier, Yarn_Carrier)
        if carrier.is_active:
            warnings.warn(In_Active_Carrier_Warning(carrier_id))
        if carrier.yarn.last_needle() is None:
            warnings.warn(In_Loose_Carrier_Warning(carrier_id))
        carrier.bring_in()

    def inhook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Bring a yarn in with insertion hook, yarn is not loose after this operation.

        Args:
            carrier_id (int | Yarn_Carrier): Carriers to bring in by id.

        Raises:
            Inserting_Hook_In_Use_Exception: If insertion hook is already in use by another carrier.

        Warns:
            In_Active_Carrier_Warning: If carrier is already active.
        """

        carrier = self[carrier_id]
        assert isinstance(carrier, Yarn_Carrier)
        if carrier.is_active:
            warnings.warn(In_Active_Carrier_Warning(carrier_id))
        if not self.inserting_hook_available and self.hooked_carrier != carrier:
            raise Inserting_Hook_In_Use_Exception(carrier_id)
        self._hooked_carrier = carrier
        self._searching_for_position = True
        self._hook_position = None
        assert isinstance(self.hooked_carrier, Yarn_Carrier)
        self.hooked_carrier.inhook()

    def releasehook(self) -> None:
        """Release the yarn inserting hook from whatever carrier is currently using it."""
        if isinstance(self.hooked_carrier, Yarn_Carrier):
            self.hooked_carrier.releasehook()
        self._hooked_carrier = None
        self._searching_for_position = False
        self._hook_position = None
        self.hook_input_direction = None

    def out(self, carrier_id: int | Yarn_Carrier) -> None:
        """Move carrier to gripper, removing it from action but does not cut it loose.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to move out.

        Raises:
            Hooked_Carrier_Exception: If carrier is currently connected to insertion hook.

        Warns:
            Out_Inactive_Carrier_Warning: If carrier is already inactive.
        """
        carrier = self[carrier_id]
        assert isinstance(carrier, Yarn_Carrier)
        if not carrier.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(carrier_id))
        if carrier.is_hooked:
            raise Hooked_Carrier_Exception(carrier_id)
        carrier.out()

    def outhook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Cut carrier yarn and move it to grippers with insertion hook, the carrier will no longer be active and is now loose.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to cut and move out.

        Raises:
            Inserting_Hook_In_Use_Exception: If insertion hook is not available.
            Hooked_Carrier_Exception: If carrier is already connected to insertion hook.

        Warns:
            Out_Inactive_Carrier_Warning: If carrier is already inactive.
        """
        carrier = self[carrier_id]
        assert isinstance(carrier, Yarn_Carrier)
        if not carrier.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(carrier_id))
        if not self.inserting_hook_available:
            Inserting_Hook_In_Use_Exception(carrier_id)
        if carrier.is_hooked:
            raise Hooked_Carrier_Exception(carrier_id)
        carrier.outhook()

    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """Get dictionary of all active floats from all carriers in the system.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]: Dictionary of loops that are active keyed to active yarn-wise neighbors,
            each key-value pair represents a directed float where k comes before v on the yarns in the system.
        """
        active_floats = {}
        for carrier in self.carriers:
            active_floats.update(carrier.yarn.active_floats())
        return active_floats

    def make_loops(self, carrier_ids: list[int | Yarn_Carrier] | Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> list[Machine_Knit_Loop]:
        """Create loops using specified carriers on a needle, handling insertion hook positioning and float management.

        Args:
            carrier_ids (list[int | Yarn_Carrier] | Yarn_Carrier_Set): The carriers to make the loops with on this needle.
            needle (Needle): The needle to make the loops on.
            direction (Carriage_Pass_Direction): The carriage direction for this operation.

        Returns:
            list[Machine_Knit_Loop]: The set of loops made on this machine.

        Raises:
            Use_Inactive_Carrier_Exception: If attempting to use an inactive carrier for loop creation.
        """
        needle = self.knitting_machine[needle]
        assert isinstance(needle, Needle)
        if self.searching_for_position:  # mark inserting hook position
            self._hook_position = needle.position + 1  # Position yarn inserting hook at the needle slot to the right of the needle.
            self.hook_input_direction = direction
            self._searching_for_position = False
            self.knitting_machine.carriage.move_to(self._hook_position)
        loops: list[Machine_Knit_Loop] = []
        for cid in carrier_ids:
            carrier = self[cid]
            assert isinstance(carrier, Yarn_Carrier)
            if not carrier.is_active:
                raise Use_Inactive_Carrier_Exception(cid)
            float_source_needle = carrier.yarn.last_needle()
            loop = carrier.yarn.make_loop_on_needle(holding_needle=needle, max_float_length=self.knitting_machine.machine_specification.maximum_float)
            if float_source_needle is not None:
                float_source_needle = self.knitting_machine[float_source_needle]
                float_start = min(float_source_needle.position, needle.position)
                float_end = max(float_source_needle.position, needle.position)
                front_floated_needles = [f for f in self.knitting_machine.front_bed[float_start: float_end + 1]
                                         if f != float_source_needle and f != needle]
                back_floated_needles = [b for b in self.knitting_machine.back_bed[float_start: float_end + 1]
                                        if b != float_source_needle and b != needle]
                for float_source_loop in float_source_needle.held_loops:
                    for fn in front_floated_needles:
                        for fl in fn.held_loops:
                            carrier.yarn.add_loop_in_front_of_float(fl, float_source_loop, loop)
                    for bn in back_floated_needles:
                        for bl in bn.held_loops:
                            carrier.yarn.add_loop_behind_float(bl, float_source_loop, loop)
            loops.append(loop)
        return loops

    def __getitem__(self, item: int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]) -> Yarn_Carrier | list[Yarn_Carrier]:
        """Get carrier(s) by ID, carrier object, carrier set, or list of IDs/carriers.

        Args:
            item (int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]): The identifier(s) for the carrier(s) to retrieve.

        Returns:
            Yarn_Carrier | list[Yarn_Carrier]: Single carrier or list of carriers corresponding to the input.

        Raises:
            KeyError: If invalid carrier ID is provided or carrier index is out of range.
        """
        try:
            if isinstance(item, Yarn_Carrier):
                return self[item.carrier_id]
            elif isinstance(item, Yarn_Carrier_Set):
                return self[item.carrier_ids]
            elif isinstance(item, list):
                if len(item) == 1:
                    return self[item[0]]
                else:
                    return [self[i] for i in item]
        except KeyError:
            raise KeyError(f"Invalid carrier: {item}. Carriers range from 1 to {len(self.carriers)}")
        assert isinstance(item, int)
        if item < 1 or item > len(self.carriers):
            raise KeyError(f"Invalid carrier index {item}")
        return self.carriers[item - 1]  # Carriers are given from values starting at 1 but indexed in the list starting at zero
