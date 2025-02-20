"""A module containing Yarn Insertion System classes."""
import warnings

from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Inserting_Hook_In_Use_Exception, Hooked_Carrier_Exception, Use_Inactive_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import In_Active_Carrier_Warning, In_Loose_Carrier_Warning, Out_Inactive_Carrier_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Yarn_Insertion_System:
    """A class for managing the state of the Yarn-Insertion system of yarn carriers on the knitting machine."""
    Hook_Size = 5

    def __init__(self, knitting_machine, carrier_count: int = 10):
        self.knitting_machine = knitting_machine
        self.carriers: list[Yarn_Carrier] = [Yarn_Carrier(i) for i in range(1, carrier_count + 1)]
        self.hook_position: None | int = None
        self.hook_input_direction: None | Carriage_Pass_Direction = None
        self._searching_for_position: bool = False
        self.hooked_carrier: Yarn_Carrier | None = None

    @property
    def searching_for_position(self) -> bool:
        """
        :return: True if the inserting hook is active but at an undefined position. False otherwise.
        """
        if self.inserting_hook_available:
            return False
        return self._searching_for_position

    @property
    def carrier_ids(self) -> list[int]:
        """
        :return: List of carrier ids in the carrier system.
        """
        return [int(c) for c in self.carriers]

    def position_carrier(self, carrier_id: int, position: int | Needle):
        """
        Update the position of the carrier.
        :param carrier_id: The carrier to update
        :param position: the position of the carrier
        """
        self[carrier_id].position = position

    @property
    def hook_size(self) -> int:
        """
        :return: The number of needles blocked to the right of the yarn inserting hook position
        """
        return Yarn_Insertion_System.Hook_Size

    @property
    def inserting_hook_available(self) -> bool:
        """
        :return: True if the yarn inserting hook can be used
        """
        return self.hooked_carrier is None

    @property
    def active_carriers(self) -> set[Yarn_Carrier]:
        """
        :return: Set of carrier id of carriers that are currently active (off the grippers)
        """
        return {c for c in self.carriers if c.is_active}

    def conflicts_with_inserting_hook(self, needle: Needle, direction: Carriage_Pass_Direction) -> bool:
        """
        :param direction:
        :param needle: the needle to check for compliance
        :return: True if inserting hook is conflicting with needle
        """
        if self.hook_position is not None:  # reserve positions to right of needle
            if direction is Carriage_Pass_Direction.Leftward:
                inserting_hook_range = range(self.hook_position + 1, self.hook_position + self.hook_size)
            else:
                inserting_hook_range = range(self.hook_position - 1, self.hook_position - self.hook_size)
            return needle.position in inserting_hook_range
        else:  # no conflicts if hook is not active
            return False

    def missing_carriers(self, carrier_ids: list[int]) -> list[int]:
        """
        :param carrier_ids: the carrier set to check for the inactive carriers.
        :return: list of carrier ids that are not active (i.e., on grippers).
        """
        return [cid for cid in carrier_ids if not self[cid].is_active]

    def is_active(self, carrier_ids: list[int]) -> bool:
        """
        :param carrier_ids:
        :return: True if the carrier (all carriers in set) are active (not-on the gripper)
            Note: If an empty list of carriers is given, this will return true because the empty set is active.
        """
        if len(carrier_ids) == 0:
            return True  # No ids given, so the null set is active
        return len(self.missing_carriers(carrier_ids)) == 0

    def yarn_is_loose(self, carrier_id: int) -> bool:
        """
        :param carrier_id:
        :return: True if any yarn in yarn carrier set is loose (not on the inserting hook or tuck/knit on bed)
        """
        return self[carrier_id].yarn.last_needle() is None

    def bring_in(self, carrier_id: int):
        """
        Brings in a yarn carrier without insertion hook (tail to gripper). Yarn is considered loose until knit
        :param carrier_id:
        """
        carrier = self[carrier_id]
        if carrier.is_active:
            warnings.warn(In_Active_Carrier_Warning(carrier_id))
        if carrier.yarn.last_needle() is None:
            warnings.warn(In_Loose_Carrier_Warning(carrier_id))
        carrier.bring_in()

    def inhook(self, carrier_id: int):
        """
        Brings a yarn in with insertion hook. Yarn is not loose
        :param carrier_id: carriers to bring in by id
        """

        carrier = self[carrier_id]
        if carrier.is_active:
            warnings.warn(In_Active_Carrier_Warning(carrier_id))
        if not self.inserting_hook_available and self.hooked_carrier != carrier:
            raise Inserting_Hook_In_Use_Exception(carrier_id)
        self.hooked_carrier = carrier
        self._searching_for_position = True
        self.hook_position = None
        self.hooked_carrier.inhook()

    def releasehook(self):
        """
        Releases the yarn inserting hook of what ever is on it.
        """
        self.hooked_carrier.releasehook()
        self.hooked_carrier = None
        self._searching_for_position = False
        self.hook_position = None
        self.hook_input_direction = None

    def out(self, carrier_id: int):
        """
        Moves carrier to gripper, removing it from action but does not cut it loose
        :param carrier_id:
        """
        carrier = self[carrier_id]
        if not carrier.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(carrier_id))
        if carrier.is_hooked:
            raise Hooked_Carrier_Exception(carrier_id)
        carrier.out()

    def outhook(self, carrier_id: int):
        """
        Cuts carrier yarn, moves it to grippers with insertion hook.
        The Carrier will no longer be active and is now loose
        :param carrier_id:
        """
        carrier = self[carrier_id]
        if not carrier.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(carrier_id))
        if not self.inserting_hook_available:
            Inserting_Hook_In_Use_Exception(carrier_id)
        if carrier.is_hooked:
            raise Hooked_Carrier_Exception(carrier_id)
        carrier.outhook()

    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """
        :return: Dictionary of loops that are active keyed to active yarn-wise neighbors.
         Each key-value pair represents a directed float where k comes before v on the yarns in the system.
        """
        active_floats = {}
        for carrier in self.carriers:
            active_floats.update(carrier.yarn.active_floats())
        return active_floats

    def make_loops(self, carrier_ids: list[int] | Yarn_Carrier_Set, needle: Needle, knit_graph: Knit_Graph, direction: Carriage_Pass_Direction) -> list[Machine_Knit_Loop]:
        """
        :param direction:
        :param carrier_ids: the carriers to make the loops with on this needle.
        :param needle: The needle to make the loops on.
        :param knit_graph: The knit Graph being constructed
        :return: The set of loops made on this machine.
        """
        needle = self.knitting_machine[needle]
        if self.searching_for_position:  # mark inserting hook position
            self.hook_position = needle.position
            self.hook_input_direction = direction
            self._searching_for_position = False
            self.knitting_machine.carriage.move_to(self.hook_position)
        loops = []
        for cid in carrier_ids:
            carrier = self[cid]
            if not carrier.is_active:
                raise Use_Inactive_Carrier_Exception(cid)
            float_source_needle = carrier.yarn.last_needle()
            loop = carrier.yarn.make_loop_on_needle(knit_graph=knit_graph, holding_needle=needle)
            if float_source_needle is not None:
                float_source_needle = self.knitting_machine[float_source_needle]
                float_start = min(float_source_needle.position, needle.position)
                float_end = max(float_source_needle.position, needle.position)
                front_floated_needles = [f for f in self.knitting_machine.front_bed[float_start: float_end + 1]
                                         if f != float_source_needle and f != needle]
                back_floated_needles = [b for b in self.knitting_machine.back_bed[float_start: float_end + 1]
                                        if b != float_source_needle and b != needle]
                for float_source_loop in float_source_needle.held_loops:
                    for fn in front_floated_needles:
                        for fl in fn.held_loops:
                            carrier.yarn.add_loop_in_front_of_float(fl, float_source_loop, loop)
                    for bn in back_floated_needles:
                        for bl in bn.held_loops:
                            carrier.yarn.add_loop_behind_float(bl, float_source_loop, loop)
            loops.append(loop)
        return loops

    def __getitem__(self, item: int | Yarn_Carrier | Yarn_Carrier_Set | list[int]) -> Yarn_Carrier | list[Yarn_Carrier]:
        try:
            if isinstance(item, Yarn_Carrier):
                return self[item.carrier_id]
            elif isinstance(item, Yarn_Carrier_Set):
                return self[item.carrier_ids]
            elif isinstance(item, list):
                if len(item) == 1:
                    return self[item[0]]
                else:
                    return [self[i] for i in item]
        except KeyError as e:
            raise KeyError(f"Invalid carrier: {item}. Carriers range from 1 to {len(self.carriers)}")
        assert isinstance(item, int)
        if item < 1 or item > len(self.carriers):
            raise KeyError(f"Invalid carrier index {item}")
        return self.carriers[item - 1]  # Carriers are given from values starting at 1 but indexed in the list starting at zero
