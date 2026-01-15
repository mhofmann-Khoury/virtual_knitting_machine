"""Module contains the Knitting Machine State Protocol"""

from collections.abc import Sequence
from typing import Protocol, overload

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Knitting_Machine_State_Protocol(Protocol):
    """A protocol that covers both Knitting_Machine and Knitting_Machine_Snapshot.

    This protocol ensures that an object can be rendered in the Knitout Visualizer.
    """

    @property
    def slot_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range of needle slots holding loops. The first value is the left most slot. The second value is the right most slot.

        Notes:
            If there are no active loops, the slot range is (0, 0).
        """
        if len(self.all_loops()) == 0 and len(self.all_slider_loops()) == 0:
            return 0, 0
        slots = [n.slot_number(self.rack) for n in self.all_loops()]
        slots.extend(n.slot_number(self.rack) for n in self.all_slider_loops())
        return min(slots), max(slots)

    @property
    def sliders_are_clear(self) -> bool:
        """
        Returns:
            bool: True if there are no loops on back for front bed sliders. False otherwise.
        """
        return len(self.all_slider_loops()) == 0

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine is set for all needle rack, False otherwise.
        """
        pass

    @property
    def rack(self) -> int:
        """
        Returns:
            int: The racking offset of the knitting machine at the time the snapshot was created.
        """
        pass

    @property
    def active_carriers(self) -> set[Yarn_Carrier]:
        """
        Returns:
            set[Yarn_Carrier]: Set of carriers that are currently active (off the grippers).
        """
        pass

    @property
    def hook_position(self) -> int | None:
        """
        Returns:
            None | int: The needle slot of the yarn-insertion hook or None if the yarn-insertion hook is not active.

        Notes:
            The hook position will be None if its exact position is to the right of the edge of the knitting machine bed.
        """
        pass

    def all_slider_loops(self) -> list[Slider_Needle]:
        """Get list of all slider needles holding loops with front bed sliders given first.

        Returns:
            list[Slider_Needle]:
                List of all slider needles holding loops with front bed sliders given first.
        """
        pass

    def all_loops(self) -> list[Needle]:
        """Get list of all needles holding loops with front bed needles given first.

        Returns:
            list[Needle]: List of all needles holding loops with front bed needles given first.
        """
        pass

    def active_floats(self) -> list[tuple[Machine_Knit_Loop, Machine_Knit_Loop]]:
        """
        Returns:
            list[tuple[Machine_Knit_Loop, Machine_Knit_Loop]]: List of all active floats between two active loops currently held on the needle beds.
        """
        active_loops = set()
        for n in self.all_loops():
            active_loops.update(n.held_loops)
        for n in self.all_slider_loops():
            active_loops.update(n.held_loops)
        floats = [(l, l.next_loop_on_yarn()) for l in active_loops]
        return [(l, nl) for l, nl in floats if isinstance(nl, Machine_Knit_Loop) and nl in active_loops]

    @overload
    def get_carrier(self, carrier: int | Yarn_Carrier) -> Yarn_Carrier: ...

    @overload
    def get_carrier(self, carrier: Sequence[int | Yarn_Carrier]) -> list[Yarn_Carrier]: ...

    def get_carrier(
        self, carrier: int | Yarn_Carrier | Sequence[int | Yarn_Carrier]
    ) -> Yarn_Carrier | list[Yarn_Carrier]:
        """Get the carrier or list of carriers owned by the machine at the given specification.

        Args:
            carrier (int | Yarn_Carrier | Sequence[int | Yarn_Carrier]):
                The carrier defined by a given carrier, carrier_set, integer or list of integers to form a set.

        Returns:
            Yarn_Carrier | list[Yarn_Carrier]:
                The carrier or list of carriers owned by the machine at the given specification.
        """
        pass
