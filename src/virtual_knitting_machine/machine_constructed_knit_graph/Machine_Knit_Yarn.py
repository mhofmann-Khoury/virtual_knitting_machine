"""Module containing the Machine_Knit_Yarn class for representing yarn in machine knitting operations.

This module extends the base Yarn class to include machine-specific functionality including
carrier management, float tracking, loop creation, and machine state coordination for yarn operations on virtual knitting machines.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, TypeVar

from knit_graphs.Yarn import Yarn, Yarn_Properties

from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Long_Float_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Machine_Knit_Yarn(Yarn[Machine_LoopT]):
    """An extension of the base Yarn class to capture machine knitting specific information.

    This includes carrier assignment, active loop tracking, float management, and machine state coordination.
    This class manages yarn operations during machine knitting including loop creation, float validation,
    and carrier state tracking with configurable maximum float lengths.

    Attributes:
        active_loops (dict[Machine_Knit_Loop, Needle]): Dictionary mapping active loops to their holding needles.
    """

    def __init__(
        self,
        carrier: Yarn_Carrier[Machine_LoopT],
        properties: Yarn_Properties | None,
        instance: int = 0,
        **_kwargs: Any,
    ) -> None:
        """Initialize a machine knit yarn with carrier and properties.

        Args:
            carrier (Yarn_Carrier): The yarn carrier this yarn is assigned to.
            properties (Yarn_Properties | None): Properties for this yarn, creates default if None.
            instance (int, optional): Instance number for yarn identification. Defaults to 0.
        """
        super().__init__(carrier.knitting_machine.knit_graph, properties, instance)
        self._carrier: Yarn_Carrier = carrier
        self.active_loops: dict[Machine_LoopT, Needle[Machine_LoopT]] = {}

    @property
    def is_active(self) -> bool:
        """Check if yarn is active and can form new loops.

        Returns:
            bool: True if yarn is active and can form new loops, False otherwise.
        """
        return not self.is_cut and self.carrier.is_active

    @property
    def is_hooked(self) -> bool:
        """Check if carrier is on yarn inserting hook.

        Returns:
            bool: True if carrier is on yarn inserting hook, False otherwise.
        """
        return self.is_active and self.carrier.is_hooked

    @property
    def carrier(self) -> Yarn_Carrier:
        """Get the carrier assigned to yarn or None if yarn has been dropped from carrier.

        Returns:
            Yarn_Carrier: Carrier assigned to yarn or None if yarn has been dropped from carrier.
        """
        return self._carrier

    @property
    def last_needle(self) -> Needle[Machine_LoopT] | None:
        """Get the needle that holds the loop closest to the end of the yarn.

        Returns:
            Needle | None: The needle that holds the loop closest to the end of the yarn,
                or None if the yarn has been dropped entirely.
        """
        if self.last_loop is None:
            return None
        return self.last_loop.holding_needle

    def active_floats(self) -> dict[Machine_LoopT, Machine_LoopT]:
        """Get dictionary of loops that are active keyed to active yarn-wise neighbors.

        Returns:
            dict[Machine_Knit_Loop, Machine_Knit_Loop]: Dictionary of loops that are active keyed to active yarn-wise neighbors.
                Each key-value pair represents a directed float where key comes before value on the yarn.
        """
        floats = {}
        for l in self.active_loops:
            n = self.next_loop(l)
            if n is not None and n in self.active_loops:
                assert isinstance(n, Machine_Knit_Loop)
                floats[l] = n
        return floats

    def add_loop_to_end(self, loop: Machine_LoopT) -> Machine_LoopT:
        """Add an existing loop to the end of this yarn and associated knit graph.

        Args:
            loop (Machine_Knit_Loop): The loop to be added at the end of this yarn.

        Returns:
            Machine_Knit_Loop: The loop that was added to the end of the yarn.

        Warns:
            Long_Float_Warning: If the float from the prior loop is too long for the machine specification.
        """
        last_needle = self.last_needle
        new_slot = loop.source_needle.slot_number
        max_float_length = self.carrier.machine_specification.maximum_float
        if last_needle is not None and abs(new_slot - last_needle.slot_number) > max_float_length:
            warnings.warn(
                Long_Float_Warning(self.carrier.carrier_id, last_needle, loop.source_needle, max_float_length),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )
        return super().add_loop_to_end(loop)
