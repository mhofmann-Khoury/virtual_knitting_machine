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
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from virtual_knitting_machine.machine_components.needles.Needle import Needle
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set


class Carrier_Position:
    """
    A class used to keep track of the position of carriers relative to needles on the machine bed.
    """

    STOPPING_DISTANCE: int = 10  # int: The distance carriers are moved when kicked to avoid conflicts.

    def __init__(self, machine_state: Knitting_Machine | None, default_rack: int = 0) -> None:
        self._default_rack: int = default_rack
        self._machine_state: Knitting_Machine | None = machine_state
        self._needle: Needle | None = None
        self._last_direction: Carriage_Pass_Direction | None = None

    @property
    def rack(self) -> int:
        """
        Returns:
            int: The current racking alignment of the machine state. Defaults to 0 if this position is not associated with a specific machine.
        """
        return self._machine_state.rack if self._machine_state is not None else self._default_rack

    @property
    def needle(self) -> Needle | None:
        """
        Returns:
            Needle | None: The needle that the carrier is positioned relative to. None if the carrier is not positioned on the bed.
        """
        return self._needle

    @property
    def last_direction(self) -> Carriage_Pass_Direction | None:
        """
        Returns:
            Carriage_Pass_Direction | None: The last direction the carrier moved or None if it is not positioned on the bed.
        """
        return self._last_direction

    @property
    def on_bed(self) -> bool:
        """
        Returns:
            bool: True if the carrier is position relative to a needle on the bed. False otherwise.
        """
        return self.needle is not None

    @property
    def between_needles(self) -> tuple[Needle, Needle] | None:
        """
        Returns:
            tuple[Needle, Needle] | None: The needles that a carrier is positioned between or None if it is not on the needle bed.
        """
        if self.needle is None:
            return None
        elif self._last_direction is Carriage_Pass_Direction.Rightward:
            return self.needle, self.needle + 1
        else:
            return self.needle - 1, self.needle

    @property
    def conflicting_needle_slot(self) -> int | None:
        """
        Returns:
            int | None: The needle slot that currently conflicts with the carrier or None if the carrier is not active.
        """
        if self.slot_position is None:
            return None
        elif self.last_direction is Carriage_Pass_Direction.Leftward:
            return self.slot_position - 1
        else:
            return self.slot_position + 1

    @property
    def slot_position(self) -> int | None:
        """
        Returns:
            int | None: The front-bed slot of the carrier's current position or None if the carrier is not on the Needle bed.
        """
        return self.needle.slot_number(self.rack) if self.needle is not None else None

    @property
    def needle_range(self) -> None | tuple[int, int]:
        """
        Returns:
            None | tuple[int, int]: The range of positions that a carrier may exist after an ambiguous movement or None if the carrier is inactive.
        """
        if self.slot_position is None:
            return None
        elif self.last_direction is Carriage_Pass_Direction.Leftward:
            return self.slot_position - self.STOPPING_DISTANCE, self.slot_position
        else:
            return self.slot_position, self.slot_position + self.STOPPING_DISTANCE

    def take_off_bed(self) -> None:
        """
        Sets the position of the carrier to be off the needle bed.
        """
        self.set_position(None)

    def direction_to_needle(self, needle: Needle, rack: int | None = None) -> Carriage_Pass_Direction:
        """
        Args:
            needle (Needle): The needle to move towards.
            rack (int, optional): The rack alignment of the machine. Defaults to the racking of the machine associated with this position or 0 if no machine is associated.

        Returns:
            Carriage_Pass_Direction: The direction that the carrier will move to reach the given position from its current position.

        Notes:
            If the carrier is not currently on the bed, the direction will be Leftward.
            If the new needle is at the same position as the carrier, the carrier's last direction will be reversed.
        """
        if self.needle is None:
            return Carriage_Pass_Direction.Leftward
        else:
            if rack is None:
                rack = self.rack
            direction = Carriage_Pass_Direction.get_direction_between_needles(self.needle, needle, rack)
            if direction is None:
                assert self._last_direction is not None
                return self._last_direction.opposite()
            else:
                return direction

    def set_position(self, needle: Needle | None, direction: Carriage_Pass_Direction | None = None) -> None:
        """
        Sets the position based on the given needle and current racking of the machine state.

        Args:
            needle (Needle): The new needle position that the carrier will move to or None if the carrier is moved off the needle bed.
            direction (Carriage_Pass_Direction | None, optional): The specific direction to set the carriage pass direction to. Defaults to inferring from the needle position and current state.

        Notes:
            If the carrier is not currently on the bed, the last direction will be set to Leftward.
            If the new needle is at the same position as the carrier, the carrier's last direction will be reversed.
        """
        if needle is None:
            self._needle = None
            self._last_direction = Carriage_Pass_Direction.Leftward
        elif needle.is_slider:
            raise ValueError(f"Carriers cannot be positioned at slider needles: {needle}")
        else:
            if direction is None:
                direction = self.direction_to_needle(needle, self.rack)
            self._last_direction = direction
            self._needle = needle

    def __eq__(self, other: object) -> bool:
        """
        Args:
            other (Carrier_Position | Yarn_Carrier | int): The other carrier position to compare to. If the position is an integer, only the slot number is compared.

        Returns:
            bool: True if this position matches the given position.
        """
        if isinstance(other, (Carrier_Position, Yarn_Carrier_State)):
            return self.needle == other.needle and self.last_direction == other.last_direction
        elif isinstance(other, int):
            return self.slot_position == other
        else:
            return False


