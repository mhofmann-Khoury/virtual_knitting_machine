"""A module containing the Carriage Snapshot Class"""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage, Carriage_State
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needle_bed_position import Needle_Bed_Position
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot


class Carriage_Snapshot(Carriage_State):
    """
    A class used to represent a snapshot of the state of the given carriage at the time of instantiation.
    """

    def __init__(self, carriage: Carriage, machine_snapshot: Knitting_Machine_Snapshot):
        self._machine_snapshot: Knitting_Machine_Snapshot = machine_snapshot
        self._position: Needle_Bed_Position = Needle_Bed_Position(
            parking_position=Side_of_Needle_Bed.Left_Side,
            rightmost_slot=self.needle_count_of_machine,
            stopping_distance=0,
        )
        self._position.update_from_position(carriage.position_on_bed)
        self._last_set_direction: Carriage_Pass_Direction = carriage.last_set_direction

    @property
    def knitting_machine(self) -> Knitting_Machine_Snapshot:
        """
        Returns:
            Knitting_Machine_Snapshot: The knitting machine that owns this carriage.
        """
        return self._machine_snapshot

    @property
    def position_on_bed(self) -> Needle_Bed_Position:
        return self._position

    @property
    def last_set_direction(self) -> Carriage_Pass_Direction:
        return self._last_set_direction
