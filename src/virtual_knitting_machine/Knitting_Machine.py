"""Module containing the Knitting_Machine class for virtual knitting machine representation and operations.

This module provides the main Knitting_Machine class which serves as the central coordinator for all
knitting operations, managing needle beds, carriage movement, yarn carriers, and knit graph construction.
"""

from __future__ import annotations

import warnings
from collections.abc import Container, Sequence
from typing import Protocol, TypeVar, overload

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.knitting_machine_exceptions.racking_errors import Max_Rack_Exception
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Knit_on_Empty_Needle_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage, Carriage_State
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.Needle_Bed import Needle_Bed, Needle_Bed_State
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier, Yarn_Carrier_State
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import (
    Carrier_State_Type,
    Yarn_Insertion_System,
    Yarn_Insertion_System_State,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import (
    Knitting_Machine_Error_Policy,
    Machine_State_With_Policy,
    checked_operation,
)

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Knitting_Machine_State(Machine_State_With_Policy, Container, Protocol[Machine_LoopT, Carrier_State_Type]):
    """
    Protocol defines all the readable attributes and properties of a knitting machine used to determine its current state.
    """

    @property
    def machine_specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The specification of this machine.
        """
        ...

    @property
    def knit_graph(self) -> Knit_Graph[Machine_LoopT]:
        """
        Returns:
            Knit_Graph: The knit graph formed on this machine.
        """
        ...

    @property
    def carrier_system(self) -> Yarn_Insertion_System_State[Machine_LoopT, Carrier_State_Type]:
        """
        Returns:
            Yarn_Insertion_System_State[Carrier_State_Type]: The carrier system used by the knitting machine.
        """
        ...

    @property
    def carriage(self) -> Carriage_State:
        """
        Returns:
            Carriage_State: The carriage that activates needle operations on this machine.
        """
        ...

    @property
    def front_bed(self) -> Needle_Bed_State[Machine_LoopT]:
        """
        Returns:
            Needle_Bed_State: The front bed of needles and slider needles in this machine.
        """
        ...

    @property
    def back_bed(self) -> Needle_Bed_State[Machine_LoopT]:
        """
        Returns:
            Needle_Bed_State: The back bed of needles and slider needles in this machine.
        """
        ...

    @property
    def gauged_layers(self) -> int:
        """
        Returns:
            int: The number of gauged layers the machine is set to.
        """

    @property
    def all_needle_rack(self) -> bool:
        """Check if racking is aligned for all needle knitting.

        Returns:
            bool: True if racking is aligned for all needle knitting, False otherwise.
        """
        ...

    @property
    def rack(self) -> int:
        """Get the current rack value of the machine.

        Returns:
            int: The current rack value of the machine.
        """
        ...

    @property
    def needle_count(self) -> int:
        """Get the needle width of the machine.

        Returns:
            int: The needle width of the machine.
        """
        return self.machine_specification.needle_count

    @property
    def max_rack(self) -> int:
        """Get the maximum distance that the machine can rack.

        Returns:
            int: The maximum distance that the machine can rack.
        """
        return self.machine_specification.maximum_rack

    @property
    def sliders_are_clear(self) -> bool:
        """Check if no loops are on any slider needle and knitting can be executed.

        Returns:
            bool:
                True if no loops are on a slider needle and knitting can be executed, False otherwise.
        """
        return bool(self.front_bed.sliders_are_clear and self.back_bed.sliders_are_clear)

    @property
    def slot_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range of needle slots holding loops. The first value is the left most slot. The second value is the right most slot.

        Notes:
            If there are no active loops, the slot range is (0, 0).
        """
        if len(self.all_loops()) == 0 and len(self.all_slider_loops()) == 0:
            return 0, 0
        slots = [n.slot_number for n in self.all_loops()]
        slots.extend(n.slot_number for n in self.all_slider_loops())
        return min(slots), max(slots)

    def front_needles(self) -> list[Needle[Machine_LoopT]]:
        """Get list of all front bed needles.

        Returns:
            list[Needle]: List of all front bed needles.
        """
        return self.front_bed.needles

    def front_sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of all front bed slider needles.

        Returns:
            list[Slider_Needle]: List of slider needles on front bed.
        """
        return self.front_bed.sliders

    def back_needles(self) -> list[Needle[Machine_LoopT]]:
        """Get list of all back bed needles.

        Returns:
            list[Needle]: List of all back bed needles.
        """
        return self.back_bed.needles

    def back_sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of all back bed slider needles.

        Returns:
            list[Slider_Needle]: List of slider needles on back bed.
        """
        return self.back_bed.sliders

    def front_loops(self) -> list[Needle[Machine_LoopT]]:
        """Get list of front bed needles that currently hold loops.

        Returns:
            list[Needle]: List of front bed needles that currently hold loops.
        """
        return self.front_bed.loop_holding_needles

    def front_slider_loops(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of front slider needles that currently hold loops.

        Returns:
            list[Slider_Needle]: List of front slider needles that currently hold loops.
        """
        return self.front_bed.loop_holding_sliders

    def back_loops(self) -> list[Needle[Machine_LoopT]]:
        """Get list of back bed needles that currently hold loops.

        Returns:
            list[Needle]: List of back bed needles that currently hold loops.
        """
        return self.back_bed.loop_holding_needles

    def back_slider_loops(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of back slider needles that currently hold loops.

        Returns:
            list[Slider_Needle]: List of back slider needles that currently hold loops.
        """
        return self.back_bed.loop_holding_sliders

    def all_needles(self) -> list[Needle[Machine_LoopT]]:
        """Get list of all needles with front bed needles given first.

        Returns:
            list[Needle]: List of all needles with front bed needles given first.
        """
        return [*self.front_needles(), *self.back_needles()]

    def all_sliders(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of all slider needles with front bed sliders given first.

        Returns:
            list[Slider_Needle]: List of all slider needles with front bed sliders given first.
        """
        return [*self.front_sliders(), *self.back_sliders()]

    def all_loops(self) -> list[Needle[Machine_LoopT]]:
        """Get list of all needles holding loops with front bed needles given first.

        Returns:
            list[Needle]: List of all needles holding loops with front bed needles given first.
        """
        return [*self.front_loops(), *self.back_loops()]

    def all_slider_loops(self) -> list[Slider_Needle[Machine_LoopT]]:
        """Get list of all slider needles holding loops with front bed sliders given first.

        Returns:
            list[Slider_Needle]:
                List of all slider needles holding loops with front bed sliders given first.
        """
        return [*self.front_slider_loops(), *self.back_slider_loops()]

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> Needle[Machine_LoopT] | None:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to search for.

        Returns:
            Needle | None: The needle holding the loop or None if it is not held.
        """
        if loop.holding_needle is None:
            return None
        elif loop.holding_needle.is_front:
            return self.front_bed.get_needle_of_loop(loop)
        else:
            return self.back_bed.get_needle_of_loop(loop)

    def has_loop(self, loop: Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (Machine_Knit_Loop): The loop to search for.

        Returns:
            bool: True if the loop is held on a needle. False otherwise.
        """
        if loop.holding_needle is None:
            return False
        elif loop.holding_needle.is_front:
            return loop in self.front_bed
        else:
            return loop in self.back_bed

    def has_needle(self, needle: Needle) -> bool:
        """
        Args:
            needle (Needle): The needle to search for.

        Returns:
            bool: True if the given needle is on a needle bed. False otherwise.
        """
        if needle.is_front:
            return int(needle) in self.front_bed
        else:
            return int(needle) in self.back_bed

    def get_front_needle(self, position: int, is_slider: bool = False) -> Needle[Machine_LoopT]:
        """
        Args:
            position (int): The position of the needle.
            is_slider (bool): True if the needle is on a slider. Defaults to False.

        Returns:
            Needle[Machine_LoopT]: The specified front bed needle.
        """
        if is_slider:
            return self.front_bed.sliders[position]
        else:
            return self.front_bed[position]

    def get_back_needle(self, position: int, is_slider: bool = False) -> Needle[Machine_LoopT]:
        """
        Args:
            position (int): The position of the needle.
            is_slider (bool): True if the needle is on a slider. Defaults to False.

        Returns:
            Needle[Machine_LoopT]: The specified back bed needle.
        """
        if is_slider:
            return self.back_bed.sliders[position]
        else:
            return self.back_bed[position]

    def get_specified_needle(self, is_front: bool, position: int, is_slider: bool = False) -> Needle[Machine_LoopT]:
        """
        Args:
            is_front (bool): If True, get a front bed needle.:
            position (int): The position of the needle.
            is_slider (bool, optional): If True get a slider needle. Defaults to False.

        Returns:
            Needle[Machine_LoopT]: The specified needle on this machine.
        """
        if is_front:
            return self.get_front_needle(position, is_slider)
        else:
            return self.get_back_needle(position, is_slider)

    def get_needle(self, needle: Needle) -> Needle[Machine_LoopT]:
        """Get the needle on this knitting machine at the given needle location.

        Args:
            needle (Needle): The needle to find on this specific machine.

        Returns:
            Needle: The needle on this knitting machine at the given needle location.
        """
        if needle.is_front:
            return self.front_bed[needle]
        else:
            return self.back_bed[needle]

    @property
    def active_loops(self) -> set[Machine_LoopT]:
        """
        Returns:
            set[Machine_Knit_Loop]: The set of loops currently held on a needle.
        """
        loops = set()
        loops.update(self.front_bed.active_loops)
        loops.update(self.front_bed.active_slider_loops)
        loops.update(self.back_bed.active_loops)
        loops.update(self.back_bed.active_slider_loops)
        return loops

    def active_floats(self) -> list[tuple[Machine_LoopT, Machine_LoopT]]:
        """
        Returns:
            list[tuple[Machine_Knit_Loop, Machine_Knit_Loop]]: List of all active floats between two active loops currently held on the needle beds.
        """
        floats = [(l, l.next_loop_on_yarn) for l in self.active_loops]
        return [(l, nl) for l, nl in floats if isinstance(nl, Machine_Knit_Loop) and nl in self.active_loops]

    def loops_crossed_by_float(self, loop1: Machine_Knit_Loop, loop2: Machine_Knit_Loop) -> set[Machine_LoopT]:
        """
        Args:
            loop1 (Machine_Knit_Loop): First loop in the float.
            loop2 (Machine_Knit_Loop): Second loop in the float.

        Returns:
            set[Machine_Knit_Loop]: The set of machine knit loops that are held on needles crossed by the given float.
        """
        needle1 = self[loop1]
        assert needle1 is not None
        needle2 = self[loop2]
        assert needle2 is not None
        left_slot = min(needle1.slot_number, needle2.slot_number)
        right_slot = max(needle1.slot_number, needle2.slot_number)
        return {
            l
            for l in self.active_loops
            if l.holding_needle is not None and left_slot < self[l.holding_needle].slot_number < right_slot
        }

    def get_carrier(
        self,
        carrier: (
            int | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State] | Sequence[int] | Sequence[Yarn_Carrier_State]
        ),
    ) -> Carrier_State_Type | list[Carrier_State_Type]:
        """Get the carrier or list of carriers owned by the machine at the given specification.

        Args:
            carrier (int | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State]):
                The carrier defined by a given carrier, carrier_set, integer or list of integers to form a set.

        Returns:
            Carrier_State_Type | list[Carrier_State_Type]:
                The carrier or list of carriers owned by the machine at the given specification.
        """
        return self.carrier_system[carrier]

    def get_aligned_needle(self, needle: Needle, aligned_slider: bool = False) -> Needle[Machine_LoopT]:
        """
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
        return self.get_specified_needle(not needle.is_front, aligned_position, aligned_slider)

    def valid_rack(self, front_pos: int, back_pos: int) -> bool:
        """Check if transfer can be completed at current racking.

        Args:
            front_pos (int): The front needle in the racking.
            back_pos (int): The back needle in the racking.

        Returns:
            bool: True if the current racking can make this transfer, False otherwise.
        """
        needed_rack = Knitting_Machine.get_rack(front_pos, back_pos)
        return self.rack == needed_rack

    def __contains__(self, item: object) -> bool:
        """
        Args:
            item (Needle | Machine_Knit_Loop | Yarn_Carrier_State | Sequence[int | Yarn_Carrier_State]): The item to search for.

        Returns:
            bool: True if the given needle or loop are on one of the needle beds or if the given carriers are all in the carrier system. Other items will return False.
        """
        if isinstance(item, Needle):
            return self.has_needle(item)
        elif isinstance(item, Machine_Knit_Loop):
            return self.has_loop(item)
        elif isinstance(item, Sequence):
            if not all(isinstance(i, (int, Yarn_Carrier_State)) for i in item):
                return False
            return item in self.carrier_system
        else:
            return False

    @overload
    def __getitem__(self, item: Machine_Knit_Loop) -> Needle[Machine_LoopT] | None: ...

    @overload
    def __getitem__(self, item: Needle) -> Needle[Machine_LoopT]: ...

    @overload
    def __getitem__(self, item: Yarn_Carrier_State) -> Carrier_State_Type: ...

    @overload
    def __getitem__(
        self, item: Sequence[int | Yarn_Carrier_State] | Sequence[Yarn_Carrier_State] | Sequence[int]
    ) -> list[Carrier_State_Type]: ...

    def __getitem__(
        self,
        item: (
            Needle
            | Yarn_Carrier_State
            | Sequence[int | Yarn_Carrier_State]
            | Sequence[int]
            | Sequence[Yarn_Carrier_State]
            | Machine_Knit_Loop
        ),
    ) -> Needle[Machine_LoopT] | Carrier_State_Type | list[Carrier_State_Type] | None:
        """Access needles, carriers, or find needles holding loops on the machine.

        Args:
            item (Needle | Yarn_Carrier_State | Yarn_Carrier_Set | Sequence[int | Yarn_Carrier_State] | Machine_Knit_Loop):
                A needle, yarn carrier, carrier set, or loop to reference in the machine.

        Returns:
            Needle | Yarn_Carrier_State | list[Yarn_Carrier_State] | None:
                The needle on the machine at the given needle position,
                or if given yarn carrier information return the corresponding carrier or carriers on the machine,
                or if given a loop return the corresponding needle that holds this loop or None if the loop is not held on a needle.

        Raises:
            KeyError: If the item cannot be accessed from the machine.
        """
        if isinstance(item, Machine_Knit_Loop):
            return self.get_needle_of_loop(item)
        elif isinstance(item, Needle):
            return self.get_needle(item)
        elif isinstance(item, (Yarn_Carrier_State, Sequence)):
            return self.carrier_system[item]
        raise KeyError(f"Could not access {item} from machine.")

    def __len__(self) -> int:
        """Get the needle bed width of the machine.

        Returns:
            int: The needle bed width of the machine.
        """
        return self.needle_count


class Knitting_Machine(Knitting_Machine_State[Machine_LoopT, Yarn_Carrier]):
    """A virtual representation of a V-Bed WholeGarment knitting machine.

    This class provides comprehensive functionality for simulating knitting operations including
    needle management, carriage control, yarn carrier operations, racking, and knit graph construction
    with support for all standard knitting operations like knit, tuck, transfer, split, and miss.
    """

    def __init__(
        self,
        machine_specification: Knitting_Machine_Specification | None = None,
        knit_graph: Knit_Graph[Machine_LoopT] | None = None,
        violation_policy: Knitting_Machine_Error_Policy | None = None,
    ) -> None:
        """Initialize a virtual knitting machine with specified configuration.

        Args:
            machine_specification (Knitting_Machine_Specification, optional): Configuration parameters for the machine. Defaults to Knitting_Machine_Specification().
            knit_graph (Knit_Graph | None, optional): Existing knit graph to use, creates new one if None. Defaults to None.
        """
        self._gauge: int = 1
        self._violation_policy: Knitting_Machine_Error_Policy = (
            violation_policy if violation_policy is not None else Knitting_Machine_Error_Policy()
        )
        self._machine_specification: Knitting_Machine_Specification = (
            machine_specification if machine_specification is not None else Knitting_Machine_Specification()
        )
        if knit_graph is None:
            knit_graph = Knit_Graph[Machine_LoopT]()
        self._knit_graph: Knit_Graph[Machine_LoopT] = knit_graph
        self._front_bed: Needle_Bed[Machine_LoopT] = Needle_Bed[Machine_LoopT](is_front=True, knitting_machine=self)
        self._back_bed: Needle_Bed[Machine_LoopT] = Needle_Bed[Machine_LoopT](is_front=False, knitting_machine=self)
        self._carrier_system: Yarn_Insertion_System[Machine_LoopT] = Yarn_Insertion_System[Machine_LoopT](
            self, self.machine_specification.carrier_count
        )
        self._carriage: Carriage = Carriage(self)
        self._rack: int = 0
        self._all_needle_rack: bool = False

    @property
    def violation_policy(self) -> Knitting_Machine_Error_Policy:
        """
        Returns:
            Knitting_Machine_Error_Policy: The policy for handling machine state errors.
        """
        return self._violation_policy

    @property
    def machine_specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The specification of this machine.
        """
        return self._machine_specification

    @property
    def knit_graph(self) -> Knit_Graph[Machine_LoopT]:
        """
        Returns:
            Knit_Graph: The knit graph formed on this machine.
        """
        return self._knit_graph

    @property
    def carrier_system(self) -> Yarn_Insertion_System[Machine_LoopT]:
        """Get the carrier system used by the knitting machine.

        Returns:
            Yarn_Insertion_System: The carrier system used by the knitting machine.
        """
        return self._carrier_system

    @property
    def carriage(self) -> Carriage:
        """
        Returns:
            Carriage: The carriage that activates needle operations on this machine.
        """
        return self._carriage

    @property
    def front_bed(self) -> Needle_Bed[Machine_LoopT]:
        """
        Returns:
            Needle_Bed: The front bed of needles and slider needles in this machine.
        """
        return self._front_bed

    @property
    def back_bed(self) -> Needle_Bed[Machine_LoopT]:
        """
        Returns:
            Needle_Bed: The back bed of needles and slider needles in this machine.
        """
        return self._back_bed

    @property
    def gauged_layers(self) -> int:
        return self._gauge

    @gauged_layers.setter
    def gauged_layers(self, gauge: int) -> None:
        self._gauge = max(1, gauge)  # clamp to 1 layer

    @property
    def all_needle_rack(self) -> bool:
        """Check if racking is aligned for all needle knitting.

        Returns:
            bool: True if racking is aligned for all needle knitting, False otherwise.
        """
        return self._all_needle_rack

    @property
    def rack(self) -> int:
        """Get the current rack value of the machine.

        Returns:
            int: The current rack value of the machine.
        """
        return self._rack

    @rack.setter
    @checked_operation
    def rack(self, new_rack: float) -> None:
        """Set the rack value with support for all-needle racking.

        Args:
            new_rack (float): The new rack value to set.

        Raises:
            Max_Rack_Exception: If the absolute rack value exceeds the maximum allowed rack.
        """
        with self.handle_violations():
            if abs(new_rack) > self.max_rack:
                raise Max_Rack_Exception(new_rack, self.max_rack)
        if self.violation_policy.proceed:
            self._all_needle_rack = abs(new_rack - int(new_rack)) != 0.0
            if new_rack < 0 and self.all_needle_rack:
                self._rack = int(new_rack) - 1
            else:
                self._rack = int(new_rack)

    def update_rack(self, front_pos: int, back_pos: int) -> bool:
        """Update the current racking to align front and back needle positions.

        Args:
            front_pos (int): Front needle to align.
            back_pos (int): Back needle to align.

        Returns:
            bool: True if the rack was updated to a new value, False if no change.
        """
        original = self.rack
        self.rack = self.get_rack(front_pos, back_pos)
        return original != self.rack

    @staticmethod
    def get_rack(front_pos: int, back_pos: int) -> int:
        """Calculate racking between front and back position using formula R = F - B, F = R + B, B = F - R.

        Args:
            front_pos (int): Front aligned needle position.
            back_pos (int): Back aligned needle position.

        Returns:
            int: Racking needed to transfer from front position to back position.
        """
        return front_pos - back_pos

    @staticmethod
    def get_transfer_rack(start_needle: Needle, target_needle: Needle) -> int | None:
        """Calculate the racking value needed to make transfer between start and target needle.

        Args:
            start_needle (Needle): Needle currently holding loops to transfer.
            target_needle (Needle): Needle to transfer loops to.

        Returns:
            int:
                Racking value needed to make transfer between start and target needle,
                None if no racking can be made because needles are on the same bed.

        Raises:
            ValueError: If the needles are on the same bed and therefor cannot be aligned by racking.
        """
        if start_needle.is_front == target_needle.is_front:
            raise ValueError(
                f"{start_needle} and {target_needle} cannot be aligned by racking because they are on the same bed."
            )
        elif start_needle.is_front:
            return Knitting_Machine.get_rack(start_needle.position, target_needle.position)
        else:
            return Knitting_Machine.get_rack(target_needle.position, start_needle.position)

    def in_hook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Declare that the in_hook for this yarn carrier is in use.

        Args:
            carrier_id (int | Yarn_Carrier): The yarn_carrier to bring in.
        """
        self.carrier_system.inhook(carrier_id)

    def release_hook(self) -> None:
        """Declare that the in-hook is not in use but yarn remains in use."""
        self.carrier_system.releasehook()

    def out_hook(self, carrier_id: int | Yarn_Carrier) -> None:
        """Declare that the yarn is no longer in service and will need to be in-hooked to use.

        Args:
            carrier_id (int | Yarn_Carrier): The yarn carrier to remove from service.
        """
        self.carrier_system.outhook(carrier_id)

    def bring_in(self, carrier_id: int | Yarn_Carrier) -> None:
        """Bring the yarn carrier into action.

        Args:
            carrier_id (int | Yarn_Carrier): The yarn carrier to bring in.
        """
        self.carrier_system.bring_in(carrier_id)

    def out(self, carrier_id: int | Yarn_Carrier) -> None:
        """Move the yarn_carrier out of action.

        Args:
            carrier_id (int | Yarn_Carrier): The yarn carrier to move out.
        """
        self.carrier_system.out(carrier_id)

    def tuck(
        self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction
    ) -> list[Machine_LoopT]:
        """Place loops made with carriers in the carrier set on the given needle.

        Args:
            carrier_set (Yarn_Carrier_Set): Set of yarns to make loops with.
            needle (Needle): Needle to make loops on.
            direction (Carriage_Pass_Direction): The direction to tuck in.

        Returns:
            list[Machine_Knit_Loop]: List of new loops made by tucking.
        """
        self.miss(carrier_set, needle, direction)  # aligns the carriers and completes the carriage movement.
        needle = self[needle]
        new_loops: list[Machine_LoopT] = self.carrier_system.make_loops(carrier_set, needle, direction)
        if needle.is_front:
            self.front_bed.add_loops(needle, new_loops, drop_prior_loops=False)
        else:
            self.back_bed.add_loops(needle, new_loops, drop_prior_loops=False)
        return new_loops

    def knit(
        self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction
    ) -> tuple[list[Machine_LoopT], list[Machine_LoopT]]:
        """Form new loops from the carrier set by pulling them through all loops on the given needle.

        Drop the existing loops and hold the new loops on the needle.

        Args:
            carrier_set (Yarn_Carrier_Set): Set of yarns to make loops with.
            needle (Needle): Needle to knit on.
            direction (Carriage_Pass_Direction): The direction to knit in.

        Returns:
            tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
                Tuple containing list of loops stitched through and dropped off needle by knitting process,
                and list of loops formed in the knitting process.

        Warns:
            Knit_on_Empty_Needle_Warning: If attempting to knit on a needle with no loops.
        """
        # Get the needle in the machine state
        needle = self[needle]
        if not needle.has_loops:
            warnings.warn(
                Knit_on_Empty_Needle_Warning(needle),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )

        # position the carrier set to align with the knitting needle
        self.miss(carrier_set, needle, direction)
        # Drop and save the current loops, then add the child loops onto this needle.
        bed = self.front_bed if needle.is_front else self.back_bed
        parent_loops = bed.drop(needle)
        # Make child loops by this specification
        child_loops = self.carrier_system.make_loops(carrier_set, needle, direction)
        bed.add_loops(needle, child_loops, drop_prior_loops=False)  # drop should have occurred in prior line

        # Create stitches in the knitgraph.
        for parent in parent_loops:
            for child in child_loops:
                self.knit_graph.connect_loops(parent, child, needle.pull_direction)
        return parent_loops, child_loops

    def drop(self, needle: Needle) -> list[Machine_LoopT]:
        """Drop all loops currently on given needle.

        Args:
            needle (Needle): The needle to drop from.

        Returns:
            list[Machine_Knit_Loop]: The list of loops dropped.

        Note:
            The direction of drop operations is not recorded, just like transfer operations.
            This enables easy tracking of relative movements that involve carriers.
        """
        needle = self[needle]
        self.carriage.move_to_needle(needle)
        return needle.drop()

    def _add_xfer_crossing(
        self, left_loop: Machine_LoopT, right_loop: Machine_LoopT, crossing_direction: Crossing_Direction
    ) -> None:
        """
        Add a crossing to the knit_graph's braid graph based on a transfer of the left loop (over or under) the right loop.
        If this crossing would undo a prior crossing, the prior crossing edge is removed.

        Args:
            left_loop: The loop involved in the crossing that starts on the left of the crossing.
            right_loop: The loop involved in the crossing that starts on the right of the crossing.
            crossing_direction: The direction of the crossing.
        """
        if self.knit_graph.braid_graph.has_edge(right_loop, left_loop):
            current_crossing = self.knit_graph.braid_graph.get_crossing(right_loop, left_loop)
            if current_crossing.opposite == crossing_direction:  # inverted crossing direction
                self.knit_graph.braid_graph.remove_edge(right_loop, left_loop)
            else:
                self.knit_graph.add_crossing(right_loop, left_loop, crossing_direction.opposite)
        else:
            self.knit_graph.add_crossing(left_loop, right_loop, crossing_direction)

    def _cross_loops_by_rightward_xfer(
        self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_LoopT]
    ) -> None:
        """
        Update the knitgraph's braid graph with a loop crossing created by a rightward crossing from the starting_needle to the aligned needle in a transfer.

        Args:
            starting_needle: The needle holding loops at the start of the transfer.
            aligned_needle: The needle receiving loops in the transfer.
            xfer_loops: The loops being transferred.
        """
        starting_position = starting_needle.slot_number
        front_crossed_positions = [
            f
            for f in self.front_bed[starting_position : starting_position + abs(self.rack) + 1]
            if f != starting_needle and f != aligned_needle and f.has_loops
        ]
        for n in front_crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    # cross the transferred loops to right, under the cross loops on the front bed.
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Under_Right)
        back_crossed_positions = [
            b
            for b in self.back_bed[starting_position : starting_position + abs(self.rack) + 1]
            if b != starting_needle and b != aligned_needle and b.has_loops
        ]
        for n in back_crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    # cross the transferred loops to the right, over the cross loops on the back bed.
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Over_Right)

    def _cross_loops_by_leftward_xfer(
        self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_LoopT]
    ) -> None:
        """
        Update the knitgraph's braid graph with a loop crossing created by a leftward crossing from the starting_needle to the aligned needle in a transfer.

        Args:
            starting_needle: The needle holding loops at the start of the transfer.
            aligned_needle: The needle receiving loops in the transfer.
            xfer_loops: The loops being transferred.
        """
        starting_position = starting_needle.slot_number
        front_crossed_positions = [
            f
            for f in self.front_bed[starting_position - self.rack : starting_position + 1]
            if f != starting_needle and f != aligned_needle and f.has_loops
        ]
        for n in front_crossed_positions:
            for right_loop in xfer_loops:
                for left_loop in n.held_loops:
                    # cross the crossed loops on the front bed to the right, over the transferred loops
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Over_Right)
        back_crossed_positions = [
            b
            for b in self.back_bed[starting_position - self.rack : starting_position + 1]
            if b != starting_needle and b != aligned_needle and b.has_loops
        ]
        for n in back_crossed_positions:
            for right_loop in xfer_loops:
                for left_loop in n.held_loops:
                    # cross the crossed loops on the back bed to the right, under the transferred loops
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Under_Right)

    def _cross_loops_by_xfer(
        self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_LoopT]
    ) -> None:
        """
        Update the knitgraph's braid graph with a loop crossing created by a transfer from the starting_needle to the aligned needle.

        Args:
            starting_needle: The needle holding loops at the start of the transfer.
            aligned_needle: The needle receiving loops in the transfer.
            xfer_loops: The loops being transferred.
        """
        if self.rack < 0:  # rightward xfer
            self._cross_loops_by_rightward_xfer(starting_needle, aligned_needle, xfer_loops)
        elif self.rack > 0:  # leftward xfer
            self._cross_loops_by_leftward_xfer(starting_needle, aligned_needle, xfer_loops)

    def xfer(self, starting_needle: Needle, to_slider: bool = False, from_split: bool = False) -> list[Machine_LoopT]:
        """Move all loops on starting_needle to aligned needle at current racking.

        Args:
            starting_needle (Needle): Needle to move loops from.
            to_slider (bool, optional): If True, loops are moved to a slider. Defaults to False.
            from_split (bool, optional):
                If True, this transfer is part of a split and does not move the carriage. Defaults to False.

        Returns:
            list[Machine_Knit_Loop]: The list of loops that are transferred.
        """
        # Get the needle and aligned needle in the current machine state.
        starting_needle = self[starting_needle]  # get needle on the machine.
        aligned_needle = self[self.get_aligned_needle(starting_needle, to_slider)]  # get needle on the machine.

        # Drop the loops from the starting bed and add them to the aligned needle on the opposite bed.
        if starting_needle.is_front:
            held_loops = self.front_bed.drop(starting_needle)
            for loop in held_loops:  # Update loop's needle history
                loop.reverse_drop()
                loop.transfer_loop(aligned_needle)
            xfer_loops: list[Machine_LoopT] = self.back_bed.add_loops(
                aligned_needle, held_loops, drop_prior_loops=False
            )
        else:
            held_loops = self.back_bed.drop(starting_needle)
            for loop in held_loops:  # Update loop's needle history
                loop.reverse_drop()
                loop.transfer_loop(aligned_needle)
            xfer_loops: list[Machine_LoopT] = self.front_bed.add_loops(
                aligned_needle, held_loops, drop_prior_loops=False
            )

        self._cross_loops_by_xfer(starting_needle, aligned_needle, xfer_loops)

        if not from_split:
            self.carriage.move_to_needle(starting_needle)
        return xfer_loops

    def split(
        self, carrier_set: Yarn_Carrier_Set, starting_needle: Needle, direction: Carriage_Pass_Direction
    ) -> tuple[list[Machine_LoopT], list[Machine_LoopT]]:
        """Pull a loop formed in direction by the yarns in carriers through the loops on needle.

        Transfer the old loops to opposite-bed needle in the process.

        Args:
            carrier_set (Yarn_Carrier_Set): Set of yarns to make loops with.
            starting_needle (Needle): The needle to transfer old loops from and to form new loops on.
            direction (Carriage_Pass_Direction): The carriage direction for the split operation.

        Returns:
            tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
                Tuple containing the list of loops created by the split and the list of loops transferred.

        Note:
            From the Knitout Documentation:
            Splitting with an empty carrier set will transfer.
            This transfers loops on starting needle to aligned needle at this racking
            then forms new loops pulled through the transferred loops and holds them on the starting needle.
        """
        parent_loops = self.xfer(starting_needle, to_slider=False, from_split=True)
        child_loops = self.tuck(
            carrier_set, starting_needle, direction
        )  # tuck new loops onto the needle after completing the transfer

        # Form the stitch between the transferred and created loops
        for parent in parent_loops:
            for child in child_loops:
                self.knit_graph.connect_loops(parent, child, starting_needle.pull_direction)
        return child_loops, parent_loops

    def miss(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> None:
        """Set the carrier positions to hover above the given needle.

        Args:
            carrier_set (Yarn_Carrier_Set): Set of yarns to move.
            needle (Needle): Needle to position the carriers from.
            direction (Carriage_Pass_Direction): The carriage direction for the miss operation.
        """
        needle = self[needle]
        carrier_set.position_carriers_at_needle(self.carrier_system, needle, direction)
        self.carriage.move_in_direction(needle, direction)
