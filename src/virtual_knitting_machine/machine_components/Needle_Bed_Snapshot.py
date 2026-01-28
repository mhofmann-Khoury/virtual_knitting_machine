"""A module containing the Needle_Bed_Snapshot class."""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

from virtual_knitting_machine.machine_components.Needle_Bed import Needle_Bed, Needle_Bed_State
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot


class Needle_Bed_Snapshot(Needle_Bed_State):
    """A snapshot of the state of a knitting machine at the time an instance is created."""

    def __init__(self, needle_bed: Needle_Bed, machine_snapshot: Knitting_Machine_Snapshot):
        self._machine_snapshot: Knitting_Machine_Snapshot = machine_snapshot
        self._is_front: bool = needle_bed.is_front
        self._loops_to_needles: dict[Machine_Knit_Loop, Needle] = {}
        self._active_needles: list[Needle] = []
        for n in needle_bed.loop_holding_needles:
            n_copy = Needle(n.is_front, n.position)
            n_copy.held_loops.extend(n.held_loops)
            self._active_needles.append(n_copy)
            self._loops_to_needles.update({l: n_copy for l in n.held_loops})
        self._active_needles_by_position: dict[int, Needle] = {n.position: n for n in self._active_needles}

        self._active_sliders: list[Slider_Needle] = []
        for n in needle_bed.loop_holding_sliders:
            n_copy = Slider_Needle(n.is_front, n.position)
            n_copy.held_loops.extend(n.held_loops)
            self._active_sliders.append(n_copy)
            self._loops_to_needles.update({l: n_copy for l in n.held_loops})
        self._active_sliders_by_position: dict[int, Slider_Needle] = {n.position: n for n in self._active_sliders}

    @property
    def knitting_machine(self) -> Knitting_Machine_Snapshot:
        """
        Returns:
            Knitting_Machine_Snapshot: The knitting machine this bed belongs to.
        """
        return self._machine_snapshot

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this snapshot is the front bed of the knitting machine, False otherwise.
        """
        return self._is_front

    @property
    def needles(self) -> list[Needle]:
        """
        Returns:
            list[Needle]: The active needles ordered by their position on the knitting machine"""
        return self._active_needles

    @property
    def sliders(self) -> list[Slider_Needle]:
        """
        Returns:
            list[Slider_Needle]: The active slider needles ordered by their position on the knitting machine"
        """
        return self._active_sliders

    @property
    def loop_holding_needles(self) -> list[Needle]:
        """
        Returns:
            list[Needle]: List of needles on bed that actively hold loops.
        """
        return self._active_needles

    @property
    def loop_holding_sliders(self) -> list[Slider_Needle]:
        """
        Returns:
            list[Slider_Needle]: List of sliders on bed that actively hold loops.
        """
        return self._active_sliders

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> Needle | None:
        """
        Args:
            loop (Machine_Knit_Loop): The loop being searched for.

        Returns:
            Needle | None: None if the bed does not hold the loop, otherwise the needle position that holds it.
        """
        return self._loops_to_needles.get(loop, None)

    def slider_is_active(self, slider: int | Slider_Needle) -> bool:
        """
        Args:
            slider: The slider or index of a slider on this needle bed.

        Returns:
            bool: True if the given slider is on this bed and holds at least one loop, False otherwise.
        """
        if isinstance(slider, Slider_Needle) and slider.is_front != self.is_front:
            return False
        else:
            return int(slider) in self._active_sliders_by_position

    def needle_is_active(self, needle: int | Needle) -> bool:
        """
        Args:
            needle: THe needle or index of a needl on this needle bed.

        Returns:
            bool: True if the given needle is on this bed and holds at least one loop, False otherwise.
        """
        if isinstance(needle, Needle) and needle.is_front != self.is_front:
            return False
        else:
            return int(needle) in self._active_needles_by_position

    def __contains__(self, item: object) -> bool:
        """
        Args:
            item (Machine_Knit_Loop | Needle | int):
                The active loop or needle to find in this snapshot. If item is an integer, the position is assumed to be a needle index, not a slider index or loop_id.

        Returns:
            bool: True if the given needle, needle position, or loop was active at the time of the snapshot, False otherwise.
        """
        if isinstance(item, Machine_Knit_Loop):
            return self.loop_is_active(item)
        elif isinstance(item, Needle) and item.is_front != self.is_front:
            return False
        elif isinstance(item, Slider_Needle):
            return self.slider_is_active(item)
        elif isinstance(item, (int, Needle)):
            return self.needle_is_active(item)
        else:
            return False

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle | None: ...

    @overload
    def __getitem__(self, item: Needle | int) -> Needle: ...

    @overload
    def __getitem__(self, item: slice) -> list[Needle]: ...

    def __getitem__(self, item: Machine_Knit_Loop | Needle | slice | int) -> Needle | list[Needle] | None:
        """
        Args:
            item (Machine_Knit_Loop | Needle | slice | int):
                The active needle or loop to find in this snapshot.
                If item is an integer, the position is assumed to be a needle index, not a slider index or loop id.

        Returns:
            list[Machine_Knit_Loop] | Needle: The list of loops on the given needle at the time of the snapshot or the needle that held the given loop.

        Raises:
            KeyError: If the given item is not an active needle, slider needle, or loop at the time of the snapshot.
        """
        if isinstance(item, slice):
            return [self[n] for n in range(item.start, item.stop, item.step) if n in self._active_needles_by_position]
        elif isinstance(item, int):
            if item not in self._active_needles_by_position:
                raise KeyError(f"{item} was not an active needle on {self} at the time of the snapshot.")
            return self._active_needles_by_position[item]
        elif isinstance(item, Machine_Knit_Loop):
            if item not in self._loops_to_needles:
                raise KeyError(f"{item} was not an active loop on {self} at the time of the snapshot.")
            return self._loops_to_needles[item]
        elif item.is_front != self.is_front:
            raise KeyError(f"{item} is not on {self}")
        elif isinstance(item, Slider_Needle):
            if item.position not in self._active_sliders_by_position:
                raise KeyError(f"{item} was not an active slider on {self} at the time of the snapshot.")
            return self._active_sliders_by_position[item.position]
        else:
            return self[int(item)]
