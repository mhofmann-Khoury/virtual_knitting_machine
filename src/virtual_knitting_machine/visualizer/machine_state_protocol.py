"""Module contains the Knitting Machine State Protocol"""

from typing import Protocol

from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Knitting_Machine_State_Protocol(Protocol):
    """A protocol that covers both Knitting_Machine and Knitting_Machine_Snapshot.

    This protocol ensures that an object can be rendered in the Knitout Visualizer.
    """

    @property
    def slot_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range of needle slots holding loops. The first value is the left most slot. The second value is the right most slot.
        """
        pass

    @property
    def sliders_are_clear(self) -> bool:
        """
        Returns:
            bool: True if there are no loops on back for front bed sliders. False otherwise.
        """
        pass

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


class Mock_Machine_State(Knitting_Machine_State_Protocol):

    def __init__(self, active_needles: list[Needle], rack: int = 0, all_needle_rack: bool = False) -> None:
        self.active_front_needles: list[Needle] = [n for n in active_needles if n.is_front and not n.is_slider]
        self.active_front_sliders: list[Needle] = [n for n in active_needles if n.is_front and n.is_slider]
        self.active_back_needles: list[Needle] = [n for n in active_needles if n.is_back and not n.is_slider]
        self.active_back_sliders: list[Needle] = [n for n in active_needles if n.is_back and n.is_slider]
        self._rack: int = rack
        self._all_needle_rack: bool = all_needle_rack
        self._leftmost_slot: int = int(min(*active_needles)) if len(active_needles) > 0 else 0
        self._rightmost_slot: int = int(max(*active_needles)) if len(active_needles) > 0 else 0

    @property
    def slot_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range of needle slots holding loops. The first value is the left most slot. The second value is the right most slot.
        """
        return self._leftmost_slot, self._rightmost_slot

    @property
    def sliders_are_clear(self) -> bool:
        """
        Returns:
            bool: True if there are no loops on back for front bed sliders. False otherwise.
        """
        return len(self.active_front_sliders) == 0 and len(self.active_back_sliders) == 0

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the knitting machine is set for all needle rack, False otherwise.
        """
        return self._all_needle_rack

    @property
    def rack(self) -> int:
        """
        Returns:
            int: The racking offset of the knitting machine at the time the snapshot was created.
        """
        return self._rack
