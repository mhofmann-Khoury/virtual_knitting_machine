"""Representation module for needle beds on knitting machines.
This module provides the Needle_Bed class which represents one bed of needles (front or back) on a knitting machine,
managing both regular needles and slider needles with their associated loops and operations."""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, overload

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Needle_Holds_Too_Many_Loops
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import (
    Knitting_Machine_Error_Policy,
    Machine_State_With_Policy,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine, Knitting_Machine_State

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Needle_Bed_State(Machine_State_With_Policy, Protocol[Machine_LoopT]):
    """Protocol for the readable properties of a needle bed."""

    @property
    def knitting_machine(self) -> Knitting_Machine_State[Machine_LoopT, Any]:
        """
        Returns:
            Knitting_Machine_State: The knitting machine this bed belongs to.
        """
        ...

    @property
    def violation_policy(self) -> Knitting_Machine_Error_Policy:
        """
        Returns:
            Knitting_Machine_Error_Policy: The policy for handling machine state errors.
        """
        return self.knitting_machine.violation_policy

    @property
    def is_front(self) -> bool:
        """Check if this is the front bed.

        Returns:
            bool: True if this is the front bed, False if back bed.
        """
        ...

    @property
    def needles(self) -> list[Needle[Machine_LoopT]]:
        """
        Returns:
            list[Needle]: The needles on this bed ordered from 0 to the needle count specified by the knitting machine.
        """
        ...

    @property
    def sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """
        Returns:
            list[Slider_Needle]: The slider needles on this bed ordered from 0 to the needle count specified by the knitting machine."
        """
        ...

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if this is the back bed, False if front bed.
        """
        return not self.is_front

    @property
    def needle_count(self) -> int:
        """
        Returns:
            int: The number of needles on the bed.
        """
        return self.knitting_machine.needle_count

    @property
    def loop_holding_needles(self) -> list[Needle[Machine_LoopT]]:
        """
        Returns:
            list[Needle]: List of needles on bed that actively hold loops.
        """
        return [n for n in self if n.has_loops]

    @property
    def loop_holding_sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """
        Returns:
            list[Slider_Needle]: List of sliders on bed that actively hold loops.
        """
        return [s for s in self.sliders if s.has_loops]

    @property
    def active_loops(self) -> set[Machine_LoopT]:
        """
        Returns:
            set[Machine_Knit_Loop]: The set of loops held on needles on the needle bed.
        """
        loops = set()
        for n in self.loop_holding_needles:
            loops.update(n.held_loops)
        return loops

    @property
    def active_slider_loops(self) -> set[Machine_LoopT]:
        """
        Returns:
            set[Machine_Knit_Loop]: The set of loops held on slider needles on the needle bed.
        """
        loops = set()
        for n in self.loop_holding_sliders:
            loops.update(n.held_loops)
        return loops

    @property
    def active_needle_count(self) -> int:
        """
        Returns:
            int: The number of active needles that hold loops.
        """
        return len(self.loop_holding_needles)

    @property
    def active_slider_count(self) -> int:
        """
        Returns:
            int: The number of active sliders that hold loops.
        """
        return len(self.loop_holding_sliders)

    @property
    def sliders_are_clear(self) -> bool:
        """Check if no loops are on any slider needle.

        Returns:
            bool: True if no loops are on a slider needle, False otherwise.
        """
        return self.active_slider_count == 0

    def loop_is_active(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to check if it is held by this bed.

        Returns:
            bool: True if the given loop is on held on a needle or slider needle, False otherwise.
        """
        return self.loop_on_needle(loop) or self.loop_on_slider(loop)

    def loop_on_slider(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to check if it is actively on a slider needle

        Returns:
            bool: True if the loop is on held on a slider needle. False, otherwise.
        """
        return loop in self.active_slider_loops

    def loop_on_needle(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to check if it is actively held by a needle

        Returns:
            bool: True if the loop is held by a needle. False, otherwise.
        """
        return loop in self.active_loops

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> Needle[Machine_LoopT] | None:
        """
        Args:
            loop (Machine_Knit_Loop): The loop being searched for.

        Returns:
            Needle | None: None if the bed does not hold the loop, otherwise the needle position that holds it.
        """
        return self[loop.holding_needle] if loop.holding_needle is not None and loop in self else None

    def slider_is_active(self, slider: int | Slider_Needle) -> bool:
        """
        Args:
            slider: The slider or index of a slider on this needle bed.

        Returns:
            bool: True if the given slider is on this bed and holds at least one loop, False otherwise.
        """
        return slider in self and self.sliders[int(slider)].has_loops

    def needle_is_active(self, needle: int | Needle) -> bool:
        """
        Args:
            needle: THe needle or index of a needl on this needle bed.

        Returns:
            bool: True if the given needle is on this bed and holds at least one loop, False otherwise.
        """
        return needle in self and self.needles[int(needle)].has_loops

    def __str__(self) -> str:
        bed = "Front" if self.is_front else "Back"
        return f"{bed}[0:{self.needle_count}]"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        """
        Returns:
            int: Number of needles on the bed.
        """
        return self.needle_count

    def __iter__(self) -> Iterator[Needle[Machine_LoopT]]:
        """Iterate over the needles in this bed.

        Returns:
            Iterator[Needle]: Iterator over the needles on this bed.
        """
        return iter(self.needles)

    def __contains__(self, item: object) -> bool:
        """
        Args:
            item (Machine_Knit_Loop | Needle | int): The value to find in the needle bed.

        Returns:
            bool:
                True if the item is in the bed, False otherwise.
                Integers are checked against the range of the needle bed.
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
        elif isinstance(item, Machine_Knit_Loop):
            holding_needle = item.holding_needle
            if holding_needle is None:
                return False
            else:
                return holding_needle in self
        else:
            return False

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle[Machine_LoopT] | None: ...

    @overload
    def __getitem__(self, item: Needle | int) -> Needle[Machine_LoopT]: ...

    @overload
    def __getitem__(self, item: slice) -> list[Needle[Machine_LoopT]]: ...

    def __getitem__(
        self, item: Machine_Knit_Loop | Needle | slice | int
    ) -> Needle[Machine_LoopT] | list[Needle[Machine_LoopT]] | None:
        """Get an indexed needle on the bed, or find needle holding a specific loop.

        Args:
            item (Machine_Knit_Loop | Needle | slice | int): The needle position to get, loop to find needle for, or slice for multiple needles.

        Returns:
            Needle | list[Needle] | None: The needle(s) at the specified position(s) or holding the specified loop.

        Raises:
            KeyError: If needle position is out of range or the loop is not held on this bed.
        """
        if isinstance(item, (Machine_Knit_Loop, Needle, int)) and item not in self:
            if isinstance(item, Machine_Knit_Loop):
                raise KeyError(f"{item} is not an active loop on the {self}")
            else:
                raise KeyError(f"Needle {item} is not on the {self}")
        if isinstance(item, (int, slice)):
            return self.needles[item]
        elif isinstance(item, Needle):
            if item.is_slider:
                return self.sliders[item.position]
            else:
                return self.needles[item.position]
        else:
            return self.get_needle_of_loop(item)


class Needle_Bed(Needle_Bed_State[Machine_LoopT]):
    """A structure to hold information about loops held on one bed of needles where increasing indices indicate needles moving from left to right (LEFT -> 0 1 2....N <- RIGHT of Machine).
    This class manages both regular needles and slider needles, tracks active sliders, and provides methods for loop manipulation and needle access operations.
    """

    def __init__(self, is_front: bool, knitting_machine: Knitting_Machine[Machine_LoopT]) -> None:
        """Initialize a needle bed representation for the machine.

        Args:
            is_front (bool): True if this is the front bed, False if it is the back bed.
            knitting_machine (Knitting_Machine): The knitting machine this bed belongs to.
        """
        self._knitting_machine: Knitting_Machine[Machine_LoopT] = knitting_machine
        self._is_front: bool = is_front
        self._needles: list[Needle] = [
            Needle(self._is_front, i, knitting_machine=self.knitting_machine) for i in range(0, self.needle_count)
        ]
        self._sliders: list[Slider_Needle] = [
            Slider_Needle(self._is_front, i, knitting_machine=self.knitting_machine)
            for i in range(0, self.needle_count)
        ]
        self._active_sliders: set[Slider_Needle] = set()

    @property
    def knitting_machine(self) -> Knitting_Machine[Machine_LoopT]:
        """
        Returns:
            Knitting_Machine: The knitting machine this bed belongs to.
        """
        return self._knitting_machine

    @property
    def is_front(self) -> bool:
        """Check if this is the front bed.

        Returns:
            bool: True if this is the front bed, False if back bed.
        """
        return self._is_front

    @property
    def needles(self) -> list[Needle[Machine_LoopT]]:
        """
        Returns:
            list[Needle]: The needles on this bed ordered from 0 to the needle count specified by the knitting machine.
        """
        return self._needles

    @property
    def sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """
        Returns:
            list[Slider_Needle]: The slider needles on this bed ordered from 0 to the needle count specified by the knitting machine."
        """
        return self._sliders

    @property
    def sliders_are_clear(self) -> bool:
        """Check if no loops are on any slider needle.

        Returns:
            bool: True if no loops are on a slider needle, False otherwise.
        """
        return len(self._active_sliders) == 0

    def add_loops(
        self, needle: Needle, loops: list[Machine_LoopT], drop_prior_loops: bool = True
    ) -> list[Machine_LoopT]:
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
        return loops

    def drop(self, needle: Needle) -> list[Machine_LoopT]:
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
