"""Module containing the Knitting Machine class."""
from __future__ import annotations
import warnings
from collections import defaultdict
from typing import cast

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction

from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Change_Active_Carrier_System_Exception
from virtual_knitting_machine.knitting_machine_exceptions.racking_errors import Max_Rack_Exception
from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Knit_on_Empty_Needle_Warning
from virtual_knitting_machine.machine_components.Needle_Bed import Needle_Bed
from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import Yarn_Insertion_System
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn


class Knitting_Machine:
    """A virtual representation of a V-Bed WholeGarment knitting machine"""

    def __init__(self, machine_specification: Knitting_Machine_Specification = Knitting_Machine_Specification(), knit_graph: Knit_Graph | None = None):
        self.machine_specification: Knitting_Machine_Specification = machine_specification
        self.front_bed: Needle_Bed = Needle_Bed(is_front=True, needle_count=self.machine_specification.needle_count)
        self.back_bed: Needle_Bed = Needle_Bed(is_front=False, needle_count=self.machine_specification.needle_count)
        self._carrier_system: Yarn_Insertion_System = Yarn_Insertion_System(self, self.machine_specification.carrier_count)
        self.carriage: Carriage = Carriage(self, self.needle_count - 1)
        self._rack: int = 0
        self._all_needle_rack: bool = False
        if knit_graph is None:
            knit_graph = Knit_Graph()
        self.knit_graph: Knit_Graph = knit_graph

    def copy(self, starting_state: Knitting_Machine | None = None) -> Knitting_Machine:
        """
        Creates a crude copy of this machine state with all relevant yarns inhooked and loops formed on required locations.
        Note that this copy does not guarantee continuity of the knitgraph structure or history. It only ensures loops and carriers are correctly positioned to mimic the current state.
        :param starting_state: A machine state to copy into. Otherwise, creates a new machine state with the same machine specification as this machine.
        :return: A copy of the current  machine state.
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
    def max_rack(self) -> int:
        """
        :return: The maximum distance that the machine can rack.
        """
        return int(self.machine_specification.maximum_rack)

    @property
    def carrier_system(self) -> Yarn_Insertion_System:
        """
        :return: The carrier system used by the knitting machine
        """
        return self._carrier_system

    @carrier_system.setter
    def carrier_system(self, carrier_count: int = 10) -> None:
        if len(self.carrier_system.active_carriers) > 0:
            raise Change_Active_Carrier_System_Exception()
        self.machine_specification.carrier_count = carrier_count
        old_system = self.carrier_system
        self._carrier_system = Yarn_Insertion_System(self, carrier_count)
        for carrier in old_system:  # reset old yarn settings
            self.carrier_system[carrier.carrier_id].yarn = carrier.yarn.properties

    @property
    def needle_count(self) -> int:
        """
        :return: The needle width of the machine.
        """
        return int(self.front_bed.needle_count)

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> None | Needle:
        """
        :return: The needle holding the loop or None if it is not held.
        :param loop: The loop to search for.
        """
        front_needle = self.front_bed.get_needle_of_loop(loop)
        back_needle = self.back_bed.get_needle_of_loop(loop)
        if front_needle is None and back_needle is None:
            return None
        elif front_needle is None:
            return back_needle
        else:
            assert back_needle is None, f"Loop {loop.loop_id} cannot be on f{front_needle.position} and b{back_needle.position}"
            return front_needle

    @property
    def rack(self) -> int:
        """
        :return: The current rack value of the machine.
        """
        return self._rack

    @property
    def all_needle_rack(self) -> bool:
        """
        :return: True if racking is aligned for all needle knitting.
        """
        return self._all_needle_rack

    @rack.setter
    def rack(self, new_rack: float) -> None:
        if abs(new_rack) > self.max_rack:
            raise Max_Rack_Exception(new_rack, self.max_rack)
        self._all_needle_rack = abs(new_rack - int(new_rack)) != 0.0
        if new_rack < 0 and self.all_needle_rack:
            self._rack = int(new_rack) - 1  # negative all needle racking adds 0.25, thus the rack value needs to be adjusted down.
        else:
            self._rack = int(new_rack)

    def __len__(self) -> int:
        """
        :return: The needle bed width of the machine.
        """
        return self.needle_count

    def get_needle(self, needle: Needle | tuple[bool, int] | tuple[bool, int, bool]) -> Needle:
        """
        :param needle: A needle or a tuple to construct a needle: is_front, needle position, optional is_slider defaults to False.
        :return: The needle on this knitting machine at the given needle location.
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
        """
        :param carrier: The carrier defined by a given carrier, carrier_set, integer or list of integers to form a set.
        :return: The carrier or list of carriers owned by the machine at the given specification.
        """
        return self.carrier_system[carrier]

    def __getitem__(self, item: Needle | tuple[bool, int, bool] | tuple[bool, int] |
                                Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier] |
                                Machine_Knit_Loop) -> Needle | Yarn_Carrier | list[Yarn_Carrier] | None:
        """

        :param item: A needle, yarn carrier or carrier set to reference in the machine.
        :return: The needle on the machine at the given needle position,
            or if given  yarn carrier information return the corresponding carrier or carriers on the machine
            or if given a loop, return the corresponding needle that holds this loop or None if the loop is not held on a needle.
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
        """
        Updates the current racking to align front and back.
        :param front_pos: front needle to align.
        :param back_pos: back needle to align.
        :return: Return True if the rack was updated to a new value.
        """
        original = self.rack
        self.rack = self.get_rack(front_pos, back_pos)
        return original != self.rack

    @staticmethod
    def get_rack(front_pos: int, back_pos: int) -> int:
        """
        Return racking between front and back position.
        R = F - B.
        F = R + B.
        B = F - R.
        :param front_pos: Front aligned needle position.
        :param back_pos: Back aligned needle position.
        :return: Racking needed to xfer from front position to back position.
        """
        return front_pos - back_pos

    def get_aligned_needle(self, needle: Needle, aligned_slider: bool = False) -> Needle:
        """
        Note from Knitout Specification on Racking
         Number indicating the offset of the front bed relative to the back bed.
         That is, at racking R, back needle index B is aligned to front needle index B+R.
         Needles are considered aligned if they can transfer.
         That is, at racking 2, it is possible to transfer from f3 to b1.
         F = B + R.
         R = F - B.
         B = F - R.
        :param needle: the needle to find the aligned needle to.
        :param aligned_slider: If true, ill return a slider needle.
        :return: Needle aligned with the given needle at current racking.
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
        """
        :param start_needle: Needle currently holding loops to transfer.
        :param target_needle: Needle to transfer loops to.
        :return: Racking value needed to make transfer between start and target needle. None if no racking can be made because needles are on the same bed.
        """
        if start_needle.is_front == target_needle.is_front:
            return None
        if start_needle.is_front:
            return Knitting_Machine.get_rack(start_needle.position, target_needle.position)
        else:
            return Knitting_Machine.get_rack(target_needle.position, start_needle.position)

    def valid_rack(self, front_pos: int, back_pos: int) -> bool:
        """
        True xfer can be completed at current racking.
        :param front_pos: The front needle in the racking.
        :param back_pos: The back needle in the racking.
        :return: True if the current racking can make this transfer.
        """
        needed_rack = self.get_rack(front_pos, back_pos)
        return self.rack == needed_rack

    def sliders_are_clear(self) -> bool:
        """
        :return: True, if no loops are on a slider needle and knitting can be executed
        """
        return bool(self.front_bed.sliders_are_clear() and self.back_bed.sliders_are_clear())

    def in_hook(self, carrier_id: int | Yarn_Carrier) -> None:
        """
        Declares that the in_hook for this yarn carrier is in use
        :param carrier_id: the yarn_carrier to bring in
        """
        self.carrier_system.inhook(carrier_id)

    def release_hook(self) -> None:
        """
        Declares that the in-hook is not in use but yarn remains in use
        """
        self.carrier_system.releasehook()

    def out_hook(self, carrier_id: int | Yarn_Carrier) -> None:
        """
        Declares that the yarn is no longer in service, will need to be in-hooked to use
        :param carrier_id: the yarn carrier to remove from service
        """
        self.carrier_system.outhook(carrier_id)

    def bring_in(self, carrier_id: int | Yarn_Carrier) -> None:
        """
        Brings the yarn carrier into action
        :param carrier_id:
        """
        self.carrier_system.bring_in(carrier_id)

    def out(self, carrier_id: int | Yarn_Carrier) -> None:
        """
        Moves the yarn_carrier out of action
        :param carrier_id:
        """
        self.carrier_system.out(carrier_id)

    def tuck(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> list[Machine_Knit_Loop]:
        """
        Place loops made with carriers in the carrier set on the given needle.
        :param direction: The direction to tuck in.
        :param carrier_set: Set of yarns to make loops with.
        :param needle: Needle to make loops on.
        :return: List of new loops made by tucking.
        """
        needle = self[needle]
        assert isinstance(needle, Needle)
        carrier_set.position_carriers(self.carrier_system, needle)
        self.carriage.transferring = False
        new_loops = cast(list[Machine_Knit_Loop], self.carrier_system.make_loops(carrier_set, needle, direction))
        self.carriage.move(direction, needle.position)
        return new_loops

    def knit(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
        """
        Form new loops from the carrier set by pulling them through all loops on the given Needle.
        Drop the needles currently on the old needle.
        Hold the new loops on the needle.
        :param direction: The direction to knit in.
        :param carrier_set: Set of yarns to make loops with.
        :param needle: Needle to knit on.
        :return: List of loops stitched through and dropped of needle by knitting process.
            List of loops formed in the knitting process.
        """
        needle = self[needle]
        assert isinstance(needle, Needle)
        if not needle.has_loops:
            warnings.warn(Knit_on_Empty_Needle_Warning(needle))
        carrier_set.position_carriers(self.carrier_system, needle)
        self.carriage.transferring = False
        parent_loops = needle.drop()
        child_loops = self.carrier_system.make_loops(carrier_set, needle, direction)
        self.carriage.move(direction, needle.position)
        for parent in parent_loops:
            for child in child_loops:
                self.knit_graph.connect_loops(parent, child, needle.pull_direction)
        return parent_loops, child_loops

    def drop(self, needle: Needle) -> list[Machine_Knit_Loop]:
        """
        Drop all loops currently on given needle.
        :param needle: The needle to drop from.
        :return: The list of loops dropped.
        """
        needle = self[needle]
        assert isinstance(needle, Needle)
        self.carriage.transferring = True
        self.carriage.move_to(needle.position)
        return cast(list[Machine_Knit_Loop], needle.drop())

    def xfer(self, starting_needle: Needle, to_slider: bool = False, from_split: bool = False) -> list[Machine_Knit_Loop]:
        """
        Move all loops on starting_needle to aligned needle at current racking.
        :param from_split: If True, this xfer is part of a split and does not move the carriage.
        :param starting_needle: Needle to move loops from.
        :param to_slider: If true, loops are moved to a slider.
        :return: The list of loops that are transferred.
        """
        starting_needle = self[starting_needle]  # get needle on the machine.
        assert isinstance(starting_needle, Needle)
        starting_position = starting_needle.opposite().racked_position_on_front(self.rack)
        aligned_needle = self[self.get_aligned_needle(starting_needle, to_slider)]  # get needle on the machine.
        assert isinstance(aligned_needle, Needle)
        aligned_position = aligned_needle.racked_position_on_front(self.rack)
        xfer_loops: list[Machine_Knit_Loop] = starting_needle.transfer_loops(aligned_needle)
        crossed_positions = [f for f in self.front_bed[starting_position: aligned_position + 1]
                             if f != starting_needle and f != aligned_needle and f.has_loops]  # Only does rightward crossings. Leftward is implied
        for n in crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    self.knit_graph.add_crossing(left_loop, right_loop, Crossing_Direction.Under_Right)
        crossed_positions = [b for b in self.back_bed[starting_position: aligned_position + 1]
                             if b != starting_needle and b != aligned_needle and b.has_loops]  # Only does rightward crossings. Leftward is implied
        for n in crossed_positions:
            for left_loop in xfer_loops:
                for right_loop in n.held_loops:
                    self.knit_graph.add_crossing(left_loop, right_loop, Crossing_Direction.Over_Right)
        if not from_split:
            self.carriage.transferring = True
            if starting_needle.is_front:
                self.carriage.move_to(starting_needle.position)
            else:
                self.carriage.move_to(aligned_needle.position)
        return  xfer_loops

    def split(self, carrier_set: Yarn_Carrier_Set, starting_needle: Needle, direction: Carriage_Pass_Direction) -> tuple[list[Machine_Knit_Loop], list[Machine_Knit_Loop]]:
        """
        Note from Knitout Documentation:
         Pull a loop formed in direction D by the yarns in carriers CS through the loops on needle N,
          transferring the old loops to opposite-bed needle N2 in the process.
          Splitting with an empty carrier set will transfer.
        Transfer the loops on the starting needle to the aligned needle at this racking.
         Then form new loops pulled through the transferred loops and hold them on the starting needle.
        :param direction:
        :param carrier_set: Set of yarns to make loops with.
        :param starting_needle: The Needle to transfer old loops from and to form new loops on.
        :return: The list of loops created by the split.
        """
        starting_needle = self[starting_needle]  # index to needle on machine
        assert isinstance(starting_needle, Needle)
        aligned_needle = self[self.get_aligned_needle(starting_needle, False)]
        assert isinstance(aligned_needle, Needle)
        carrier_set.position_carriers(self.carrier_system, starting_needle)
        self.carriage.transferring = False
        parent_loops = self.xfer(starting_needle, to_slider=False, from_split=True)
        child_loops = self.carrier_system.make_loops(carrier_set, starting_needle, direction)
        if starting_needle.is_front:
            self.carriage.move(direction, starting_needle.position)
        else:
            self.carriage.move(direction, aligned_needle.position)
        for parent in parent_loops:
            for child in child_loops:
                self.knit_graph.connect_loops(parent, child, starting_needle.pull_direction)
        return child_loops, parent_loops

    def miss(self, carrier_set: Yarn_Carrier_Set, needle: Needle, direction: Carriage_Pass_Direction) -> None:
        """
        Set the carrier positions to hover above the given needle.
        :param direction:
        :param carrier_set: Set of yarns to move.
        :param needle: Needle to position the carriers from.
        """
        carrier_set.position_carriers(self.carrier_system, needle)
        self.carriage.transferring = False
        self.carriage.move(direction, needle.position)

    def front_needles(self) -> list[Needle]:
        """
        :return: iterator over the front needles.
        """
        return cast(list[Needle], self.front_bed.needles)

    def front_sliders(self) -> list[Slider_Needle]:
        """
        :return: list of slider needles on front bed.
        """
        return cast(list[Slider_Needle], self.front_bed.sliders)

    def back_needles(self) -> list[Needle]:
        """
        :return: iterator over the back bed needles.
        """
        return cast(list[Needle], self.back_bed.needles)

    def back_sliders(self) -> list[Slider_Needle]:
        """
        :return: list of slider needles on back bed.
        """
        return cast(list[Slider_Needle], self.back_bed.sliders)

    def front_loops(self) -> list[Needle]:
        """
        :return: list of front bed needles that currently hold loops.
        """
        return cast(list[Needle], self.front_bed.loop_holding_needles())

    def front_slider_loops(self) -> list[Slider_Needle]:
        """
        :return: list of front slider needles that currently hold loops.
        """
        return cast(list[Slider_Needle], self.front_bed.loop_holding_sliders())

    def back_loops(self) -> list[Needle]:
        """
        :return: List of back bed needles that currently hold loops.
        """
        return cast(list[Needle], self.back_bed.loop_holding_needles())

    def back_slider_loops(self) -> list[Slider_Needle]:
        """
        :return: List of back slider needles that currently hold loops.
        """
        return cast(list[Slider_Needle], self.back_bed.loop_holding_sliders())

    def all_needles(self) -> list[Needle]:
        """
        :return: List of all needles with front bed needles given first.
        """
        return [*self.front_needles(), *self.back_needles()]

    def all_sliders(self) -> list[Slider_Needle]:
        """
        :return: List of all slider needles with front bed sliders given first.
        """
        return [*self.front_sliders(), *self.back_sliders()]

    def all_loops(self) -> list[Needle]:
        """
        :return: List of all needles with front bed needles given first.
        """
        return [*self.front_loops(), *self.back_loops()]

    def all_slider_loops(self) -> list[Slider_Needle]:
        """
        :return: List of all slider needles with front bed sliders given first.
        """
        return [*self.front_slider_loops(), *self.back_slider_loops()]
