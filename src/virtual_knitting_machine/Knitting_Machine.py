"""Module containing the Knitting_Machine class for virtual knitting machine representation and operations.

This module provides the main Knitting_Machine class which serves as the central coordinator for all
knitting operations, managing needle beds, carriage movement, yarn carriers, and knit graph construction.
"""
from __future__ import annotations

import warnings
from collections import defaultdict
from typing import cast

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.knitting_machine_exceptions.racking_errors import (
    Max_Rack_Exception,
)
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import (
    Knit_on_Empty_Needle_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage import (
    Carriage,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.Needle_Bed import Needle_Bed
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import (
    Slider_Needle,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import (
    Yarn_Insertion_System,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import (
    Machine_Knit_Yarn,
)


class Knitting_Machine:
    """A virtual representation of a V-Bed WholeGarment knitting machine.

    This class provides comprehensive functionality for simulating knitting operations including
    needle management, carriage control, yarn carrier operations, racking, and knit graph construction
    with support for all standard knitting operations like knit, tuck, transfer, split, and miss.

    Attributes:
        machine_specification (Knitting_Machine_Specification): The specification to build this machine from.
        knit_graph (Knit_Graph): The knit graph that has been formed on the machine.
    """

    def __init__(self, machine_specification: Knitting_Machine_Specification = Knitting_Machine_Specification(), knit_graph: Knit_Graph | None = None) -> None:
        """Initialize a virtual knitting machine with specified configuration.

        Args:
            machine_specification (Knitting_Machine_Specification, optional):
                Configuration parameters for the machine. Defaults to Knitting_Machine_Specification().
            knit_graph (Knit_Graph | None, optional):
                Existing knit graph to use, creates new one if None. Defaults to None.
        """
        self.machine_specification: Knitting_Machine_Specification = machine_specification
        if knit_graph is None:
            knit_graph = Knit_Graph()
        self.knit_graph: Knit_Graph = knit_graph
        self._front_bed: Needle_Bed = Needle_Bed(is_front=True, knitting_machine=self)
        self._back_bed: Needle_Bed = Needle_Bed(is_front=False, knitting_machine=self)
        self._carrier_system: Yarn_Insertion_System = Yarn_Insertion_System(self, self.machine_specification.carrier_count)
        self._carriage: Carriage = Carriage(self, self.needle_count - 1)
        self._rack: int = 0
        self._all_needle_rack: bool = False

    @property
    def needle_count(self) -> int:
        """Get the needle width of the machine.

        Returns:
            int: The needle width of the machine.
        """
        return int(self.machine_specification.needle_count)

    @property
    def max_rack(self) -> int:
        """Get the maximum distance that the machine can rack.

        Returns:
            int: The maximum distance that the machine can rack.
        """
        return int(self.machine_specification.maximum_rack)

    def __len__(self) -> int:
        """Get the needle bed width of the machine.

        Returns:
            int: The needle bed width of the machine.
        """
        return self.needle_count

    def copy(self, starting_state: Knitting_Machine | None = None) -> Knitting_Machine:
        """Create a crude copy of this machine state with all relevant yarns inhooked and loops formed on required locations.

        Args:
            starting_state (Knitting_Machine | None, optional):
                A machine state to copy into, otherwise creates a new machine state with the same machine specification as this machine.
                Defaults to None.

        Returns:
            Knitting_Machine: A copy of the current machine state.

        Note:
            This copy does not guarantee continuity of the knitgraph structure or history,
            it only ensures loops and carriers are correctly positioned to mimic the current state.
        """
        if starting_state is None:
            copy_machine_state = Knitting_Machine(machine_specification=self.machine_specification)
        else:
            copy_machine_state = starting_state
        hold_to_hook = self.carrier_system.hooked_carrier
        for carrier in self.carrier_system.active_carriers:
            if carrier != hold_to_hook and not copy_machine_state.carrier_system.is_active([carrier.carrier_id]):
                copy_machine_state.in_hook(carrier.carrier_id)
                copy_machine_state.release_hook()
        if hold_to_hook is not None:
            copy_machine_state.in_hook(hold_to_hook.carrier_id)
        carrier_to_needles: dict[int, list[Needle]] = defaultdict(list)
        for needle in Carriage_Pass_Direction.Leftward.sort_needles(self.all_loops()):
            for loop in needle.held_loops:
                assert isinstance(loop, Machine_Knit_Loop)
                assert isinstance(loop.yarn, Machine_Knit_Yarn)
                carrier_to_needles[loop.yarn.carrier.carrier_id].append(needle)
        for cid, needles in carrier_to_needles.items():
            for needle in needles:
                copy_machine_state.tuck(Yarn_Carrier_Set([cid]), needle, Carriage_Pass_Direction.Leftward)
        return copy_machine_state

    @property
    def carrier_system(self) -> Yarn_Insertion_System:
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
    def front_bed(self) -> Needle_Bed:
        """
        Returns:
            Needle_Bed: The front bed of needles and slider needles in this machine.
        """
        return self._front_bed

    @property
    def back_bed(self) -> Needle_Bed:
        """
        Returns:
            Needle_Bed: The back bed of needles and slider needles in this machine.
        """
        return self._back_bed

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> None | Needle:
        """Get the needle holding the loop or None if it is not held.

        Args:
            loop (Machine_Knit_Loop): The loop to search for.

        Returns:
            None | Needle: The needle holding the loop or None if it is not held.
        """
        if loop.holding_needle is None:
            return None
        if loop.holding_needle.is_front:
            return self.front_bed.get_needle_of_loop(loop)
        else:
            return self.back_bed.get_needle_of_loop(loop)

    @property
    def rack(self) -> int:
        """Get the current rack value of the machine.

        Returns:
            int: The current rack value of the machine.
        """
        return self._rack

    @property
    def all_needle_rack(self) -> bool:
        """Check if racking is aligned for all needle knitting.

        Returns:
            bool: True if racking is aligned for all needle knitting, False otherwise.
        """
        return self._all_needle_rack

    @rack.setter
    def rack(self, new_rack: float) -> None:
        """Set the rack value with support for all-needle racking.

        Args:
            new_rack (float): The new rack value to set.

        Raises:
            Max_Rack_Exception: If the absolute rack value exceeds the maximum allowed rack.
        """
        if abs(new_rack) > self.max_rack:
            raise Max_Rack_Exception(new_rack, self.max_rack)
        self._all_needle_rack = abs(new_rack - int(new_rack)) != 0.0
        if new_rack < 0 and self.all_needle_rack:
            self._rack = int(new_rack) - 1  # negative all needle racking adds 0.25, thus the rack value needs to be adjusted down.
        else:
            self._rack = int(new_rack)

    def get_needle(self, needle: Needle | tuple[bool, int] | tuple[bool, int, bool]) -> Needle:
        """Get the needle on this knitting machine at the given needle location.

        Args:
            needle (Needle | tuple[bool, int] | tuple[bool, int, bool]):
                A needle or a tuple to construct a needle: is_front, needle position, optional is_slider defaults to False.

        Returns:
            Needle: The needle on this knitting machine at the given needle location.
        """
        if isinstance(needle, tuple):
            is_front = bool(needle[0])
            position = int(needle[1])
            if len(needle) == 2 or not bool(needle[2]):  # no slider declared or slider is false
                needle = Needle(is_front, position)
            else:
                needle = Slider_Needle(is_front, position)
        if needle.is_front:
            return self.front_bed[needle]
        else:
            return self.back_bed[needle]

    def get_carrier(self, carrier: int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]) -> Yarn_Carrier | list[Yarn_Carrier]:
        """Get the carrier or list of carriers owned by the machine at the given specification.

        Args:
            carrier (int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]):
                The carrier defined by a given carrier, carrier_set, integer or list of integers to form a set.

        Returns:
            Yarn_Carrier | list[Yarn_Carrier]:
                The carrier or list of carriers owned by the machine at the given specification.
        """
        return self.carrier_system[carrier]

    def __getitem__(self, item: Needle | tuple[bool, int, bool] | tuple[bool, int] |
                                Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]
                                | Machine_Knit_Loop) -> Needle | Yarn_Carrier | list[Yarn_Carrier] | None:
        """Access needles, carriers, or find needles holding loops on the machine.

        Args:
            item (Needle | tuple[bool, int, bool] | tuple[bool, int] | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier] | Machine_Knit_Loop):
                A needle, yarn carrier, carrier set, or loop to reference in the machine.

        Returns:
            Needle | Yarn_Carrier | list[Yarn_Carrier] | None:
                The needle on the machine at the given needle position,
                or if given yarn carrier information return the corresponding carrier or carriers on the machine,
                or if given a loop return the corresponding needle that holds this loop or None if the loop is not held on a needle.

        Raises:
            KeyError: If the item cannot be accessed from the machine.
        """
        if isinstance(item, Machine_Knit_Loop):
            return self.get_needle_of_loop(item)
        if isinstance(item, Needle) or isinstance(item, tuple):
            if isinstance(item, tuple):
                if len(item) == 2:
                    item = bool(item[0]), int(item[1]), False
                else:
                    item = bool(item[0]), int(item[1]), bool(item[2])
            return self.get_needle(item)
        elif isinstance(item, Yarn_Carrier) or isinstance(item, Yarn_Carrier_Set):
            return self.carrier_system[item]
        raise KeyError(f"Could not access {item} from machine.")

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
        needle = self[needle]
        assert isinstance(needle, Needle)
        if needle.is_front:  # aligned position is on the back bed
            aligned_position = needle.position - self.rack
        else:  # aligned position is on the front bed.
            aligned_position = needle.position + self.rack
        if aligned_slider:
            return Slider_Needle(not needle.is_front, aligned_position)
        else:
            return Needle(not needle.is_front, aligned_position)

    @staticmethod
    def get_transfer_rack(start_needle: Needle, target_needle: Needle) -> int | None:
        """Calculate the racking value needed to make transfer between start and target needle.

        Args:
            start_needle (Needle): Needle currently holding loops to transfer.
            target_needle (Needle): Needle to transfer loops to.

        Returns:
            int | None:
                Racking value needed to make transfer between start and target needle,
                None if no racking can be made because needles are on the same bed.
        """
        if start_needle.is_front == target_needle.is_front:
            return None
        if start_needle.is_front:
            return Knitting_Machine.get_rack(start_needle.position, target_needle.position)
        else:
            return Knitting_Machine.get_rack(target_needle.position, start_needle.position)

    def valid_rack(self, front_pos: int, back_pos: int) -> bool:
        """Check if transfer can be completed at current racking.

        Args:
            front_pos (int): The front needle in the racking.
            back_pos (int): The back needle in the racking.

        Returns:
            bool: True if the current racking can make this transfer, False otherwise.
        """
        needed_rack = self.get_rack(front_pos, back_pos)
        return self.rack == needed_rack

    def sliders_are_clear(self) -> bool:
        """Check if no loops are on any slider needle and knitting can be executed.

        Returns:
            bool:
                True if no loops are on a slider needle and knitting can be executed, False otherwise.
        """
        return bool(self.front_bed.sliders_are_clear() and self.back_bed.sliders_are_clear())

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

    def tuck(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> list[Machine_Knit_Loop]:
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
        assert isinstance(needle, Needle)
        new_loops: list[Machine_Knit_Loop] = self.carrier_system.make_loops(carrier_set, needle, direction)
        if needle.is_front:
            self.front_bed.add_loops(needle, new_loops, drop_prior_loops=False)
        else:
            self.back_bed.add_loops(needle, new_loops, drop_prior_loops=False)
        return new_loops

    def knit(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
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
        assert isinstance(needle, Needle)
        if not needle.has_loops:
            warnings.warn(Knit_on_Empty_Needle_Warning(needle))

        # position the carrier set to align with the knitting needle
        carrier_set.position_carriers(self.carrier_system, needle, direction)
        # Set the carriage for this operation
        self.carriage.transferring = False
        self.carriage.move(direction, needle.position)
        # Drop and save the current loops, then add the child loops onto this needle.
        if needle.is_front:
            bed = self.front_bed
        else:
            bed = self.back_bed
        parent_loops = bed.drop(needle)
        # Make child loops by this specification
        child_loops = self.carrier_system.make_loops(carrier_set, needle, direction)
        bed.add_loops(needle, child_loops, drop_prior_loops=False)  # drop should have occurred in prior line

        # Create stitches in the knitgraph.
        for parent in parent_loops:
            for child in child_loops:
                self.knit_graph.connect_loops(parent, child, needle.pull_direction)
        return parent_loops, child_loops

    def drop(self, needle: Needle) -> list[Machine_Knit_Loop]:
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
        assert isinstance(needle, Needle)
        self.carriage.transferring = True  # Used to mark that the direction of drop operation is also ignored.
        self.carriage.move_to(needle.position)
        return cast(list[Machine_Knit_Loop], needle.drop())

    def _add_xfer_crossing(self, left_loop: Machine_Knit_Loop, right_loop: Machine_Knit_Loop, crossing_direction: Crossing_Direction) -> None:
        """
        Add a crossing to the knit_graph's braid graph based on a transfer of the left loop (over or under) the right loop.
        If this crossing would undo a prior crossing, the prior crossing edge is removed.

        Args:
            left_loop: The loop involved in the crossing that starts on the left of the crossing.
            right_loop: The loop involved in the crossing that starts on the right of the crossing.
            crossing_direction: The direction of the crossing.
        """
        if self.knit_graph.braid_graph.loop_crossing_graph.has_edge(right_loop, left_loop):
            current_crossing = self.knit_graph.braid_graph.get_crossing(right_loop, left_loop)
            if current_crossing.opposite == crossing_direction:  # inverted crossing direction
                self.knit_graph.braid_graph.loop_crossing_graph.remove_edge(right_loop, left_loop)
            else:
                self.knit_graph.add_crossing(right_loop, left_loop, crossing_direction.opposite)
        else:
            self.knit_graph.add_crossing(left_loop, right_loop, crossing_direction)

    def _cross_loops_by_rightward_xfer(self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_Knit_Loop]) -> None:
        """
        Update the knitgraph's braid graph with a loop crossing created by a rightward crossing from the starting_needle to the aligned needle in a transfer.

        Args:
            starting_needle: The needle holding loops at the start of the transfer.
            aligned_needle: The needle receiving loops in the transfer.
            xfer_loops: The loops being transferred.
        """
        starting_position = starting_needle.racked_position_on_front(self.rack)
        front_crossed_positions = [f for f in self.front_bed[starting_position:starting_position + abs(self.rack) + 1]
                                   if f != starting_needle and f != aligned_needle and f.has_loops]
        for n in front_crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    # cross the transferred loops to right, under the cross loops on the front bed.
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Under_Right)
        back_crossed_positions = [b for b in self.back_bed[starting_position:starting_position + abs(self.rack) + 1]
                                  if b != starting_needle and b != aligned_needle and b.has_loops]
        for n in back_crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    # cross the transferred loops to the right, over the cross loops on the back bed.
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Over_Right)

    def _cross_loops_by_leftward_xfer(self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_Knit_Loop]) -> None:
        """
        Update the knitgraph's braid graph with a loop crossing created by a leftward crossing from the starting_needle to the aligned needle in a transfer.

        Args:
            starting_needle: The needle holding loops at the start of the transfer.
            aligned_needle: The needle receiving loops in the transfer.
            xfer_loops: The loops being transferred.
        """
        starting_position = starting_needle.racked_position_on_front(self.rack)
        front_crossed_positions = [f for f in self.front_bed[starting_position - self.rack:starting_position + 1]
                                   if f != starting_needle and f != aligned_needle and f.has_loops]
        for n in front_crossed_positions:
            for right_loop in xfer_loops:
                for left_loop in n.held_loops:
                    # cross the crossed loops on the front bed to the right, over the transferred loops
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Over_Right)
        back_crossed_positions = [b for b in self.back_bed[starting_position - self.rack:starting_position + 1]
                                  if b != starting_needle and b != aligned_needle and b.has_loops]
        for n in back_crossed_positions:
            for right_loop in xfer_loops:
                for left_loop in n.held_loops:
                    # cross the crossed loops on the back bed to the right, under the transferred loops
                    self._add_xfer_crossing(left_loop, right_loop, Crossing_Direction.Under_Right)

    def _cross_loops_by_xfer(self, starting_needle: Needle, aligned_needle: Needle, xfer_loops: list[Machine_Knit_Loop]) -> None:
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

    def xfer(self, starting_needle: Needle, to_slider: bool = False, from_split: bool = False) -> list[Machine_Knit_Loop]:
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
        assert isinstance(starting_needle, Needle)
        aligned_needle = self[self.get_aligned_needle(starting_needle, to_slider)]  # get needle on the machine.
        assert isinstance(aligned_needle, Needle)

        # Drop the loops from the starting bed and add them to the aligned needle on the opposite bed.
        if starting_needle.is_front:
            held_loops = self.front_bed.drop(starting_needle)
            for loop in held_loops:  # Update loop's needle history
                loop.reverse_drop()
                loop.transfer_loop(aligned_needle)
            xfer_loops: list[Machine_Knit_Loop] = self.back_bed.add_loops(aligned_needle, held_loops, drop_prior_loops=False)
        else:
            held_loops = self.back_bed.drop(starting_needle)
            for loop in held_loops:  # Update loop's needle history
                loop.reverse_drop()
                loop.transfer_loop(aligned_needle)
            xfer_loops: list[Machine_Knit_Loop] = self.front_bed.add_loops(aligned_needle, held_loops, drop_prior_loops=False)

        self._cross_loops_by_xfer(starting_needle, aligned_needle, xfer_loops)

        if not from_split:  # Update the carriage position, regardless of carrier behaviors.
            self.carriage.transferring = True
            if starting_needle.is_front:
                self.carriage.move_to(starting_needle.position)
            else:
                self.carriage.move_to(aligned_needle.position)
        return xfer_loops

    def split(self, carrier_set: Yarn_Carrier_Set, starting_needle: Needle, direction: Carriage_Pass_Direction) -> tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
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
        child_loops = self.tuck(carrier_set, starting_needle, direction)  # tuck new loops onto the needle after completing the transfer

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
        carrier_set.position_carriers(self.carrier_system, needle, direction)
        self.carriage.transferring = False
        self.carriage.move(direction, needle.position)

    def front_needles(self) -> list[Needle]:
        """Get list of all front bed needles.

        Returns:
            list[Needle]: List of all front bed needles.
        """
        return cast(list[Needle], self.front_bed.needles)

    def front_sliders(self) -> list[Slider_Needle]:
        """Get list of all front bed slider needles.

        Returns:
            list[Slider_Needle]: List of slider needles on front bed.
        """
        return cast(list[Slider_Needle], self.front_bed.sliders)

    def back_needles(self) -> list[Needle]:
        """Get list of all back bed needles.

        Returns:
            list[Needle]: List of all back bed needles.
        """
        return cast(list[Needle], self.back_bed.needles)

    def back_sliders(self) -> list[Slider_Needle]:
        """Get list of all back bed slider needles.

        Returns:
            list[Slider_Needle]: List of slider needles on back bed.
        """
        return cast(list[Slider_Needle], self.back_bed.sliders)

    def front_loops(self) -> list[Needle]:
        """Get list of front bed needles that currently hold loops.

        Returns:
            list[Needle]: List of front bed needles that currently hold loops.
        """
        return cast(list[Needle], self.front_bed.loop_holding_needles())

    def front_slider_loops(self) -> list[Slider_Needle]:
        """Get list of front slider needles that currently hold loops.

        Returns:
            list[Slider_Needle]: List of front slider needles that currently hold loops.
        """
        return cast(list[Slider_Needle], self.front_bed.loop_holding_sliders())

    def back_loops(self) -> list[Needle]:
        """Get list of back bed needles that currently hold loops.

        Returns:
            list[Needle]: List of back bed needles that currently hold loops.
        """
        return cast(list[Needle], self.back_bed.loop_holding_needles())

    def back_slider_loops(self) -> list[Slider_Needle]:
        """Get list of back slider needles that currently hold loops.

        Returns:
            list[Slider_Needle]: List of back slider needles that currently hold loops.
        """
        return cast(list[Slider_Needle], self.back_bed.loop_holding_sliders())

    def all_needles(self) -> list[Needle]:
        """Get list of all needles with front bed needles given first.

        Returns:
            list[Needle]: List of all needles with front bed needles given first.
        """
        return [*self.front_needles(), *self.back_needles()]

    def all_sliders(self) -> list[Slider_Needle]:
        """Get list of all slider needles with front bed sliders given first.

        Returns:
            list[Slider_Needle]: List of all slider needles with front bed sliders given first.
        """
        return [*self.front_sliders(), *self.back_sliders()]

    def all_loops(self) -> list[Needle]:
        """Get list of all needles holding loops with front bed needles given first.

        Returns:
            list[Needle]: List of all needles holding loops with front bed needles given first.
        """
        return [*self.front_loops(), *self.back_loops()]

    def all_slider_loops(self) -> list[Slider_Needle]:
        """Get list of all slider needles holding loops with front bed sliders given first.

        Returns:
            list[Slider_Needle]:
                List of all slider needles holding loops with front bed sliders given first.
        """
        return [*self.front_slider_loops(), *self.back_slider_loops()]
