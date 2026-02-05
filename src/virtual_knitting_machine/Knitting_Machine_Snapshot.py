"""A module containing the Knitting_Machine_Snapshot class."""

from typing import TypeVar

from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine, Knitting_Machine_State
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Snapshot import Carriage_Snapshot
from virtual_knitting_machine.machine_components.Needle_Bed_Snapshot import Needle_Bed_Snapshot
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Snapshot import Yarn_Carrier_Snapshot
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System_Snapshot import (
    Yarn_Insertion_System_Snapshot,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Knitting_Machine_Snapshot(Knitting_Machine_State[Machine_LoopT, Yarn_Carrier_Snapshot]):
    """
    A snapshot of the state of a knitting machine at the time an instance is created.

    Attributes:
        _machine_state (Knitting_Machine): A reference to the current state of the knitting machine that this snapshot was created from. It will update after creation of the snapshot.
    """

    def __init__(self, machine_state: Knitting_Machine[Machine_LoopT]):
        self._machine_state: Knitting_Machine[Machine_LoopT] = machine_state
        self._last_loop_id: int | None = (
            machine_state.knit_graph.last_loop.loop_id if machine_state.knit_graph.last_loop is not None else None
        )
        self._rack: int = machine_state.rack
        self._all_needle_rack: bool = machine_state.all_needle_rack
        self._front_bed_snapshot: Needle_Bed_Snapshot = Needle_Bed_Snapshot(self._machine_state.front_bed, self)
        self._back_bed_snapshot: Needle_Bed_Snapshot = Needle_Bed_Snapshot(self._machine_state.back_bed, self)
        self._carrier_system_snapshot: Yarn_Insertion_System_Snapshot = Yarn_Insertion_System_Snapshot(
            self._machine_state.carrier_system, self
        )
        self._carriage_snapshot: Carriage_Snapshot = Carriage_Snapshot(machine_state.carriage, self)

    @property
    def carriage(self) -> Carriage_Snapshot:
        """
        Returns:
            Carriage_Snapshot: A snapshot of the carriage's state at the time this snapshot was created.
        """
        return self._carriage_snapshot

    @property
    def machine_specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The specification of the knitting machine this snapshot was created from.
        """
        return self._machine_state.machine_specification

    @property
    def knit_graph(self) -> Knit_Graph[Machine_LoopT]:
        """
        Returns:
            Knit_Graph: The knit graph associated with the machine state.

        Notes:
            The knit graph does is a reference to the machine state and will be updated to the latest state of the knitting machine, past the point of this snapshot.
        """
        return self._machine_state.knit_graph

    @property
    def last_loop_id(self) -> int | None:
        """
        Returns:
            int | None: The id of the last loop created on the knitting machine's knitgraph at the time the snapshot was created. None if no loops were in the knitgraph at that time.
        """
        return self._last_loop_id

    @property
    def rack(self) -> int:
        """
        Returns:
            int: The racking offset of the knitting machine at the time the snapshot was created.
        """
        return self._rack

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine has all needle rack at the time the snapshot was created, False otherwise.
        """
        return self._all_needle_rack

    @property
    def front_bed(self) -> Needle_Bed_Snapshot:
        """
        Returns:
            Needle_Bed_Snapshot: The snapshot of the front bed of needles and slider needles.
        """
        return self._front_bed_snapshot

    @property
    def back_bed(self) -> Needle_Bed_Snapshot:
        """
        Returns:
            Needle_Bed_Snapshot:  The snapshot of the back bed of needles and slider needles.
        """
        return self._back_bed_snapshot

    @property
    def carrier_system(self) -> Yarn_Insertion_System_Snapshot:
        """
        Returns:
            Yarn_Insertion_System_Snapshot: The snapshot of the carrier system at the time of this snapshot.
        """
        return self._carrier_system_snapshot

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
