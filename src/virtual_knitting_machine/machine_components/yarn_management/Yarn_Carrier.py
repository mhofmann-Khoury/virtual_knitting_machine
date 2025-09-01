"""Yarn_Carrier representation module for managing individual yarn carriers on knitting machines.
This module provides the Yarn_Carrier class which represents a single yarn carrier that can hold yarn, track position, and manage active/hooked states for knitting operations."""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Hooked_Carrier_Exception,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import (
    Machine_Knit_Yarn,
)

if TYPE_CHECKING:
    from virtual_knitting_machine.machine_components.needles.Needle import Needle
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
        Yarn_Carrier_Set,
    )


class Yarn_Carrier:
    """A class representing an individual yarn carrier on a knitting machine.
    Yarn carriers hold yarn and can be moved to different positions on the machine, activated for knitting operations, and connected to insertion hooks for yarn manipulation.
    Each carrier tracks its state including position, active status, and hook connection.
    """

    STOPPING_DISTANCE: int = 10  # int: The distance carriers are moved when kicked to avoid conflicts.

    def __init__(self, carrier_id: int, yarn: None | Machine_Knit_Yarn = None, yarn_properties: Yarn_Properties | None = None, knit_graph: Knit_Graph | None = None) -> None:
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
        self._last_direction: None | Carriage_Pass_Direction = None
        if yarn is not None:
            self._yarn: Machine_Knit_Yarn = yarn
            self._yarn.knit_graph = knit_graph
        else:
            self._yarn: Machine_Knit_Yarn = Machine_Knit_Yarn(self, yarn_properties, knit_graph=knit_graph)

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """Get the yarn held on this carrier.

        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        return self._yarn

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
        Infers the direction of the carrier movement from the differences between the states.
        If the direction is ambiguous because the operation occurs at the same location, the last direction is reversed.

        Args:
            new_position (None | Needle | int): The new position for the carrier, None if inactive, or a needle/position value.
        """
        if new_position is None:
            self._position = None
            self.last_direction = None  # No position means no carrier position direction.
        else:
            if self.position is None:
                self.last_direction = Carriage_Pass_Direction.Leftward  # moving in a leftward position when the carrier is inserted
            else:
                if int(new_position) < self.position:
                    self.last_direction = Carriage_Pass_Direction.Leftward
                elif int(new_position) > self.position:
                    self.last_direction = Carriage_Pass_Direction.Rightward
                else:
                    assert isinstance(self.last_direction, Carriage_Pass_Direction)
                    self.last_direction = self.last_direction.opposite()
            self._position = int(new_position)

    def direction_to_needle(self, needle_position: int | Needle) -> Carriage_Pass_Direction:
        """
        Args:
            needle_position (int | Needle): The position of a needle to move towards.

        Returns:
            Carriage_Pass_Direction: The direction that the carrier will move to reach the given position from its current position.
        """
        if self.position is None:  # inactive carriers enter from the right
            return Carriage_Pass_Direction.Leftward
        elif int(needle_position) < self.position:
            return Carriage_Pass_Direction.Leftward
        elif int(needle_position) > self.position:
            return Carriage_Pass_Direction.Rightward
        else:
            assert isinstance(self.last_direction, Carriage_Pass_Direction)
            return self.last_direction.opposite()

    @property
    def last_direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction | None: The last direction that the carrier was moved in or None if the carrier is inactive.
        """
        return self._last_direction

    @last_direction.setter
    def last_direction(self, direction: None | Carriage_Pass_Direction) -> None:
        """
        Sets the last direction that the carrier was move in.
        Args:
            direction (Carriage_Pass_Direction | None): The direction of the last move or None if the carrier is inactive.
        """
        self._last_direction = direction

    @property
    def conflicting_needle_slot(self) -> int | None:
        """
        Returns:
            int | None: The needle slot that currently conflicts with the carrier or None if the carrier is not active.
        """
        if not self.is_active:
            return None
        else:
            assert isinstance(self.position, int)
            assert isinstance(self.last_direction, Carriage_Pass_Direction)
            if self.last_direction is Carriage_Pass_Direction.Leftward:
                return self.position - 1
            else:
                return self.position + 1

    @property
    def needle_range(self) -> None | tuple[int, int]:
        """
        Returns:
            None | tuple[int, int]: The range of positions that a carrier may exist after an ambiguous movement or None if the carrier is inactive.
        """
        if self.position is None:
            return None
        elif self.last_direction is Carriage_Pass_Direction.Leftward:
            return self.position - self.STOPPING_DISTANCE, self.position
        else:
            return self.position, self.position + self.STOPPING_DISTANCE

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
        self.last_direction = Carriage_Pass_Direction.Leftward

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
        self.last_direction = None

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
