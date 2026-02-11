"""
    A module containing Yarn Insertion System classes for managing yarn carriers on knitting machines.
    This module provides the Yarn_Insertion_System class which manages the complete yarn carrier system including carrier states,
    insertion hook operations, position tracking, and loop creation operations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, overload

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Blocked_by_Yarn_Inserting_Hook_Exception,
    Hooked_Carrier_Exception,
    Inserting_Hook_In_Use_Exception,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.machine_component_protocol import Machine_Component
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier, Yarn_Carrier_State
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import checked_operation
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)
Carrier_State_Type = TypeVar("Carrier_State_Type", bound="Yarn_Carrier_State")


class Yarn_Insertion_System_State(Machine_Component, Protocol[Machine_LoopT, Carrier_State_Type]):
    """
    A protocol for the readable elements of a yarn-insertion system.
    """

    @property
    def carriers(self) -> list[Carrier_State_Type]:
        """
        Returns:
            list[Yarn_Carrier_State]: The list of yarn carriers in this insertion system. The carriers are ordered from 1 to the number of carriers in the system.
        """
        ...

    @property
    def hook_position(self) -> int | None:
        """
        Returns:
            None | int: The needle slot of the yarn-insertion hook or None if the yarn-insertion hook is not active.

        Notes:
            The hook position will be None if its exact position is to the right of the edge of the knitting machine bed.
        """
        ...

    @property
    def hook_input_direction(self) -> Carriage_Pass_Direction | None:
        """
        Returns:
            Carriage_Pass_Direction | None: The direction that the carrier was moving when the yarn-inserting hook was use. None if the yarn-inserting hook is not active.
        """
        ...

    @property
    def hooked_carrier(self) -> Carrier_State_Type | None:
        """
        Returns:
            (Yarn_Carrier_State | None): The yarn-carrier currently on the yarn-inserting-hook or None if the hook is not active.
        """
        ...

    @property
    def searching_for_position(self) -> bool:
        """Check if the inserting hook is active but at an undefined position.

        Returns:
            bool: True if the inserting hook is active but at an undefined position, False otherwise.
        """
        ...

    @property
    def carrier_ids(self) -> list[int]:
        """Get list of all carrier IDs in the carrier system.

        Returns:
            list[int]: List of carrier ids in the carrier system.
        """
        return [int(c) for c in self.carriers]

    @property
    def inserting_hook_available(self) -> bool:
        """Check if the yarn inserting hook can be used.

        Returns:
            bool: True if the yarn inserting hook can be used, False if in use.
        """
        return self.hooked_carrier is None

    @property
    def active_carriers(self) -> set[Carrier_State_Type]:
        """
        Returns:
            set[Yarn_Carrier_State]: Set of carriers that are currently active (off the grippers).
        """
        return {c for c in self.carriers if c.is_active}

    @property
    def active_floats(self) -> dict[Machine_LoopT, Machine_LoopT]:
        """Get dictionary of all active floats from all carriers in the system.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]:
                Dictionary of loops that are active keyed to active yarn-wise neighbors, each key-value pair represents a directed float where k comes before v on the yarns in the system.
        """
        active_floats = {}
        for carrier in self.carriers:
            active_floats.update(carrier.yarn.active_floats())
        return active_floats

    def conflicts_with_inserting_hook(self, needle: Needle) -> bool:
        """Check if a needle position conflicts with the inserting hook position.

        Args:
            needle (Needle): The needle-position to check for compliance.

        Returns:
            bool: True if inserting hook conflicts with a needle slot because the slot is to the right of the hook's current position. False otherwise.
        """
        if self.hook_position is None:
            return False
        return self.hook_position <= needle.slot_number

    def missing_carriers(
        self, carrier_ids: Sequence[int | Yarn_Carrier_State] | Sequence[int] | Sequence[Yarn_Carrier_State]
    ) -> list[int]:
        """
        Args:
            carrier_ids (Sequence[int | Yarn_Carrier_State]): The carrier set to check for the inactive carriers.

        Returns:
            list[int]: List of carrier ids that are not active (i.e., on grippers).
        """
        return [int(cid) for cid in carrier_ids if not self[cid].is_active]

    def is_active(
        self, carrier_ids: Sequence[int | Yarn_Carrier_State] | Sequence[int] | Sequence[Yarn_Carrier_State]
    ) -> bool:
        """Check if all carriers in the given set are active (not on the gripper).

        Args:
            carrier_ids (Sequence[int | Yarn_Carrier_State]): List of carrier IDs to check.

        Returns:
            bool: True if all carriers in set are active (not-on the gripper), Note: If an empty list of carriers is given, this will return true because the empty set is active.
        """
        if len(carrier_ids) == 0:
            return True  # No ids given, so the null set is active
        return len(self.missing_carriers(carrier_ids)) == 0

    def yarn_is_loose(self, carrier_id: int | Yarn_Carrier_State) -> bool:
        """
        Args:
            carrier_id (int | Yarn_Carrier_State): The carrier to check for loose yarn.

        Returns:
            bool: True if any yarn in yarn carrier set is loose (not on the inserting hook or tuck/knit on bed), False otherwise.
        """
        return self[carrier_id].yarn.last_needle is None

    def __contains__(
        self,
        item: (
            int | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State] | Sequence[Yarn_Carrier_State] | Sequence[int]
        ),
    ) -> bool:
        """

        Args:
            item (int | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State]): The carrier, carrier id, or sequence of carriers to search for in carriers in this yarn insertion system.

        Returns:
            bool: True if all the given carriers are in the yarn insertion system. False otherwise.
        """
        if isinstance(item, (int, Yarn_Carrier_State)):
            return int(item) in self.carrier_ids
        else:
            return all(int(elem) in self.carrier_ids for elem in item)

    @overload
    def __getitem__(self, item: int | Yarn_Carrier_State) -> Carrier_State_Type: ...

    @overload
    def __getitem__(
        self, item: slice | Sequence[int | Yarn_Carrier_State] | Sequence[Yarn_Carrier_State] | Sequence[int]
    ) -> list[Carrier_State_Type]: ...

    def __getitem__(
        self,
        item: (
            int
            | Yarn_Carrier_State
            | slice
            | Sequence[int | Yarn_Carrier_State]
            | Sequence[Yarn_Carrier_State]
            | Sequence[int]
        ),
    ) -> Carrier_State_Type | list[Carrier_State_Type]:
        """Get carrier(s) by ID, carrier object, carrier set, or list of IDs/carriers.

        Args:
            item (int | Yarn_Carrier | slice | Sequence[int | Yarn_Carrier]): The identifier(s) for the carrier(s) to retrieve.

        Returns:
            Yarn_Carrier | list[Yarn_Carrier]: Single carrier or list of carriers corresponding to the input.

        Raises:
            KeyError: If invalid carrier ID is provided or carrier index is out of range.
        """
        if isinstance(item, int):
            if item < 1 or item > len(self.carriers):
                raise KeyError(f"Invalid carrier: {item}. Carriers range from 1 to {len(self.carriers)}")
            # Carriers are given from values starting at 1 but indexed in the list starting at zero
            return self.carriers[item - 1]
        elif isinstance(item, Yarn_Carrier_State):
            return self[item.carrier_id]
        elif isinstance(item, slice):
            return self.carriers[item]
        else:
            return [self[i] for i in item]

    def __len__(self) -> int:
        return len(self.carriers)


class Yarn_Insertion_System(Yarn_Insertion_System_State[Machine_LoopT, Yarn_Carrier[Machine_LoopT]]):
    """A class for managing the complete state of the yarn insertion system including all yarn carriers on the knitting machine.
    This system handles carrier positioning, activation states, insertion hook operations, and coordinates loop creation across multiple carriers.
    It provides comprehensive management of yarn carrier operations including bring-in, hook operations, and float management.

    """

    def __init__(self, knitting_machine: Knitting_Machine[Machine_LoopT], carrier_count: int = 10) -> None:
        """Initialize the yarn insertion system with specified number of carriers.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine this system belongs to.
            carrier_count (int, optional): Number of yarn carriers to create. Defaults to 10.
        """
        self._knitting_machine: Knitting_Machine[Machine_LoopT] = knitting_machine
        self._carriers: list[Yarn_Carrier[Machine_LoopT]] = [
            Yarn_Carrier[Machine_LoopT](i, machine_state=self.knitting_machine) for i in range(1, carrier_count + 1)
        ]
        self._hook_position: int | None = None
        self._hook_input_direction: Carriage_Pass_Direction | None = None
        self._searching_for_position: bool = False
        self._hooked_carrier: Yarn_Carrier | None = None

    @property
    def knitting_machine(self) -> Knitting_Machine[Machine_LoopT]:
        """
        Returns:
            Knitting_Machine: The knitting machine that this system belongs to.
        """
        return self._knitting_machine

    @property
    def carriers(self) -> list[Yarn_Carrier[Machine_LoopT]]:
        """
        Returns:
            list[Yarn_Carrier]: The list of yarn carriers in this insertion system. The carriers are ordered from 1 to the number of carriers in the system.
        """
        return self._carriers

    @property
    def hook_position(self) -> int | None:
        """
        Returns:
            None | int: The needle slot of the yarn-insertion hook or None if the yarn-insertion hook is not active.

        Notes:
            The hook position will be None if its exact position is to the right of the edge of the knitting machine bed.
        """
        return self._hook_position

    @property
    def hook_input_direction(self) -> Carriage_Pass_Direction | None:
        """
        Returns:
            Carriage_Pass_Direction | None: The direction that the carrier was moving when the yarn-inserting hook was use. None if the yarn-inserting hook is not active.
        """
        return self._hook_input_direction

    @hook_input_direction.setter
    @checked_operation
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
        else:
            with self.handle_violations(response_policy=Violation.INHOOK_RIGHTWARDS):
                if direction is Carriage_Pass_Direction.Rightward:
                    raise ValueError("Yarn Inserting Hook must start in a leftward direction")
            if self.violation_policy.proceed:
                self._hook_input_direction = direction

    @property
    def hooked_carrier(self) -> Yarn_Carrier[Machine_LoopT] | None:
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

    def bring_in(self, carrier_id: int | Yarn_Carrier) -> None:
        """Bring in a yarn carrier without insertion hook (tail to gripper), yarn is considered loose until knit.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to bring in.
        """
        self[carrier_id].bring_in()

    @checked_operation
    def inhook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Bring a yarn in with insertion hook, yarn is not loose after this operation.

        Args:
            carrier_id (int | Yarn_Carrier): Carriers to bring in by id.
        """

        carrier = self[carrier_id]
        with self.handle_violations(handler=self.releasehook):
            if not self.inserting_hook_available and self.hooked_carrier != carrier:
                raise Inserting_Hook_In_Use_Exception(carrier)
        if self.violation_policy.proceed:
            self._hooked_carrier = carrier
            self._searching_for_position = True
            self._hook_position = None
            self._hooked_carrier.inhook()

    def releasehook(self) -> None:
        """Release the yarn inserting hook from whatever carrier is currently using it."""
        if self.hooked_carrier is not None:
            self.hooked_carrier.releasehook()
        self._hooked_carrier = None
        self._searching_for_position = False
        self._hook_position = None
        self.hook_input_direction = None

    @checked_operation
    def out(self, carrier_id: int | Yarn_Carrier) -> None:
        """Move carrier to gripper, removing it from action but does not cut it loose.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to move out.

        Raises:
            Hooked_Carrier_Exception: If carrier is currently connected to insertion hook.
        """
        carrier = self[carrier_id]
        with self.handle_violations(handler=self.releasehook):
            if carrier.is_hooked:
                raise Hooked_Carrier_Exception(carrier_id)
        if self.violation_policy.proceed:
            carrier.out()

    @checked_operation
    def outhook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Cut carrier yarn and move it to grippers with insertion hook, the carrier will no longer be active and is now loose.

        Args:
            carrier_id (int | Yarn_Carrier): Carrier ID to cut and move out.

        Raises:
            Inserting_Hook_In_Use_Exception: If insertion hook is not available.
            Hooked_Carrier_Exception: If carrier is already connected to insertion hook.
        """
        carrier = self[carrier_id]
        with self.handle_violations(response_policy=Violation.INSERTING_HOOK_IN_USE, handler=self.releasehook):
            if carrier.is_hooked:
                raise Hooked_Carrier_Exception(carrier)
            elif not self.inserting_hook_available:
                raise Inserting_Hook_In_Use_Exception(carrier)
        if self.violation_policy.proceed:
            carrier.outhook()

    @checked_operation
    def position_carrier_at_needle(
        self, carrier_id: int | Yarn_Carrier, needle: Needle | None, direction: Carriage_Pass_Direction | None = None
    ) -> None:
        """Update the needle-slot position of a specific carrier.

        Args:
            carrier_id (int | Yarn_Carrier): The carrier to update.
            needle (Needle | None): The needle to position the carrier relative to.
            direction (Carriage_Pass_Direction, optional): The direction of the carrier movement. If this is not provided, the direction will be inferred.

        Raises:
            BLocked_By_Yarn_Inserting_Hook_Exception: If the yarn-inserting hook blocks this carrier movement.
        """
        carrier = self[carrier_id]
        with self.handle_violations(handler=self.releasehook):
            if needle is not None and self.hooked_carrier is not None and self.conflicts_with_inserting_hook(needle):
                raise Blocked_by_Yarn_Inserting_Hook_Exception(self.hooked_carrier, needle)
        if self.violation_policy.proceed:
            carrier.set_position(needle, direction)

    def make_loops(
        self,
        carrier_ids: Sequence[int | Yarn_Carrier] | Yarn_Carrier_Set | Sequence[int] | Sequence[Yarn_Carrier],
        needle: Needle,
        direction: Carriage_Pass_Direction,
        **_loop_kwargs: Any,
    ) -> list[Machine_LoopT]:
        """Create loops using specified carriers on a needle, handling insertion hook positioning and float management.

        Args:
            carrier_ids (list[int | Yarn_Carrier] | Yarn_Carrier_Set): The carriers to make the loops with on this needle.
            needle (Needle): The needle to make the loops on.
            direction (Carriage_Pass_Direction): The carriage direction for this operation.

        Returns:
            list[Machine_Knit_Loop]: The set of loops made on this machine.
        """
        needle = self.knitting_machine[needle]
        if self.searching_for_position:  # mark inserting hook position
            # Position yarn inserting hook at the needle slot to the right of the needle.
            self._hook_position = needle.slot_number + 1
            self.hook_input_direction = direction
            self._searching_for_position = False
        loops: list[Machine_LoopT] = []
        for cid in carrier_ids:
            carrier = self[cid]
            float_source_loop = carrier.yarn.last_loop
            float_source_needle = float_source_loop.holding_needle if float_source_loop is not None else None
            loop = carrier.make_loop(needle, **_loop_kwargs)
            carrier.yarn.add_loop_to_end(loop)
            if float_source_needle is not None:
                float_source_needle = self.knitting_machine[float_source_needle]
                float_start = min(float_source_needle.position, needle.position)
                float_end = max(float_source_needle.position, needle.position)
                front_floated_needles = [
                    f
                    for f in self.knitting_machine.front_bed[float_start : float_end + 1]
                    if f != float_source_needle and f != needle
                ]
                back_floated_needles = [
                    b
                    for b in self.knitting_machine.back_bed[float_start : float_end + 1]
                    if b != float_source_needle and b != needle
                ]
                for float_source_loop in float_source_needle.held_loops:
                    for fn in front_floated_needles:
                        for fl in fn.held_loops:
                            float_source_loop.add_loop_in_front_of_started_float(fl)
                    for bn in back_floated_needles:
                        for bl in bn.held_loops:
                            float_source_loop.add_loop_behind_started_float(bl)
            loops.append(loop)
        return loops
