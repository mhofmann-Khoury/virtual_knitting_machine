"""Module containing Yarn Carrier Snapshot class"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from virtual_knitting_machine.machine_components.needle_bed_position import Needle_Bed_Position
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier, Yarn_Carrier_State
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Yarn_Carrier_Snapshot(Yarn_Carrier_State[Machine_LoopT]):
    """
    A snapshot of the state of a carrier at the time this instance was created.
    """

    def __init__(
        self, yarn_carrier: Yarn_Carrier[Machine_LoopT], machine_snapshot: Knitting_Machine_Snapshot[Machine_LoopT]
    ):
        self._carrier_id: int = yarn_carrier.carrier_id
        self._is_active: bool = yarn_carrier.is_active
        self._is_hooked: bool = yarn_carrier.is_hooked
        self._machine_snapshot: Knitting_Machine_Snapshot[Machine_LoopT] = machine_snapshot
        self._position: Needle_Bed_Position = self.starting_position(self.knitting_machine)
        self._position.update_from_position(yarn_carrier.position_on_bed)
        self._yarn: Machine_Knit_Yarn[Machine_LoopT] = yarn_carrier.yarn
        self._last_loop_id: int | None = int(self.yarn.last_loop) if self.yarn.last_loop is not None else None

    @property
    def knitting_machine(self) -> Knitting_Machine_Snapshot[Machine_LoopT]:
        """
        Returns:
            Knitting_Machine_Snapshot: The knitting machine snapshot that this system belongs to.
        """
        return self._machine_snapshot

    @property
    def last_loop_id(self) -> int | None:
        """
        Returns:
            int | None: The last loop formed on the yarn of this carrier or None if it had not formed a loop yet.
        """
        return self._last_loop_id

    @property
    def yarn(self) -> Machine_Knit_Yarn[Machine_LoopT]:
        """
        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        return self._yarn

    @property
    def position_on_bed(self) -> Needle_Bed_Position:
        """
        Returns:
            Needle_Bed_Position: The position of the machine component relative to the needle bed.
        """
        return self._position

    @property
    def is_active(self) -> bool:
        """
        Returns:
            bool: True if carrier is active, False otherwise.
        """
        return self._is_active

    @property
    def is_hooked(self) -> bool:
        """
        Returns:
            bool: True if connected to inserting hook, False otherwise.
        """
        return self._is_hooked

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: ID of carrier, corresponds to order in machine.
        """
        return self._carrier_id

    def loop_made_before_snapshot(self, loop: int | Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (int | Machine_Knit_Loop): The loop (or loop_id) to compare to the timing of this snapshot.

        Returns:
            bool: True if the given loop was formed prior to the snapshot, False otherwise.

        Notes:
            This program assumes that the loop belongs to the knitgraph rendered by this knitting machine.
        """
        return int(loop) <= self.last_loop_id if isinstance(self.last_loop_id, int) else False
