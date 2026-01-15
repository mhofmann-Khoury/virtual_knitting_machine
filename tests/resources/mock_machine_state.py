from typing import Sequence, overload

from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Carrier_Yarn_Color_Defaults
from virtual_knitting_machine.visualizer.machine_state_protocol import Knitting_Machine_State_Protocol


class Mock_Machine_State(Knitting_Machine_State_Protocol):
    """A Mock Knitting machine used for quick testing of the diagram generator."""

    def __init__(
        self,
        carriers_to_active_needles: dict[int, list[Needle]],
        rack: int = 0,
        all_needle_rack: bool = False,
    ) -> None:
        self._rack: int = rack
        self._all_needle_rack: bool = all_needle_rack
        self.carriers: dict[int, Yarn_Carrier] = {}
        active_needles = set()
        for cid, needles in carriers_to_active_needles.items():
            active_needles.update(needles)
            for n in needles:
                self.form_loop_on_needle(cid, n)
        assert not any(len(n.held_loops) == 0 for n in active_needles)
        self.active_front_needles: list[Needle] = [n for n in active_needles if n.is_front and not n.is_slider]
        self.active_back_needles: list[Needle] = [n for n in active_needles if n.is_back and not n.is_slider]
        self.active_front_sliders: list[Slider_Needle] = [
            n for n in active_needles if n.is_front and isinstance(n, Slider_Needle)
        ]
        self.active_back_sliders: list[Slider_Needle] = [
            n for n in active_needles if n.is_back and isinstance(n, Slider_Needle)
        ]
        self._leftmost_slot: int = int(min(active_needles)) if len(active_needles) > 0 else 0
        self._rightmost_slot: int = int(max(active_needles)) if len(active_needles) > 0 else 0

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
        if isinstance(carrier, (int, Yarn_Carrier)):
            return self.carriers[int(carrier)]
        else:
            return [self.get_carrier(c) for c in carrier]

    def add_yarn_carrier(self, carrier_id: int, yarn_color: str | None = None) -> None:
        """
        Adds a yarn-carrier based on the given values.
        Args:
            carrier_id (int): The id of the yarn-carrier.
            yarn_color (str, optional): The name of the color to draw this yarn with. Defaults to the default color assigned to that carrier.
        """
        if yarn_color is None:
            yarn_color = Carrier_Yarn_Color_Defaults.get_color_by_carrier_number(carrier_id)
        self.carriers[carrier_id] = Yarn_Carrier(carrier_id, yarn_properties=Yarn_Properties(color=yarn_color))

    def form_loop_on_needle(self, carrier_id: int, needle: Needle) -> Machine_Knit_Loop:
        """
        Form a loop at the end of the yarn on the given carrier and place it on the given needle.

        Args:
            carrier_id (int): The id of the carrier to form the loop from.
            needle (Needle): The needle to form the loop on.

        Returns:
            Machine_Knit_Loop: The loop formed and added ot that needle
        """
        if carrier_id not in self.carriers:
            self.add_yarn_carrier(carrier_id)
        carrier = self.carriers[carrier_id]
        carrier.is_active = True
        if needle.is_slider:
            main_needle = needle.main_needle().opposite()
            loop = carrier.yarn.make_loop_on_needle(main_needle)
            carrier.slot_position = main_needle.slot_number(self.rack)
            main_needle.add_loop(loop)
            main_needle.transfer_loops(needle)
        else:
            loop = carrier.yarn.make_loop_on_needle(needle)
            carrier.slot_position = needle.slot_number(self.rack)
            needle.add_loop(loop)
        return loop

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

    @property
    def active_carriers(self) -> set[Yarn_Carrier]:
        """
        Returns:
            set[Yarn_Carrier]: Set of carriers that are currently active (off the grippers).
        """
        return {self.get_carrier(cid) for cid in self.carriers if self.get_carrier(cid).is_active}

    def all_slider_loops(self) -> list[Slider_Needle]:
        """Get list of all slider needles holding loops with front bed sliders given first.

        Returns:
            list[Slider_Needle]:
                List of all slider needles holding loops with front bed sliders given first.
        """
        return [*self.active_front_sliders, *self.active_back_sliders]

    def all_loops(self) -> list[Needle]:
        """Get list of all needles holding loops with front bed needles given first.

        Returns:
            list[Needle]: List of all needles holding loops with front bed needles given first.
        """
        return [*self.active_front_needles, *self.active_back_needles]
