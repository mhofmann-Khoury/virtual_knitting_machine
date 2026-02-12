"""Module containing the Machine_Component"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import (
    Knitting_Machine_Error_Policy,
    Machine_State_With_Policy,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
    from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Machine_Component(Machine_State_With_Policy, Protocol[Machine_LoopT]):
    @property
    def knitting_machine(self) -> Knitting_Machine_State[Machine_LoopT, Any]:
        """
        Returns:
            Knitting_Machine_State: The knitting machine that owns this component.
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
    def machine_specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The machine specification of the machine associated with this component.
        """
        return self.knitting_machine.machine_specification

    @property
    def machine_racking(self) -> int:
        """
        Returns:
            int: The racking of the knitting machine.
        """
        return self.knitting_machine.rack

    @property
    def machine_is_all_needle_racked(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine is racked for all needle knitting.
        """
        return self.knitting_machine.all_needle_rack

    @property
    def needle_count_of_machine(self) -> int:
        """
        Returns:
            int: The number of needles on each bed of the knitting machine. Defaults to the bed size in the knitting machine specification.
        """
        return self.machine_specification.needle_count

    @property
    def rightmost_slot_on_machine(self) -> int:
        """
        Returns:
            int: The rightmost slot on this knitting machine. Defaults to the standard bed size in the knitting machine specification.
        """
        return self.needle_count_of_machine - 1
