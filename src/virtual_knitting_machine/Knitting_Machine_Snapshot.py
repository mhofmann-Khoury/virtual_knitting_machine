"""A module containing the Knitting_Machine_Snapshot class."""

from collections.abc import Sequence
from typing import overload

from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Snapshot import Carriage_Snapshot
from virtual_knitting_machine.machine_components.Needle_Bed_Snapshot import Needle_Bed_Snapshot
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Snapshot import Yarn_Carrier_Snapshot
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System_Snapshot import (
    Yarn_Insertion_System_Snapshot,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Knitting_Machine_Snapshot:
    """
    A snapshot of the state of a knitting machine at the time an instance is created.

    Attributes:
        _machine_state (Knitting_Machine): A reference to the current state of the knitting machine that this snapshot was created from. It will update after creation of the snapshot.
    """

    def __init__(self, machine_state: Knitting_Machine):
        self._machine_state: Knitting_Machine = machine_state
        self._last_loop_id: int | None = (
            machine_state.knit_graph.last_loop.loop_id if machine_state.knit_graph.last_loop is not None else None
        )
        self._rack: int = machine_state.rack
        self._all_needle_rack: bool = machine_state.all_needle_rack
        self._front_bed_snapshot: Needle_Bed_Snapshot = Needle_Bed_Snapshot(self._machine_state.front_bed)
        self._back_bed_snapshot: Needle_Bed_Snapshot = Needle_Bed_Snapshot(self._machine_state.back_bed)
        self._carrier_system_snapshot: Yarn_Insertion_System_Snapshot = Yarn_Insertion_System_Snapshot(
            self._machine_state.carrier_system
        )
        self._carriage_snapshot: Carriage_Snapshot = Carriage_Snapshot(machine_state.carriage)

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
    def knit_graph(self) -> Knit_Graph:
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
    def max_rack(self) -> int:
        """Get the maximum distance that the machine can rack.

        Returns:
            int: The maximum distance that the machine can rack.
        """
        return int(self._machine_state.max_rack)

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
    def sliders_are_clear(self) -> bool:
        """
        Returns:
            bool: True if there are no loops on back for front bed sliders at the time the snapshot was created. False otherwise.
        """
        return self.front_bed.sliders_are_clear and self.back_bed.sliders_are_clear

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

    def valid_rack(self, front_pos: int, back_pos: int) -> bool:
        """Check if transfer can be completed at the racking of the current snapshot.

        Args:
            front_pos (int): The front needle in the racking.
            back_pos (int): The back needle in the racking.

        Returns:
            bool: True if the current racking can make this transfer, False otherwise.
        """
        needed_rack = Knitting_Machine.get_rack(front_pos, back_pos)
        return self.rack == needed_rack

    def get_aligned_needle(self, needle: Needle, aligned_slider: bool = False) -> Needle:
        """Get the needle aligned with the given needle at current racking.

        Args:
            needle (Needle): The needle to find the aligned needle to.
            aligned_slider (bool, optional): If True, will return a slider needle. Defaults to False.

        Returns:
            Needle: Needle aligned with the given needle at current racking.

        Note:
            From Knitout Specification:
            Specification: at racking R, back needle index B is aligned to front needle index B+R,
            needles are considered aligned if they can transfer.
            At racking 2 it is possible to transfer from f3 to b1 using formulas F = B + R, R = F - B, B = F - R.
        """
        aligned_position = needle.position - self.rack if needle.is_front else needle.position + self.rack
        if aligned_slider:
            return Slider_Needle(not needle.is_front, aligned_position)
        else:
            return Needle(not needle.is_front, aligned_position)

    @property
    def front_active_needles(self) -> set[Needle]:
        """
        Returns:
            set[Needle]: A set of front bed needles that actively hold loops at the time the snapshot was created.
        """
        return self.front_bed.active_needles

    @property
    def front_active_sliders(self) -> set[Slider_Needle]:
        """
        Returns:
            set[Slider_Needle]: A set of front bed sliders that actively hold loops at the time the snapshot was created.
        """
        return self.front_bed.active_sliders

    @property
    def back_active_needles(self) -> set[Needle]:
        """
        Returns:
            set[Needle]: A set of back bed needles that actively hold loops at the time the snapshot was created.
        """
        return self.back_bed.active_needles

    @property
    def back_active_sliders(self) -> set[Slider_Needle]:
        """
        Returns:
            set[Slider_Needle]: A set of back bed sliders that actively hold loops at the time the snapshot was created.
        """
        return self.back_bed.active_sliders

    @property
    def all_active_needles(self) -> set[Needle]:
        """
        Returns:
            set[Needle]: The set of all needles that held loops at the time that the snapshot was created.
        """
        return set(*self.front_active_needles, *self.back_active_needles)

    @property
    def all_active_sliders(self) -> set[Slider_Needle]:
        """
        Returns:
            set[Slider_Needle]: The set of all sliders that held loops at the time that the snapshot was created.
        """
        return set(*self.front_active_sliders, *self.back_active_sliders)

    # noinspection PyMissingOrEmptyDocstring
    @overload
    def get_carrier_snapshot(self, carrier: int | Yarn_Carrier | Yarn_Carrier_Snapshot) -> Yarn_Carrier_Snapshot: ...

    # noinspection PyMissingOrEmptyDocstring
    @overload
    def get_carrier_snapshot(
        self, carrier: Yarn_Carrier_Set | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
    ) -> Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]: ...

    def get_carrier_snapshot(
        self,
        carrier: (
            int
            | Yarn_Carrier
            | Yarn_Carrier_Snapshot
            | Yarn_Carrier_Set
            | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
        ),
    ) -> Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]:
        """Get the snapshot of the carrier or list of carriers owned by the machine at the given specification.

        Args:
            carrier (int | Yarn_Carrier | Yarn_Carrier_Set | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]):
                The carrier defined by a given snapshot, carrier, carrier_set, integer or list of integers to form a set.

        Returns:
            Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]:
                The snapshot of the carrier or list of carriers owned by the machine at the given specification.
        """
        return self.carrier_system[carrier]

    def __contains__(self, item: Needle | Machine_Knit_Loop) -> bool:
        if isinstance(item, (Needle | Machine_Knit_Loop)):
            return item in self.front_bed or item in self.back_bed

    @overload
    def __getitem__(self, item: Needle) -> list[Machine_Knit_Loop]: ...

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle: ...

    @overload
    def __getitem__(self, item: Yarn_Carrier | Yarn_Carrier_Snapshot) -> Yarn_Carrier_Snapshot: ...

    @overload
    def __getitem__(
        self, item: Yarn_Carrier_Set | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
    ) -> Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]: ...

    def __getitem__(
        self,
        item: (
            Needle
            | Machine_Knit_Loop
            | Yarn_Carrier
            | Yarn_Carrier_Snapshot
            | Yarn_Carrier_Set
            | Sequence[int | Yarn_Carrier | Yarn_Carrier_Snapshot]
        ),
    ) -> Needle | list[Machine_Knit_Loop] | Yarn_Carrier_Snapshot | list[Yarn_Carrier_Snapshot]:
        if isinstance(item, Needle):
            if item.is_front:
                return self.front_bed[item]
            else:
                return self.back_bed[item]
        elif isinstance(item, Machine_Knit_Loop):
            try:
                return self.front_bed[item]
            except KeyError:
                return self.back_bed[item]
        elif isinstance(item, (Yarn_Carrier, Yarn_Carrier_Snapshot, Sequence, Yarn_Carrier_Set)):
            return self.get_carrier_snapshot(item)
