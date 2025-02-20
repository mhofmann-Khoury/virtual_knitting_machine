"""Module containing the Machine Knit Yarn Class"""
import warnings

from knit_graphs.Yarn import Yarn, Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Use_Cut_Yarn_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Long_Float_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Machine_Knit_Yarn(Yarn):
    MAX_FLOAT_LENGTH = 20

    def __init__(self, carrier, properties: Yarn_Properties | None, instance: int = 0):
        if properties is None:
            properties = Yarn_Properties()
        properties.name = f"{instance}_Yarn on c{carrier.carrier_id}"
        super().__init__(properties)
        self._instance: int = instance
        self._carrier = carrier
        self.active_loops: dict[Machine_Knit_Loop: Needle] = {}

    @property
    def is_active(self) -> bool:
        """
        :return: True if yarn is active and can form new loops
        """
        return self.carrier is not None and self.carrier.is_active

    @property
    def is_hooked(self) -> bool:
        """
        :return: True if carrier is on yarn inserting hook
        """
        return self.is_active and self.carrier.is_hooked

    @property
    def is_cut(self) -> bool:
        """
        :return: True if yarn is no longer on a carrier
        """
        return self.carrier is None

    @property
    def carrier(self):
        """
        :return: Carrier assigned to yarn or None if yarn has been dropped from carrier
        """
        return self._carrier

    def cut_yarn(self):
        """
        Cut yarns are no longer active
        :return: New Yarn of the same type after cut this yarn
        """
        self._carrier = None
        return Machine_Knit_Yarn(self.carrier, self.properties, instance=self._instance + 1)

    @property
    def last_loop(self) -> Machine_Knit_Loop | None:
        if self._last_loop is not None:
            assert isinstance(self._last_loop, Machine_Knit_Loop)
        return self._last_loop

    def last_needle(self) -> Needle | None:
        """
        :return: The needle that holds the loop closest to the end of the yarn or None if the yarn has been dropped entirely
        """
        if self.last_loop is None:
            return None
        return self.last_loop.holding_needle

    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """
        :return: Dictionary of loops that are active keyed to active yarn-wise neighbors.
         Each key-value pair represents a directed float where k comes before v on the yarn.
        """
        floats = {}
        for l in self.active_loops:
            assert isinstance(l, Machine_Knit_Loop)
            n = self.next_loop(l)
            if n is not None and n in self.active_loops:
                assert isinstance(n, Machine_Knit_Loop)
                floats[l] = n
        return floats

    def make_loop_on_needle(self, holding_needle: Needle, knit_graph=None) -> Machine_Knit_Loop:
        """
        Adds the loop at the end of the yarn.
        :param holding_needle: The needle to make the loop on and hold it.
        :param knit_graph: An optional Knit_Graph used to calculate last loop id in knitgraph.
        """
        if self.is_cut:
            raise Use_Cut_Yarn_Exception(self.carrier.carrier_id)
        last_needle = self.last_needle()
        if last_needle is not None and abs(holding_needle.position - last_needle.position) > self.MAX_FLOAT_LENGTH:
            warnings.warn(Long_Float_Warning(self.carrier.carrier_id, last_needle, holding_needle))
        loop = Machine_Knit_Loop(self._next_loop_id(knit_graph), self, holding_needle)
        self.add_loop_to_end(knit_graph, loop)
        return loop
