"""A module containing the Carriage Snapshot Class"""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage, Carriage_State
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot


class Carriage_Snapshot(Carriage_State):
    """
    A class used to represent a snapshot of the state of the given carriage at the time of instantiation.
    """

    def __init__(self, carriage: Carriage, machine_snapshot: Knitting_Machine_Snapshot):
        self._machine_snapshot: Knitting_Machine_Snapshot = machine_snapshot
        self._transferring: bool = carriage.transferring
        self._last_direction: Carriage_Pass_Direction = carriage.last_direction
        self._current_needle_position: int = carriage.current_needle_slot
        self._position_prior_to_transfers: int = carriage.slot_prior_to_transfers
        self._direction_prior_to_transfers: Carriage_Pass_Direction = carriage.direction_prior_to_transfers

    @property
    def knitting_machine(self) -> Knitting_Machine_Snapshot:
        """
        Returns:
            Knitting_Machine_Snapshot: The knitting machine snapshot that owns this carriage.
        """
        return self._machine_snapshot

    @property
    def transferring(self) -> bool:
        """
        Returns:
            bool: True if the carriage was currently running transfers, False otherwise.
        """
        return self._transferring

    @property
    def current_needle_slot(self) -> int:
        """
        Returns:
            int: The needle position of the carriage at the time of the snapshot.
        """
        return self._current_needle_position

    @property
    def slot_prior_to_transfers(self) -> int:
        """
        Returns:
            int: The position of the carriage prior to its last transfer pass.
        """
        return self._position_prior_to_transfers

    @property
    def last_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The last direction the carriage moved in prior to this snapshot.
        """
        return self._last_direction

    @property
    def direction_prior_to_transfers(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction the carriage was moving prior to the latest transfer pass.
        """
        return self._direction_prior_to_transfers
