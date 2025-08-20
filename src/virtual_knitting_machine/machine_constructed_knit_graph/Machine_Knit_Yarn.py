"""Module containing the Machine_Knit_Yarn class for representing yarn in machine knitting operations.

This module extends the base Yarn class to include machine-specific functionality including
carrier management, float tracking, loop creation, and machine state coordination for yarn operations on virtual knitting machines.
"""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn, Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Use_Cut_Yarn_Exception,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    Long_Float_Warning,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
        Yarn_Carrier,
    )


class Machine_Knit_Yarn(Yarn):
    """An extension of the base Yarn class to capture machine knitting specific information.

    This includes carrier assignment, active loop tracking, float management, and machine state coordination.
    This class manages yarn operations during machine knitting including loop creation, float validation,
    and carrier state tracking with configurable maximum float lengths.

    Attributes:
        active_loops (dict[Machine_Knit_Loop, Needle]): Dictionary mapping active loops to their holding needles.
    """

    def __init__(self, carrier: Yarn_Carrier, properties: Yarn_Properties | None, knit_graph: None | Knit_Graph, instance: int = 0) -> None:
        """Initialize a machine knit yarn with carrier and properties.

        Args:
            carrier (Yarn_Carrier): The yarn carrier this yarn is assigned to.
            properties (Yarn_Properties | None): Properties for this yarn, creates default if None.
            instance (int, optional): Instance number for yarn identification. Defaults to 0.
        """
        if properties is None:
            properties = Yarn_Properties()
        super().__init__(properties, knit_graph=knit_graph)
        self._instance: int = instance
        self._carrier: Yarn_Carrier = carrier
        self.active_loops: dict[Machine_Knit_Loop: Needle] = {}

    @property
    def is_active(self) -> bool:
        """Check if yarn is active and can form new loops.

        Returns:
            bool: True if yarn is active and can form new loops, False otherwise.
        """
        return self.carrier is not None and self.carrier.is_active

    @property
    def is_hooked(self) -> bool:
        """Check if carrier is on yarn inserting hook.

        Returns:
            bool: True if carrier is on yarn inserting hook, False otherwise.
        """
        return self.is_active and self.carrier.is_hooked

    @property
    def is_cut(self) -> bool:
        """Check if yarn is no longer on a carrier (has been cut).

        Returns:
            bool: True if yarn is no longer on a carrier, False otherwise.
        """
        return self.carrier is None

    @property
    def carrier(self) -> Yarn_Carrier:
        """Get the carrier assigned to yarn or None if yarn has been dropped from carrier.

        Returns:
            Yarn_Carrier: Carrier assigned to yarn or None if yarn has been dropped from carrier.
        """
        return self._carrier

    def cut_yarn(self) -> Machine_Knit_Yarn:
        """Cut yarn to make it no longer active and create a new yarn instance of the same type.

        Returns:
            Machine_Knit_Yarn: New yarn of the same type after cutting this yarn.
        """
        self._carrier = None
        return Machine_Knit_Yarn(self.carrier, self.properties, knit_graph=self.knit_graph, instance=self._instance + 1)

    @property
    def last_loop(self) -> Machine_Knit_Loop | None:
        """Get the last loop in this yarn with machine-specific type checking.

        Returns:
            Machine_Knit_Loop | None: The last loop in the yarn or None if no loops exist.
        """
        if self._last_loop is not None:
            assert isinstance(self._last_loop, Machine_Knit_Loop)
        return self._last_loop

    def last_needle(self) -> Needle | None:
        """Get the needle that holds the loop closest to the end of the yarn.

        Returns:
            Needle | None: The needle that holds the loop closest to the end of the yarn,
                or None if the yarn has been dropped entirely.
        """
        if self.last_loop is None:
            return None
        return self.last_loop.holding_needle

    def active_floats(self) -> dict[Machine_Knit_Loop, Machine_Knit_Loop]:
        """Get dictionary of loops that are active keyed to active yarn-wise neighbors.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]: Dictionary of loops that are active keyed to active yarn-wise neighbors.
                Each key-value pair represents a directed float where key comes before value on the yarn.
        """
        floats = {}
        for l in self.active_loops:
            assert isinstance(l, Machine_Knit_Loop)
            n = self.next_loop(l)
            if n is not None and n in self.active_loops:
                assert isinstance(n, Machine_Knit_Loop)
                floats[l] = n
        return floats

    def make_loop_on_needle(self, holding_needle: Needle, max_float_length: int | None = None) -> Machine_Knit_Loop:
        """Add a new loop at the end of the yarn on the specified needle with configurable float length validation.

        Args:
            holding_needle (Needle): The needle to make the loop on and hold it.
            max_float_length (int | None, optional): The maximum allowed distance between needles holding a loop.
                If None no float length validation is performed. Defaults to None.

        Returns:
            Machine_Knit_Loop: The newly created machine knit loop.

        Raises:
            Use_Cut_Yarn_Exception: If attempting to use a cut yarn that is no longer on a carrier.

        Warns:
            Long_Float_Warning: If max_float_length is specified and the distance between this needle
                and the last needle exceeds the maximum.
        """
        if self.is_cut:
            raise Use_Cut_Yarn_Exception(self.carrier.carrier_id)
        last_needle = self.last_needle()
        if max_float_length is not None and last_needle is not None and abs(holding_needle.position - last_needle.position) > max_float_length:
            warnings.warn(Long_Float_Warning(self.carrier.carrier_id, last_needle, holding_needle, max_float_length))
        loop = Machine_Knit_Loop(self._next_loop_id(), self, holding_needle)
        self.add_loop_to_end(loop)
        return loop

    def __str__(self) -> str:
        """
        Returns:
            str: The string specifying the instance and carrier of this yarn.
        """
        return f"{self._instance}_Yarn on c{self.carrier.carrier_id}"

    def __repr__(self) -> str:
        """
        Returns:
            str: The string specifying the instance and carrier of this yarn.
        """
        return str(self)
