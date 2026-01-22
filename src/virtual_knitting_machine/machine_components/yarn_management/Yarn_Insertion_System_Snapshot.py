"""Module containing Yarn Insertion System Snapshot class"""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Snapshot import Yarn_Carrier_Snapshot
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import (
    Yarn_Insertion_System,
    Yarn_Insertion_System_State,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot


class Yarn_Insertion_System_Snapshot(Yarn_Insertion_System_State[Yarn_Carrier_Snapshot]):
    """
    A snapshot of a given Yarn Insertion System at the time of instance creation.

    Attributes:
        _carriers (list[Yarn_Carrier_Snapshot]): The list of carrier snapshots at the time of this snapshot.
    """

    def __init__(self, yarn_insertion_system: Yarn_Insertion_System, machine_snapshot: Knitting_Machine_Snapshot):
        self._machine_snapshot: Knitting_Machine_Snapshot = machine_snapshot
        self._yarn_insertion_system: Yarn_Insertion_System = yarn_insertion_system
        self._carriers: list[Yarn_Carrier_Snapshot] = [Yarn_Carrier_Snapshot(c) for c in yarn_insertion_system.carriers]
        self._hook_position: int | None = self.yarn_insertion_system.hook_position
        self._hook_input_direction: Carriage_Pass_Direction | None = self.yarn_insertion_system.hook_input_direction
        self._searching_for_position: bool = self.yarn_insertion_system.searching_for_position
        self._hooked_carrier_id: int | None = (
            self.yarn_insertion_system.hooked_carrier.carrier_id
            if isinstance(self.yarn_insertion_system.hooked_carrier, Yarn_Carrier)
            else None
        )
        self.active_loops_by_carrier: dict[Yarn_Carrier_Snapshot, dict[Machine_Knit_Loop, Needle]] = {
            c: c.yarn.active_loops for c in self._carriers
        }
        self.active_floats_by_carrier: dict[Yarn_Carrier_Snapshot, dict[Machine_Knit_Loop, Machine_Knit_Loop]] = {
            c: c.yarn.active_floats() for c in self._carriers
        }
        self._active_floats: dict[Machine_Knit_Loop, Machine_Knit_Loop] = {}
        for floats in self.active_floats_by_carrier.values():
            self._active_floats.update(floats)

    @property
    def yarn_insertion_system(self) -> Yarn_Insertion_System:
        """
        Returns:
            Yarn_Insertion_System: The Yarn Insertion System this snapshot was taken from.
        """
        return self._yarn_insertion_system

    @property
    def knitting_machine(self) -> Knitting_Machine_Snapshot:
        """
        Returns:
            Knitting_Machine_Snapshot: The knitting machine snapshot that this system belongs to.
        """
        return self._machine_snapshot

    @property
    def carriers(self) -> list[Yarn_Carrier_Snapshot]:
        """
        Returns:
            list[Yarn_Carrier_Snapshot]: The list of yarn carriers in this insertion system. The carriers are ordered from 1 to the number of carriers in the system.
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

    @property
    def hooked_carrier(self) -> Yarn_Carrier_Snapshot | None:
        """
        Returns:
            (Yarn_Carrier_Snapshot | None): The snapshot of the yarn-carrier that was on the yarn-inserting-hook or None if the hook was not active.
        """
        return self[self._hooked_carrier_id] if self._hooked_carrier_id is not None else None

    @property
    def searching_for_position(self) -> bool:
        """
        Returns:
            bool: True if the inserting hook is active but at an undefined position, False otherwise.
        """
        if self.inserting_hook_available:
            return False
        return self._searching_for_position

    @property
    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """Get dictionary of all active floats from all carriers in the system.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]:
                Dictionary of loops that are active keyed to active yarn-wise neighbors, each key-value pair represents a directed float where k comes before v on the yarns in the system.
        """
        return self._active_floats
