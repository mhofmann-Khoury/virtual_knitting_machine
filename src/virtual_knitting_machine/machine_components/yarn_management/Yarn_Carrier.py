"""Yarn_Carrier representation module for managing individual yarn carriers on knitting machines.
This module provides the Yarn_Carrier class which represents a single yarn carrier that can hold yarn, track position, and manage active/hooked states for knitting operations."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast, runtime_checkable

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Use_Inactive_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import (
    get_user_warning_stack_level_from_virtual_knitting_machine_package,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    In_Loose_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needle_bed_position import Needle_Bed_Position, Relative_to_Needle_Bed
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import checked_operation

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


@runtime_checkable
class Yarn_Carrier_State(Relative_to_Needle_Bed, Protocol[Machine_LoopT]):
    """A class from which all read-only attributes and properties of a yarn-carrier can be accessed.
    This class defines common properties between yarn-carriers and yarn-carrier-snapshots.
    """

    @property
    def yarn(self) -> Machine_Knit_Yarn[Machine_LoopT]:
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

    @property
    def starting_position(self) -> Needle_Bed_Position:
        """
        Returns:
            Needle_Bed_Position: The default starting position for carriers.
        """
        return Needle_Bed_Position(self.knitting_machine, parking_position=Side_of_Needle_Bed.Right_Side)

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


class Yarn_Carrier(Yarn_Carrier_State[Machine_LoopT]):
    """A class representing an individual yarn carrier on a knitting machine.
    Yarn carriers hold yarn and can be moved to different positions on the machine, activated for knitting operations, and connected to insertion hooks for yarn manipulation.
    Each carrier tracks its state including position, active status, and hook connection.
    """

    def __init__(
        self,
        carrier_id: int,
        machine_state: Knitting_Machine[Machine_LoopT],
        yarn_properties: Yarn_Properties | None = None,
    ) -> None:
        """Initialize a yarn carrier with specified ID and optional yarn configuration.

        Args:
            carrier_id (int): Unique identifier for this yarn carrier.
            yarn_properties (Yarn_Properties | None, optional): Properties for creating new yarn if yarn parameter is None. Defaults to None.
            machine_state (Knitting_Machine[Machine_LoopT] | None): The machine state that owns this carrier or None.
        """
        self._machine_state: Knitting_Machine[Machine_LoopT] = machine_state
        self._carrier_id: int = carrier_id
        self._is_active: bool = False
        self._is_hooked: bool = False
        self._position: Needle_Bed_Position = self.starting_position
        if yarn_properties is None and self._machine_state is not None:
            yarn_properties = Yarn_Properties(
                name=f"yarn-from-c{carrier_id}",
                color=self._machine_state.machine_specification.get_yarn_color(self.carrier_id),
            )
        knit_graph: Knit_Graph[Machine_LoopT] | None = (
            self.knitting_machine.knit_graph if self.knitting_machine is not None else None
        )
        self._yarn: Machine_Knit_Yarn[Machine_LoopT] = Machine_Knit_Yarn[Machine_LoopT](
            self, yarn_properties, knit_graph=knit_graph
        )

    @property
    def knitting_machine(self) -> Knitting_Machine[Machine_LoopT]:
        """
        Returns:
            Knitting_Machine_State: The knitting machine that owns this carrier.
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
    def yarn(self) -> Machine_Knit_Yarn[Machine_LoopT]:
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

    def activate(self) -> None:
        """
        Sets the carrier to be active.
        """
        self.is_active = True

    def deactivate(self) -> None:
        """Sets the carrier to be inactive."""
        self.is_active = False

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

    @checked_operation
    def set_position(self, needle: Needle | None, direction: Carriage_Pass_Direction | None = None) -> None:
        """
        Set the position of this carrier to the given needle or set it to be off the needle bed.

        Args:
            needle (Needle | None): The needle to position the carrier relative or None if it is off the needle bed.
            direction (Carriage_Pass_Direction | None, optional): The direction the carrier should be moving in. Defaults to None.

        Raises:
            Use_Inactive_Carrier_Exception: If the carrier is not active when its position is being set.
        """
        with self.handle_violations(handler=self.activate):
            if not self.is_active:
                raise Use_Inactive_Carrier_Exception(self)
        if self.violation_policy.proceed:
            self.position_on_bed.set_position(needle, direction)

    @checked_operation
    def make_loop(self, needle: Needle[Machine_LoopT], **_loop_kwargs: Any) -> Machine_LoopT:
        """

        Args:
            needle (Needle[Machine_LoopT]): The needle to form the loop on.
            **_loop_kwargs (Any): Additional keyword argument to pass to the loop.

        Returns:
            Machine_LoopT: The loop formed with the carrier on the given needle.

        Raises:
            Use_Inactive_Carrier_Exception: If the carrier is not active when forming the loop.
        """
        with self.handle_violations(handler=self.activate):
            if not self.is_active:
                raise Use_Inactive_Carrier_Exception(self)
        assert self.violation_policy.proceed
        return cast(
            Machine_LoopT,
            self.machine_specification.loop_class(
                cast(Needle[Machine_Knit_Loop], needle), cast(Machine_Knit_Yarn[Machine_Knit_Loop], self.yarn)
            ),
        )

    def bring_in(self) -> None:
        """Record bring-in operation to activate the carrier without using insertion hook.

        Warns:
            In_Active_Carrier_Warning: If carrier is already active.
            In_Loose_Carrier_Warning: If carrier is bringing in a yarn that is neither on the yarn-inserting-hook nor looped on a needle.
        """
        if self.is_active:
            warnings.warn(
                In_Active_Carrier_Warning(self),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )
        if not (self.is_hooked or self.yarn.last_needle is not None):
            warnings.warn(
                In_Loose_Carrier_Warning(self),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )
        self.is_active = True

    def inhook(self) -> None:
        """Record inhook operation to bring in carrier using insertion hook."""
        self.is_hooked = True
        self.bring_in()

    def releasehook(self) -> None:
        """Record release hook operation to disconnect carrier from insertion hook."""
        self.is_hooked = False

    def out(self) -> None:
        """Record out operation to deactivate the carrier and move to grippers."""
        if not self.is_active:
            warnings.warn(
                Out_Inactive_Carrier_Warning(self.carrier_id),
                stacklevel=get_user_warning_stack_level_from_virtual_knitting_machine_package(),
            )  # Warn use but do not do out action
        self._position.take_off_bed()
        self._is_active = False
        self._is_hooked = False

    def outhook(self) -> None:
        """Record outhook operation to cut and remove carrier using insertion hook."""
        self.out()
