"""Representation module for needle beds on knitting machines.
This module provides the Needle_Bed class which represents one bed of needles (front or back) on a knitting machine,
managing both regular needles and slider needles with their associated loops and operations."""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from typing import TYPE_CHECKING, overload

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Needle_Holds_Too_Many_Loops
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine


class Needle_Bed:
    """A structure to hold information about loops held on one bed of needles where increasing indices indicate needles moving from left to right (LEFT -> 0 1 2....N <- RIGHT of Machine).
    This class manages both regular needles and slider needles, tracks active sliders, and provides methods for loop manipulation and needle access operations.

    Attributes:
        needles (list[Needle]): The needles on this bed ordered from 0 to max.
        sliders (list[Slider_Needle]): The slider needles on this bed ordered from 0 to max.
    """

    def __init__(self, is_front: bool, knitting_machine: Knitting_Machine) -> None:
        """Initialize a needle bed representation for the machine.

        Args:
            is_front (bool): True if this is the front bed, False if it is the back bed.
            knitting_machine (Knitting_Machine): The knitting machine this bed belongs to.
        """
        self._knitting_machine: Knitting_Machine = knitting_machine
        self._is_front: bool = is_front
        self.needles: list[Needle] = [Needle(self._is_front, i) for i in range(0, self.needle_count)]
        self.sliders: list[Slider_Needle] = [Slider_Needle(self._is_front, i) for i in range(0, self.needle_count)]
        self._active_sliders: set[Slider_Needle] = set()

    def loop_holding_needles(self) -> list[Needle]:
        """Get list of needles on bed that actively hold loops.

        Returns:
            list[Needle]: List of needles on bed that actively hold loops.
        """
        return [n for n in self if n.has_loops]

    def loop_holding_sliders(self) -> list[Slider_Needle]:
        """Get list of sliders on bed that actively hold loops.

        Returns:
            list[Slider_Needle]: List of sliders on bed that actively hold loops.
        """
        return [s for s in self.sliders if s.has_loops]

    @property
    def needle_count(self) -> int:
        """Get the number of needles on the bed.

        Returns:
            int: The number of needles on the bed.
        """
        return int(self._knitting_machine.machine_specification.needle_count)

    @property
    def is_front(self) -> bool:
        """Check if this is the front bed.

        Returns:
            bool: True if this is the front bed, False if back bed.
        """
        return self._is_front

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if this is the back bed, False if front bed.
        """
        return not self.is_front

    def add_loops(
        self, needle: Needle, loops: list[Machine_Knit_Loop], drop_prior_loops: bool = True
    ) -> list[Machine_Knit_Loop]:
        """Add loops to a given needle, optionally dropping existing loops as if a knit operation took place.

        Args:
            needle (Needle): The needle to add the loops on.
            loops (list[Machine_Knit_Loop]): The loops to put on the needle if not creating with the yarn carrier.
            drop_prior_loops (bool, optional): If True, any loops currently held on this needle are dropped. Defaults to True.

        Returns:
            list[Machine_Knit_Loop]: Returns the list of loops made with the carrier on this needle.

        Warns:
            Needle_Holds_Too_Many_Loops: If adding these loops would exceed maximum loop count.
        """
        needle = self[needle]  # make sure needle instance is the one in the machine bed state
        assert isinstance(needle, Needle)
        if drop_prior_loops:
            self.drop(needle)
        needle.add_loops(loops)
        if len(needle.held_loops) >= self._knitting_machine.machine_specification.maximum_loop_hold:
            warnings.warn(
                Needle_Holds_Too_Many_Loops(needle, self._knitting_machine.machine_specification.maximum_loop_hold),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )
        if isinstance(needle, Slider_Needle):
            self._active_sliders.add(needle)
        for loop in loops:
            assert loop.holding_needle == needle, "Needle must be recorded in loop history"
        return loops

    def drop(self, needle: Needle) -> list[Machine_Knit_Loop]:
        """Clear the loops held at this position as though a drop operation has been done.

        Args:
            needle (Needle): The position to drop loops from main and slider needles.

        Returns:
            list[Machine_Knit_Loop]: List of loops that were dropped.
        """
        needle = self[needle]  # make sure the correct needle instance in machine bed state is used
        assert isinstance(needle, Needle)
        loops = list(needle.held_loops)
        needle.drop()
        if needle in self._active_sliders:
            assert isinstance(needle, Slider_Needle)
            self._active_sliders.remove(needle)
        return loops

    @property
    def sliders_are_clear(self) -> bool:
        """Check if no loops are on any slider needle.

        Returns:
            bool: True if no loops are on a slider needle, False otherwise.
        """
        return len(self._active_sliders) == 0

    def __len__(self) -> int:
        """Get the number of needles on this bed.

        Returns:
            int: Number of needles on the bed.
        """
        return self.needle_count

    def __iter__(self) -> Iterator[Needle]:
        """Iterate over the needles in this bed.

        Returns:
            Iterator[Needle]: Iterator over the needles on this bed.
        """
        return iter(self.needles)

    def __contains__(self, item: Machine_Knit_Loop | Needle | int | slice) -> bool:
        """
        Args:
            item (Machine_Knit_Loop | Needle | int | slice): The value to find in the needle bed.

        Returns:
            bool:
                True if the item is in the bed, False otherwise.
                Integer and Slices are checked against the range of the needle bed.
                Needles are checked against range and bed position.
                Loops are checked to see if they are being held on this bed.
        """
        if isinstance(item, Needle):
            return item.is_front == self.is_front and int(item) in self
        elif isinstance(item, int):
            if item < 0:  # allow negative indexing in slices and integers.
                return abs(item) <= self.needle_count
            else:
                return 0 <= item < self.needle_count
        elif isinstance(item, slice):
            return item.start in self and item.stop in self
        else:  # Machine Knit Loop
            holding_needle = item.holding_needle
            if holding_needle is None:
                return False
            else:
                return holding_needle in self

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> None | Needle:
        """
        Args:
            loop (Machine_Knit_Loop): The loop being searched for.

        Returns:
            None | Needle: None if the bed does not hold the loop, otherwise the needle position that holds it.
        """
        if loop in self:
            return loop.holding_needle
        else:
            return None

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle | None: ...

    @overload
    def __getitem__(self, item: Needle | int) -> Needle: ...

    @overload
    def __getitem__(self, item: slice) -> list[Needle]: ...

    def __getitem__(self, item: Machine_Knit_Loop | Needle | slice | int) -> Needle | list[Needle] | None:
        """Get an indexed needle on the bed, or find needle holding a specific loop.

        Args:
            item (Machine_Knit_Loop | Needle | slice | int): The needle position to get, loop to find needle for, or slice for multiple needles.

        Returns:
            Needle | list[Needle] | None: The needle(s) at the specified position(s) or holding the specified loop.

        Raises:
            KeyError: If needle position is out of range or the loop is not held on this bed.
        """
        if item not in self:
            if isinstance(item, Machine_Knit_Loop):
                raise KeyError(f"{item} is not an active loop on this bed")
            elif isinstance(item, Needle):
                raise KeyError(f"Needle {item} is out of range of the needle bed of size {self.needle_count}")
            else:
                raise KeyError(f"{item} is outside the range of this needle bed.")
        if isinstance(item, (int, slice)):
            return self.needles[item]
        elif isinstance(item, Machine_Knit_Loop):
            return self.get_needle_of_loop(item)
        else:  # isinstance(item, Needle):
            if item.is_slider:
                return self.sliders[item.position]
            else:
                return self.needles[item.position]
