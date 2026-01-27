"""Yarn_Carrier representation module for managing individual yarn carriers on knitting machines.
This module provides the Yarn_Carrier class which represents a single yarn carrier that can hold yarn, track position, and manage active/hooked states for knitting operations."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Hooked_Carrier_Exception,
    Use_Inactive_Carrier_Exception,
)
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needle_bed_position import Needle_Bed_Position, Relative_to_Needle_Bed
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine, Knitting_Machine_State
    from virtual_knitting_machine.machine_components.needles.Needle import Needle
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set


@runtime_checkable
class Yarn_Carrier_State(Relative_to_Needle_Bed, Protocol):
    """A class from which all read-only attributes and properties of a yarn-carrier can be accessed.
    This class defines common properties between yarn-carriers and yarn-carrier-snapshots.
    """

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """
        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        pass

    @property
    def is_active(self) -> bool:
        """
        Returns:
            bool: True if carrier is active, False otherwise.
        """
        pass

    @property
    def is_hooked(self) -> bool:
        """
        Returns:
            bool: True if connected to inserting hook, False otherwise.
        """
        pass

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: ID of carrier, corresponds to order in machine.
        """
        pass

    @staticmethod
    def starting_position(machine_state: Knitting_Machine_State | None = None) -> Needle_Bed_Position:
        """
        Args:
            machine_state (Knitting_Machine_State | None): The machine state to base the carrier position on.

        Returns:
            Needle_Bed_Position: The default starting position for carriers.
        """
        return Needle_Bed_Position(
            parking_position=Side_of_Needle_Bed.Right_Side,
            rightmost_slot=machine_state.needle_count if machine_state is not None else 540,
        )

    def __lt__(self, other: int | Yarn_Carrier_State) -> bool:
        """Compare if this carrier ID is less than another carrier or integer.

        Args:
            other (int | Yarn_Carrier_State): The carrier or integer to compare with.

        Returns:
            bool: True if this carrier's ID is less than the other.
        """
        return int(self) < int(other)

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison of a carrier to another carrier or object representing a carrier.
        Args:
            other (int | Yarn_Carrier_State | Yarn_Carrier_Set | Sequence[int | Yarn_Carrier_State]): The carrier or object representing a carrier.

        Returns:
            bool: True if this carrier is equal to the other. Carrier sets are equal if they only contain this carrier.
        """
        if isinstance(other, Yarn_Carrier_State):
            return (
                self.carrier_id == other.carrier_id
                and self.position_on_bed == other.position_on_bed
                and self.is_active == other.is_active
                and self.is_hooked == other.is_hooked
            )
        elif isinstance(other, int):
            return self.carrier_id == int(other)
        elif isinstance(other, (Yarn_Carrier_Set, Sequence)):
            if len(other) != 1:
                return False
            return self == other[0]
        else:
            return False

    def __hash__(self) -> int:
        """Return hash value based on carrier ID.

        Returns:
            int: Hash value of the carrier ID.
        """
        return self.carrier_id

    def __str__(self) -> str:
        """Return string representation of the carrier.

        Returns:
            str: String representation showing carrier ID and yarn if different from ID.
        """
        if self.yarn.yarn_id == str(self.carrier_id):
            return str(self.carrier_id)
        else:
            return f"{self.carrier_id}:{self.yarn}"

    def __repr__(self) -> str:
        """Return string representation of the carrier.

        Returns:
            str: String representation of the carrier.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer representation of the carrier.

        Returns:
            int: The carrier ID as an integer.
        """
        return self.carrier_id


