"""Module containing Yarn Carrier Snapshot class"""

from __future__ import annotations

from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Carrier_Position,
    Yarn_Carrier,
    Yarn_Carrier_State,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn


class Yarn_Carrier_Snapshot(Yarn_Carrier_State):
    """
    A snapshot of the state of a carrier at the time this instance was created.
    """

    def __init__(self, yarn_carrier: Yarn_Carrier):
        self._carrier_id: int = yarn_carrier.carrier_id
        self._is_active: bool = yarn_carrier.is_active
        self._is_hooked: bool = yarn_carrier.is_hooked
        self._position: Carrier_Position = Carrier_Position(None, default_rack=yarn_carrier.rack)
        self._position.set_position(yarn_carrier.needle, yarn_carrier.last_direction)
        self._yarn: Machine_Knit_Yarn = yarn_carrier.yarn
        self._last_loop_id: int | None = int(self.yarn.last_loop) if self.yarn.last_loop is not None else None

    @property
    def last_loop_id(self) -> int | None:
        """
        Returns:
            int | None: The last loop formed on the yarn of this carrier or None if it had not formed a loop yet.
        """
        return self._last_loop_id

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        return self._yarn

    @property
    def position(self) -> Carrier_Position:
        return self._position

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_hooked(self) -> bool:
        return self._is_hooked

    @property
    def carrier_id(self) -> int:
        return self._carrier_id

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

    def __str__(self) -> str:
        """Return string representation of the carrier.

        Returns:
            str: The string of the carrier and timing information based on the last loop formed on that yarn.
        """
        return f"c{self.carrier_id} when Loop {self.last_loop_id} as formed"
