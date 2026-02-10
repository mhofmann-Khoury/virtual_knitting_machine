"""Module containing the Machine_Component"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State


@runtime_checkable
class Machine_Component(Protocol):
    """
    A protocol for elements owned by a knitting machine used to access common state values across multiple sources.
    """

    _DEFAULT_RACK: int = 0  # Default racking alignment if a machine is not specified
    _DEFAULT_ALL_NEEDLE: bool = False  # Default state of all needle racking.
    _DEFAULT_MACHINE_SPEC: Knitting_Machine_Specification = (
        Knitting_Machine_Specification()
    )  # Default specification when the knitting machine is not present.

    @property
    def knitting_machine(self) -> Knitting_Machine_State | None:
        """
        Returns:
            Knitting_Machine_State | None: The machine state of the knitting machine that owns this component or None if the machine has not been specified.
        """
        ...

    @property
    def has_machine(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine that owns this component has been specified.
        """
        return self.knitting_machine is not None

    @property
    def machine_specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The machine specification of the machine associated with this component or a default machine spec.
        """
        return (
            self._DEFAULT_MACHINE_SPEC if self.knitting_machine is None else self.knitting_machine.machine_specification
        )

    @property
    def machine_racking(self) -> int:
        """
        Returns:
            int: The racking of the knitting machine. Defaults to 0 if no machine is specified.
        """
        return self.knitting_machine.rack if self.knitting_machine is not None else Machine_Component._DEFAULT_RACK

    @property
    def machine_is_all_needle_racked(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine is racked for all needle knitting. Defaults to False if no machine is specified.
        """
        return (
            self.knitting_machine.all_needle_rack
            if self.knitting_machine is not None
            else Machine_Component._DEFAULT_ALL_NEEDLE
        )

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

    def machines_match(self, other: Machine_Component | Knitting_Machine_State) -> bool:
        """

        Args:
            other (Machine_Component | Knitting_Machine_State): The component or machine to ensure the machines match.

        Returns:
            bool: True if the other component shares or is the machine state of this component. False, otherwise.
        """
        if isinstance(other, Machine_Component):
            return self.knitting_machine is other.knitting_machine
        else:
            return self.knitting_machine is other