@runtime_checkable
class Yarn_Carrier_State(Protocol):
    """A class from which all read-only attributes and properties of a yarn-carrier can be accessed.
    This class defines common properties between yarn-carriers and yarn-carrier-snapshots.
    """

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """Get the yarn held on this carrier.

        Returns:
            Machine_Knit_Yarn: The yarn held on this carrier.
        """
        pass

    @property
    def position(self) -> Carrier_Position:
        """
        Returns:
            Carrier_Position: The current position of this carrier.
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
        """Check if the carrier is connected to the insertion hook.

        Returns:
            bool: True if connected to inserting hook, False otherwise.
        """
        pass

    @property
    def carrier_id(self) -> int:
        """Get the unique identifier of this carrier.

        Returns:
            int: ID of carrier, corresponds to order in machine.
        """
        pass

    @property
    def needle(self) -> Needle | None:
        """
        Returns:
            Needle | None: The needle the carrier is positioned relative to or None if the carrier is not on the needle bed.
        """
        return self.position.needle

    @property
    def last_direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction | None: The last direction that the carrier was moved in or None if the carrier is inactive.
        """
        return self.position.last_direction

    @property
    def slot_position(self) -> None | int:
        """
        Returns:
            None | int: The needle-slot that the carrier was last moved to or None if the carrier is not active.
        """
        return self.position.slot_position

    @property
    def between_needles(self) -> tuple[Needle, Needle] | None:
        """
        Returns:
            tuple[Needle, Needle] | None: The needles that a carrier is positioned between or None if it is not on the needle bed.
        """
        return self.position.between_needles

    @property
    def needle_range(self) -> None | tuple[int, int]:
        """
        Returns:
            None | tuple[int, int]: The range of positions that a carrier may exist after an ambiguous movement or None if the carrier is inactive.
        """
        return self.position.needle_range

    def direction_to_needle(self, needle: Needle, rack: int | None = None) -> Carriage_Pass_Direction:
        """
        Args:
            needle (Needle): The needle to move towards.
            rack (int, optional): The racking of the machine state. Defaults to the current racking of the machine state associated with this carrier.

        Returns:
            Carriage_Pass_Direction: The direction that the carrier will move to reach the given needle from its current position.
        """
        return self.position.direction_to_needle(needle, rack)

    def conflicting_needle_slot(self) -> int | None:
        """
        Returns:
            int | None: The needle slot that currently conflicts with the carrier or None if the carrier is not active.
        """
        return self.position.conflicting_needle_slot

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
                and self.position == other.position
                and self.is_active == other.is_active
                and self.is_hooked == other.is_hooked
            )
        if isinstance(other, int):
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
        self._position: Carrier_Position = Carrier_Position(self._machine_state)
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
    def rack(self) -> int:
        """
        Returns:
            int: The current racking alignment of the machine state. Defaults to 0 if this position is not associated with a specific machine.
        """
        return self._position.rack

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
    def position(self) -> Carrier_Position:
        """
        Returns:
            Carrier_Position: The current position of this carrier.
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
        self._position.set_position(needle, direction)

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
