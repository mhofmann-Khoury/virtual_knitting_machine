"""Module containing Yarn Carrier Snapshot class"""

from __future__ import annotations

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn


class Yarn_Carrier_Snapshot:
    """
    A snapshot of the state of a carrier at the time this instance was created.
    """

    def __init__(self, yarn_carrier: Yarn_Carrier):
        self._carrier = yarn_carrier
        self._is_active: bool = yarn_carrier.is_active
        self._is_hooked: bool = yarn_carrier.is_hooked
        self._position: None | int = yarn_carrier.position
        self._last_direction: None | Carriage_Pass_Direction = yarn_carrier.last_direction
        self._yarn: Machine_Knit_Yarn = yarn_carrier.yarn
        self._last_loop_id: int | None = int(self.yarn.last_loop) if self.yarn.last_loop is not None else None

    @property
    def carrier(self) -> Yarn_Carrier:
        """
        Returns:
            Yarn_Carrier: The yarn carrier that this snapshot was taken form.

        Notes:
            The carrier object will update over time and may no longer match the state of the snapshot.
        """
        return self._carrier

    @property
    def last_loop_id(self) -> int | None:
        """
        Returns:
            int | None: The last loop formed on the yarn of this carrier or None if it had not formed a loop yet.
        """
        return self._last_loop_id

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: The carrier id of the snapshot carrier.
        """
        return self.carrier.carrier_id

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """
        Returns:
            Machine_Knit_Yarn: The machine knit yarn that belonged to this carrier at the time of this snapshot.

        Notes:
            The yarn object will update after the snapshot has been created.
        """
        return self._yarn

    @property
    def position(self) -> None | int:
        """Get the needle position that the carrier sits at or None if inactive.

        Returns:
            None | int: The needle position that the carrier sits at or None if the carrier is not active.
        """
        return self._position

    @property
    def is_active(self) -> bool:
        """
        Returns:
            bool: True if the carrier was active at the time of the snapshot, False otherwise.
        """
        return self._is_active

    @property
    def is_hooked(self) -> bool:
        """
        Returns:
            bool: True if the carrier was connected to inserting hook at the time of the snapshot, False otherwise.
        """
        return self._is_hooked

    @property
    def last_direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction | None: The last direction that the carrier was moved in or None if the carrier is inactive.
        """
        return self._last_direction

    def direction_to_needle(self, needle_position: int | Needle) -> Carriage_Pass_Direction:
        """
        Args:
            needle_position (int | Needle): The position of a needle to move towards.

        Returns:
            Carriage_Pass_Direction: The direction that the carrier will move to reach the given position from its current position.
        """
        if self.position is None or int(needle_position) < self.position:  # inactive carriers enter from the right
            return Carriage_Pass_Direction.Leftward
        elif int(needle_position) > self.position:
            return Carriage_Pass_Direction.Rightward
        else:
            assert isinstance(self.last_direction, Carriage_Pass_Direction)
            return self.last_direction.opposite()

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

    def loop_made_before_snapshot(self, loop: int | Machine_Knit_Loop) -> bool:
        """
        Args:
            loop (int | Machine_Knit_Loop): The loop (or loop_id) to compare to the timing of this snapshot.

        Returns:
            bool: True if the given loop was formed prior to the snapshot, False otherwise.

        Notes:
            This program assumes that the loop belongs to the knitgraph rendered by this knitting machine.
        """
        return int(loop) <= self.last_loop_id if isinstance(self.last_loop_id, int) else False

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison of a carrier to another carrier or object representing a carrier.
        Args:
            other (int | Yarn_Carrier | Yarn_Carrier_Set | list[int | Yarn_Carrier] | Yarn_Carrier_Snapshot): The carrier or object representing a carrier.

        Returns:
            bool: True if this carrier is equal to the other. Carrier sets are equal if they only contain this carrier.
        """
        if isinstance(other, Yarn_Carrier_Snapshot):
            return (
                self.carrier_id == other.carrier_id
                and self.position == other.position
                and self.is_active == other.is_active
                and self.is_hooked == other.is_hooked
                and self.last_direction == other.last_direction
                and self.last_loop_id == other.last_loop_id
            )
        if isinstance(other, (Yarn_Carrier, int)):
            return self.carrier_id == int(other)
        elif isinstance(other, (Yarn_Carrier_Set, list)):
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
            str: The string of the carrier and timing information based on the last loop formed on that yarn.
        """
        return f"{self.carrier} when Loop {self.last_loop_id} as formed"

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