class Yarn_Carrier(Yarn_Carrier_State):
    """A class representing an individual yarn carrier on a knitting machine.
    Yarn carriers hold yarn and can be moved to different positions on the machine, activated for knitting operations, and connected to insertion hooks for yarn manipulation.
    Each carrier tracks its state including position, active status, and hook connection.
    """

    def __init__(
        self,
        carrier_id: int,
        yarn: Machine_Knit_Yarn | None = None,
        yarn_properties: Yarn_Properties | None = None,
        knit_graph: Knit_Graph | None = None,
        machine_state: Knitting_Machine | None = None,
    ) -> None:
        """Initialize a yarn carrier with specified ID and optional yarn configuration.

        Args:
            carrier_id (int): Unique identifier for this yarn carrier.
            yarn (None | Machine_Knit_Yarn, optional): Existing machine knit yarn to assign to this carrier. Defaults to None.
            yarn_properties (Yarn_Properties | None, optional): Properties for creating new yarn if yarn parameter is None. Defaults to None.
        """
        self._machine_state: Knitting_Machine | None = machine_state
        self._carrier_id: int = carrier_id
        self._is_active: bool = False
        self._is_hooked: bool = False
        self._position: Needle_Bed_Position = self.starting_position(self._machine_state)
        if yarn is not None:
            self._yarn: Machine_Knit_Yarn = yarn
            if knit_graph is not None:
                self._yarn.knit_graph = knit_graph
        else:
            if yarn_properties is None and self._machine_state is not None:
                yarn_properties = Yarn_Properties(
                    color=self._machine_state.machine_specification.get_yarn_color(self.carrier_id)
                )
            self._yarn: Machine_Knit_Yarn = Machine_Knit_Yarn(self, yarn_properties, knit_graph=knit_graph)

    @property
    def knitting_machine(self) -> Knitting_Machine | None:
        """
        Returns:
            Knitting_Machine_State | None: The machine state of the knitting machine that owns this component or None if the machine has not been specified.
        """
        return self._machine_state

    @property
    def carrier_id(self) -> int:
        """Get the unique identifier of this carrier.

        Returns:
            int: ID of carrier, corresponds to order in machine.
        """
        return self._carrier_id

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """Get the yarn held on this carrier.

        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        return self._yarn

    @property
    def position_on_bed(self) -> Needle_Bed_Position:
        """
        Returns:
            Needle_Bed_Position: The current position of this carrier.
        """
        return self._position

    @property
    def is_active(self) -> bool:
        """
        Returns:
            bool: True if carrier is active, False otherwise.
        """
        return self._is_active

    @is_active.setter
    def is_active(self, active_state: bool) -> None:
        """Set the active state of the carrier and update related properties.

        Args:
            active_state (bool): True to activate carrier, False to deactivate.
        """
        if active_state is True:
            self._is_active = True
        else:
            self._is_active = False
            self.is_hooked = False
            self._position.take_off_bed()

    @property
    def is_hooked(self) -> bool:
        """Check if the carrier is connected to the insertion hook.

        Returns:
            bool: True if connected to inserting hook, False otherwise.
        """
        return self._is_hooked

    @is_hooked.setter
    def is_hooked(self, hook_state: bool) -> None:
        """Set the hook state of the carrier.

        Args:
            hook_state (bool): True to connect to hook, False to disconnect.
        """
        self._is_hooked = hook_state

    def set_position(self, needle: Needle | None, direction: Carriage_Pass_Direction | None = None) -> None:
        """
        Set the position of this carrier to the given needle or set it to be off the needle bed.

        Args:
            needle (Needle | None): The needle to position the carrier relative or None if it is off the needle bed.
            direction (Carriage_Pass_Direction | None, optional): The direction the carrier should be moving in. Defaults to None.

        Warnings:


        """
        if needle is not None and not self.is_active:
            raise Use_Inactive_Carrier_Exception(self.carrier_id)
        self.position_on_bed.set_position(needle, direction)

    def bring_in(self) -> None:
        """Record bring-in operation to activate the carrier without using insertion hook.

        Warns:
            In_Active_Carrier_Warning: If carrier is already active.
        """
        if self.is_active:
            warnings.warn(
                In_Active_Carrier_Warning(self.carrier_id),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )  # Warn user but do no in action
        self.is_active = True

    def inhook(self) -> None:
        """Record inhook operation to bring in carrier using insertion hook."""
        self.bring_in()
        self.is_hooked = True

    def releasehook(self) -> None:
        """Record release hook operation to disconnect carrier from insertion hook."""
        self.is_hooked = False

    def out(self) -> None:
        """Record out operation to deactivate the carrier and move to grippers.

        Warns:
            Out_Inactive_Carrier_Warning: If carrier is already inactive.
        """
        if not self.is_active:
            warnings.warn(
                Out_Inactive_Carrier_Warning(self.carrier_id),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )  # Warn use but do not do out action
        self._position.take_off_bed()
        self._is_active = False
        self._is_hooked = False

    def outhook(self) -> None:
        """Record outhook operation to cut and remove carrier using insertion hook.

        Raises:
            Hooked_Carrier_Exception: If carrier is already connected to yarn inserting hook.
        """
        if self.is_hooked:
            raise Hooked_Carrier_Exception(self.carrier_id)
        else:
            self.out()
