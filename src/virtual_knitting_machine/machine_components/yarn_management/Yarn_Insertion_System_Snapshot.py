"""Module containing Yarn Insertion System Snapshot class"""

from collections.abc import Sequence
from typing import cast, overload

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Snapshot import Yarn_Carrier_Snapshot
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import Yarn_Insertion_System
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Yarn_Insertion_System_Snapshot:
    """
    A snapshot of a given Yarn Insertion System at the time of instance creation.

    Attributes:
        carrier_snapshots (list[Yarn_Carrier_Snapshot]): The list of carrier snapshots at the time of this snapshot.
    """

    def __init__(self, yarn_insertion_system: Yarn_Insertion_System):
        self._yarn_insertion_system: Yarn_Insertion_System = yarn_insertion_system
        self.carrier_snapshots: list[Yarn_Carrier_Snapshot] = [
            Yarn_Carrier_Snapshot(c) for c in yarn_insertion_system.carriers
        ]
        self._hook_position: int = (
            self.yarn_insertion_system.hook_position
            if self.yarn_insertion_system.hook_position is not None
            else self.yarn_insertion_system.knitting_machine.needle_count
            + Yarn_Insertion_System.FREE_INSERTING_HOOK_POSITION
        )
        self._hook_input_direction: None | Carriage_Pass_Direction = self.yarn_insertion_system.hook_input_direction
        self._searching_for_position: bool = self.yarn_insertion_system.searching_for_position
        self._hooked_carrier_id: int | None = (
            self.yarn_insertion_system.hooked_carrier.carrier_id
            if isinstance(self.yarn_insertion_system.hooked_carrier, Yarn_Carrier)
            else None
        )
        self.active_loops_by_carrier: dict[Yarn_Carrier_Snapshot, dict[Machine_Knit_Loop, Needle]] = {
            c: c.yarn.active_loops for c in self.carrier_snapshots
        }
        self.active_floats_by_carrier: dict[Yarn_Carrier_Snapshot, dict[Machine_Knit_Loop, Machine_Knit_Loop]] = {
            c: c.yarn.active_floats() for c in self.carrier_snapshots
        }
        self.active_floats: dict[Machine_Knit_Loop, Machine_Knit_Loop] = {}
        for floats in self.active_floats_by_carrier.values():
            self.active_floats.update(floats)

    @property
    def yarn_insertion_system(self) -> Yarn_Insertion_System:
        """
        Returns:
            Yarn_Insertion_System: The Yarn Insertion System this snapshot was taken from.
        """
        return self._yarn_insertion_system

    @property
    def hook_position(self) -> None | int:
        """
        Returns:
            None | int: The needle slot of the yarn-insertion hook or None if the yarn-insertion hook was not active.

        Notes:
            The hook position will be None if its exact position is to the right of the edge of the knitting machine bed.
        """
        if self._hook_position >= self.yarn_insertion_system.knitting_machine.needle_count:
            return self._hook_position
        else:
            return None

    @property
    def hook_input_direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            None | Carriage_Pass_Direction: The direction that the carrier was moving when the yarn-inserting hook was use. None if the yarn-inserting hook is not active.
        """
        return self._hook_input_direction

    @property
    def hooked_carrier(self) -> Yarn_Carrier_Snapshot | None:
        """
        Returns:
            (Yarn_Carrier_Snapshot | None): The snapshot of the yarn-carrier that was on the yarn-inserting-hook or None if the hook was not active.
        """
        return self[self._hooked_carrier_id] if isinstance(self._hooked_carrier_id, int) else None

    @property
    def inserting_hook_available(self) -> bool:
        """Check if the yarn inserting hook can be used.

        Returns:
            bool: True if the yarn inserting hook can be used, False if in use.
        """
        return self.hooked_carrier is None

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
    def active_carriers(self) -> set[Yarn_Carrier_Snapshot]:
        """
        Returns:
            set[Yarn_Carrier_Snapshot]: Set of snapshots of carriers that were active (off the grippers).
        """
        return {c for c in self.carrier_snapshots if c.is_active}

    def yarn_is_loose(self, carrier_id: int | Yarn_Carrier | Yarn_Carrier_Snapshot) -> bool:
        """Check if yarn in carrier was loose (not on the inserting hook or tuck/knit on bed).

        Args:
            carrier_id (int | Yarn_Carrier): The carrier to check for loose yarn.

        Returns:
            bool: True if any yarn in yarn carrier set is loose (not on the inserting hook or tuck/knit on bed), False otherwise.
        """
        return self[carrier_id].last_loop_id is None

    def conflicts_with_inserting_hook(self, needle_position: Needle | int | None) -> bool:
        """Check if a needle position conflicted with the inserting hook position.

        Args:
            needle_position (Needle | int | None): The needle position to check for compliance, or None if the position is moving a carrier off the machine.

        Returns:
            bool: True if inserting hook conflicted with a needle slot because the slot is to the right of the hook's current position. False otherwise.
        """
        if needle_position is None or self.inserting_hook_available:
            return False  # Non-position does not conflict with yarn-inserting hook.
        return self._hook_position <= int(needle_position)

    def missing_carriers(self, carrier_ids: list[int | Yarn_Carrier | Yarn_Carrier_Snapshot]) -> list[int]:
        """Get list of carrier IDs that are were not active.

        Args:
            carrier_ids (list[int | Yarn_Carrier | Yarn_Carrier_Snapshot]): The carrier set to check for the inactive carriers.

        Returns:
            list[int]: List of carrier ids that were not active (i.e., on grippers).
        """
        return [int(cid) for cid in carrier_ids if not self[cid].is_active]

    def is_active(self, carrier_ids: list[int | Yarn_Carrier | Yarn_Carrier_Snapshot]) -> bool:
        """Check if all carriers in the given set were active (not on the gripper).

        Args:
            carrier_ids (list[int | Yarn_Carrier | Yarn_Carrier_Snapshot]): List of carrier IDs to check.

        Returns:
            bool: True if all carriers in set were active (not-on the gripper).

        Notes:
            If an empty list of carriers is given, this will return true because the empty set is active.
        """
        if len(carrier_ids) == 0:
            return True  # No ids given, so the null set is active
        return len(self.missing_carriers(carrier_ids)) == 0

    def __len__(self) -> int:
        """
        Returns:
            int: The number of carriers in the yarn-inserting system.
        """
        return len(self.carrier_snapshots)

    @overload
    def __getitem__(self, item: int | Yarn_Carrier | Yarn_Carrier_Snapshot) -> Yarn_Carrier_Snapshot: ...

    @overload
    def __getitem__(
        self, item: Yarn_Carrier_Set | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
    ) -> list[Yarn_Carrier_Snapshot] | Yarn_Carrier_Snapshot: ...

    def __getitem__(
        self,
        item: (
            int
            | Yarn_Carrier
            | Yarn_Carrier_Snapshot
            | Yarn_Carrier_Set
            | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
        ),
    ) -> Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]:
        """Get carrier(s) by ID, carrier object, carrier set, or list of IDs/carriers.

        Args:
            item (int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]): The identifier(s) for the carrier(s) to retrieve.

        Returns:
            Yarn_Carrier | list[Yarn_Carrier]: Single carrier or list of carriers corresponding to the input.

        Raises:
            KeyError: If invalid carrier ID is provided or carrier index is out of range.
        """
        try:
            if isinstance(item, (Yarn_Carrier, Yarn_Carrier_Snapshot)):
                return self[item.carrier_id]
            elif isinstance(item, Yarn_Carrier_Set):
                return self[cast(list[int | Yarn_Carrier | Yarn_Carrier_Snapshot], [item.carrier_ids])]
            elif isinstance(item, Sequence):
                if len(item) == 1:
                    return self[item[0]]
                else:
                    return [self[i] for i in item]
        except KeyError:
            raise KeyError(f"Invalid carrier: {item}. Carriers range from 1 to {len(self)}") from None
        assert isinstance(item, int)
        if item < 1 or item > len(self):
            raise KeyError(f"Invalid carrier index {item}")
        return self.carrier_snapshots[
            item - 1
        ]  # Carriers are given from values starting at 1 but indexed in the list starting at zero
