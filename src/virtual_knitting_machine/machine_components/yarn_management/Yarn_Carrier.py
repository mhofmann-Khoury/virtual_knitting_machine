"""Yarn_Carrier representation module for managing individual yarn carriers on knitting machines.
This module provides the Yarn_Carrier class which represents a single yarn carrier that can hold yarn, track position, and manage active/hooked states for knitting operations."""
from __future__ import annotations
import warnings
from typing import TYPE_CHECKING

from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Change_Active_Yarn_Exception, Hooked_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import In_Active_Carrier_Warning, Out_Inactive_Carrier_Warning
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set


class Yarn_Carrier:
    """A class representing an individual yarn carrier on a knitting machine.
    Yarn carriers hold yarn and can be moved to different positions on the machine, activated for knitting operations, and connected to insertion hooks for yarn manipulation.
    Each carrier tracks its state including position, active status, and hook connection."""

    def __init__(self, carrier_id: int, yarn: None | Machine_Knit_Yarn = None, yarn_properties: Yarn_Properties | None = None) -> None:
        """Initialize a yarn carrier with specified ID and optional yarn configuration.

        Args:
            carrier_id (int): Unique identifier for this yarn carrier.
            yarn (None | Machine_Knit_Yarn, optional): Existing machine knit yarn to assign to this carrier. Defaults to None.
            yarn_properties (Yarn_Properties | None, optional): Properties for creating new yarn if yarn parameter is None. Defaults to None.
        """
        self._carrier_id: int = carrier_id
        self._is_active: bool = False
        self._is_hooked: bool = False
        self._position: None | int = None
        if yarn is not None:
            self._yarn = yarn
        elif yarn_properties is None:
            self.yarn = Yarn_Properties()
        else:
            self.yarn = yarn_properties

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """Get the yarn held on this carrier.

        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        return self._yarn

    @yarn.setter
    def yarn(self, yarn_properties: Yarn_Properties) -> None:
        """Set new yarn properties for this carrier, creating a new Machine_Knit_Yarn instance.

        Args:
            yarn_properties (Yarn_Properties): Properties for the new yarn to be created.

        Raises:
            Change_Active_Yarn_Exception: If attempting to change yarn while carrier is active.
        """
        if self.is_active:
            raise Change_Active_Yarn_Exception(self.carrier_id)
        self._yarn: Machine_Knit_Yarn = Machine_Knit_Yarn(self, yarn_properties)

    @property
    def position(self) -> None | int:
        """Get the needle position that the carrier sits at or None if inactive.

        Returns:
            None | int: The needle position that the carrier sits at or None if the carrier is not active.
        """
        return self._position

    @position.setter
    def position(self, new_position: None | Needle | int) -> None:
        """Set the position of the carrier.

        Args:
            new_position (None | Needle | int): The new position for the carrier, None if inactive, or a needle/position value.
        """
        if new_position is None:
            self._position = None
        else:
            self._position = int(new_position)

    @property
    def is_active(self) -> bool:
        """Check if the carrier is currently active (off the grippers).

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
            self.position = None

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

    def bring_in(self) -> None:
        """Record bring-in operation to activate the carrier without using insertion hook.

        Warns:
            In_Active_Carrier_Warning: If carrier is already active.
        """
        if self.is_active:
            warnings.warn(In_Active_Carrier_Warning(self.carrier_id))  # Warn user but do no in action
        self.is_active = True

    def inhook(self) -> None:
        """Record inhook operation to bring in carrier using insertion hook.
        """
        self.bring_in()
        self.is_hooked = True

    def releasehook(self) -> None:
        """Record release hook operation to disconnect carrier from insertion hook.
        """
        self.is_hooked = False

    def out(self) -> None:
        """Record out operation to deactivate the carrier and move to grippers.

        Warns:
            Out_Inactive_Carrier_Warning: If carrier is already inactive.
        """
        if not self.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(self.carrier_id))  # Warn use but do not do out action
        self.is_active = False

    def outhook(self) -> None:
        """Record outhook operation to cut and remove carrier using insertion hook.

        Raises:
            Hooked_Carrier_Exception: If carrier is already connected to yarn inserting hook.
        """
        if self.is_hooked:
            raise Hooked_Carrier_Exception(self.carrier_id)
        else:
            self.out()

    @property
    def carrier_id(self) -> int:
        """Get the unique identifier of this carrier.

        Returns:
            int: ID of carrier, corresponds to order in machine.
        """
        return self._carrier_id

    def __lt__(self, other: int | Yarn_Carrier) -> bool:
        """Compare if this carrier ID is less than another carrier or integer.

        Args:
            other (int | Yarn_Carrier): The carrier or integer to compare with.

        Returns:
            bool: True if this carrier's ID is less than the other.
        """
        return int(self) < int(other)

    def __eq__(self, other: int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]) -> bool:
        """
        Equality comparison of a carrier to another carrier or object representing a carrier.
        Args:
            other (int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier]): The carrier or object representing a carrier.

        Returns:
            bool: True if this carrier is equal to the other. Carrier sets are equal if they only contain this carrier.
        """
        if isinstance(other, Yarn_Carrier) or isinstance(other, int):
            return self.carrier_id == int(other)
        else:  # Yarn_Carrier_Set or list of carriers
            if len(other) != 1:
                return False
            return self == other[0]

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
        if self.yarn.yarn_id == str(self._carrier_id):
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
