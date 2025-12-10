"""A module containing the Needle_Bed_Snapshot class."""

from typing import overload

from virtual_knitting_machine.machine_components.Needle_Bed import Needle_Bed
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Needle_Bed_Snapshot:
    """A snapshot of the state of a knitting machine at the time an instance is created.

    Attributes:
        needle_bed (Needle_Bed): The needle bed this snapshot was taken from. The needle bed will continue to update after the snapshot is initialized.
        active_needle_snapshots (dict[int, list[Machine_Knit_Loop]]): Mapping of needle indices on the bed that were actively holding loops at the snapshot time to the stack of loops at that time.
        active_slider_snapshots (dict[int, list[Machine_Knit_Loop]]):
            Mapping of slider indices on the bed that were actively holding loops at the snapshot time to the stack of loops at that time.
    """

    def __init__(self, needle_bed: Needle_Bed):
        self.needle_bed: Needle_Bed = needle_bed
        self._is_front: bool = needle_bed.is_front
        self.active_needle_snapshots: dict[int, list[Machine_Knit_Loop]] = {
            n.position: list(n.held_loops) for n in self.needle_bed.loop_holding_needles()
        }
        self.active_slider_snapshots: dict[int, list[Machine_Knit_Loop]] = {
            n.position: list(n.held_loops) for n in self.needle_bed.loop_holding_needles()
        }
        self.active_needles: set[Needle] = set()
        self.active_sliders: set[Slider_Needle] = set()
        self.loops_on_needles: dict[Machine_Knit_Loop, int] = {}
        self.loops_on_sliders: dict[Machine_Knit_Loop, int] = {}
        for n, loops in self.active_needle_snapshots.items():
            needle = Needle(is_front=self.is_front, position=n)
            needle.held_loops = loops
            self.active_needles.add(needle)
            self.loops_on_needles.update({l: n for l in loops})
        for n, loops in self.active_slider_snapshots.items():
            needle = Slider_Needle(is_front=self.is_front, position=n)
            needle.held_loops = loops
            self.active_sliders.add(needle)
            self.loops_on_sliders.update({l: n for l in loops})
        self._loop_history: dict[Machine_Knit_Loop, int] = {l: len(l.needle_history) for l in self.loops_on_needles}
        self._loop_history.update({l: len(l.needle_history) for l in self.loops_on_sliders})

    @property
    def active_needle_count(self) -> int:
        """
        Returns:
            int: The number of active needles at the time of the snapshot.
        """
        return len(self.active_needle_snapshots)

    @property
    def active_slider_count(self) -> int:
        """
        Returns:
            int: The number of active sliders at the time of the snapshot.
        """
        return len(self.active_slider_snapshots)

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this snapshot is the front bed of the knitting machine, False otherwise.
        """
        return self._is_front

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if this snapshot is the back bed of the knitting machine, False otherwise.
        """
        return not self.is_front

    @property
    def sliders_are_clear(self) -> bool:
        """
        Returns:
            bool: True if no loops are on the sliders at time of this snapshot, False otherwise.
        """
        return self.active_slider_count == 0

    def slider_was_active(self, slider: int | Slider_Needle) -> bool:
        """
        Args:
            slider: The slider or index of a slider on this needle bed.

        Returns:
            bool: True if the given slider actively held loops at the time of this snapshot, False otherwise.

        Raises:
            KeyError: If the given slider is not a slider or the given needle bed.
        """
        if isinstance(slider, Slider_Needle) and slider.is_front != self.is_front:
            raise KeyError(f"{slider} does not belong to this {'Front' if self.is_front else 'Back'} needle bed")
        return int(slider) in self.active_slider_snapshots

    def needle_was_active(self, needle: int | Needle) -> bool:
        """
        Args:
            needle: THe needle or index of a needl on this needle bed.

        Returns:
            bool: True if the given needle actively held loops at the time of this snapshot, False otherwise.

        Raises:
            KeyError: If the given needle is not a needle or the given needle bed.
        """
        if isinstance(needle, Slider_Needle):
            return self.slider_was_active(needle)
        elif isinstance(needle, Needle) and needle.is_front != self.is_front:
            raise KeyError(f"{needle} does not belong to this {'Front' if self.is_front else 'Back'} needle bed")
        return int(needle) in self.active_needle_snapshots

    def loop_was_active(self, loop: Machine_Knit_Loop) -> bool:
        """

        Args:
            loop (Machine_Knit_Loop): The loop to check if it was on a needle at the time of this snapshot.

        Returns:
            bool: True if the given loop was held at the time of this snapshot, False otherwise.
        """
        return loop in self._loop_history

    def loop_on_slider(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to check if it was on a slider at the time of the snapshot.

        Returns:
            bool: True if the loop was on a slider at the time of the snapshot. False, otherwise.
        """
        return loop in self.loops_on_sliders

    def loop_on_needle(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to check if it was on a main-bed needle at the time of the snapshot.

        Returns:
            bool: True if the loop was on a main bed needle at the time of the snapshot. False, otherwise.
        """
        return loop in self.loops_on_needles

    def needle_holding_loop(self, loop: Machine_Knit_Loop) -> Needle | None:
        """
        Args:
            loop (Machine_Knit_Loop): The machine knit loop to find the holding needle of at the time of the snapshot.

        Returns:
            Needle | None: The needle that held the loop at the time of this snapshot or None if the loop was not actively held at the time of this snapshot.
        """
        if not self.loop_was_active(loop):
            return None
        return loop.needle_history[self._loop_history[loop]]

    def __contains__(self, item: int | Needle | Machine_Knit_Loop) -> bool:
        """
        Args:
            item (int | Needle | Machine_Knit_Loop):
                The active loop or needle to find in this snapshot. If item is an integer, the position is assumed to be a needle index, not a slider index or loop_id.

        Returns:
            bool: True if the given needle, needle position, or loop was active at the time of the snapshot, False otherwise.
        """
        if isinstance(item, Machine_Knit_Loop):
            return self.loop_was_active(item)
        elif isinstance(item, Needle) and item.is_front != self.is_front:
            return False
        return self.needle_was_active(item)

    @overload
    def __getitem__(self, item: int | Needle) -> list[Machine_Knit_Loop]: ...

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle: ...

    def __getitem__(self, item: int | Needle | Machine_Knit_Loop) -> list[Machine_Knit_Loop] | Needle:
        """
        Args:
            item (int | Needle | Machine_Knit_Loop):
                The active needle or loop to find in this snapshot.
                If item is an integer, the position is assumed to be a needle index, not a slider index or loop id.

        Returns:
            list[Machine_Knit_Loop] | Needle: The list of loops on the given needle at the time of the snapshot or the needle that held the given loop.

        Raises:
            KeyError: If the given item is not an active needle, slider needle, or loop at the time of the snapshot.
        """
        if item not in self:
            if isinstance(item, int):
                item = Needle(is_front=self.is_front, position=item)
            raise KeyError(f"{item} was not active at the time of this snapshot")
        if isinstance(item, Machine_Knit_Loop):
            holding = self.needle_holding_loop(item)
            assert isinstance(holding, Needle)
            return holding
        if isinstance(item, Slider_Needle):
            return self.active_slider_snapshots[item.position]
        else:
            return self.active_needle_snapshots[int(item)]

    def __len__(self) -> int:
        """
        Returns:
            int: The number of active needles (excluding sliders) on this bed at the time of the snapshot.
        """
        return self.active_needle_count
