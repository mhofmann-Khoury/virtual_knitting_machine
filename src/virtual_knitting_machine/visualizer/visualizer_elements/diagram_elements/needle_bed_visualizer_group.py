"""Module containing the Needle Bed Group class."""

from typing import overload

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_bed_element import (
    Needle_Bed_Element,
)
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_box import Needle_Box
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Visualizer_Element
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group


class Needle_Bed_Group(Visualizer_Group):
    """
    Wrapper class for the groupings that form the Needle Bed diagram.

    Attributes:
        render_sliders (bool): True if the slider beds are rendered, False otherwise.
        leftmost_slot (int): The leftmost needle slot to render from.
        rightmost_slot (int): The rightmost needle slot to render to.
        settings (Diagram_Settings): The machine diagram settings.
    """

    def __init__(
        self,
        leftmost_slot: int,
        rightmost_slot: int,
        render_sliders: bool,
        diagram_settings: Diagram_Settings,
        machine_state: Knitting_Machine_State,
    ):
        """
        Constructor for the Needle Bed Group class.
        Args:
            leftmost_slot (int): The leftmost needle slot to render from.
            rightmost_slot (int): The rightmost needle slot to render to.
            render_sliders (bool): True if the slider beds are rendered, False otherwise.
            diagram_settings (Diagram_Settings): The machine diagram settings.
            machine_state (Knitting_Machine_State): The machine state being displayed.
        """
        self.machine_state: Knitting_Machine_State = machine_state
        self.render_sliders: bool = render_sliders
        self.leftmost_slot: int = leftmost_slot
        self.rightmost_slot: int = rightmost_slot
        self.settings: Diagram_Settings = diagram_settings
        super().__init__(x=0, y=0, name="NeedleBed")
        self.back_bed: Needle_Bed_Element = Needle_Bed_Element(
            is_front=False,
            is_slider=False,
            leftmost_needle=self.back_leftmost,
            rightmost_needle=self.back_rightmost,
            render_sliders=self.render_sliders,
            diagram_setting=self.settings,
            machine_state=self.machine_state,
        )
        self.add_child(self.back_bed)
        self.front_bed: Needle_Bed_Element = Needle_Bed_Element(
            is_front=True,
            is_slider=False,
            leftmost_needle=self.leftmost_slot,
            rightmost_needle=self.rightmost_slot,
            render_sliders=self.render_sliders,
            diagram_setting=self.settings,
            machine_state=self.machine_state,
        )
        self.add_child(self.front_bed)
        self.back_slider_bed: Needle_Bed_Element | None = (
            Needle_Bed_Element(
                is_front=False,
                is_slider=True,
                leftmost_needle=self.leftmost_slot,
                rightmost_needle=self.rightmost_slot,
                render_sliders=self.render_sliders,
                diagram_setting=self.settings,
                machine_state=self.machine_state,
            )
            if self.render_sliders
            else None
        )
        if self.back_slider_bed is not None:
            self.add_child(self.back_slider_bed)
        self.front_slider_bed: Needle_Bed_Element | None = (
            Needle_Bed_Element(
                is_front=True,
                is_slider=True,
                leftmost_needle=self.back_leftmost,
                rightmost_needle=self.back_rightmost,
                render_sliders=self.render_sliders,
                diagram_setting=self.settings,
                machine_state=self.machine_state,
            )
            if self.render_sliders
            else None
        )
        if self.front_slider_bed is not None:
            self.add_child(self.front_slider_bed)

    @property
    def rack(self) -> int:
        """
        Returns:
            int: Racking value of the machine state.
        """
        return self.machine_state.rack

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the machine state is set for all needle rack. False otherwise.
        """
        return self.machine_state.all_needle_rack

    @property
    def carriage_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The last direction of movement of the carriage.
        """
        return self.machine_state.carriage.last_direction

    @property
    def back_leftmost(self) -> int:
        """
        Returns:
            int: The leftmost position on the back bed.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.leftmost_slot - self.rack

    @property
    def back_rightmost(self) -> int:
        """
        Returns:
            int: The rightmost position on the back bed.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.rightmost_slot - self.rack

    @property
    def slot_count(self) -> int:
        """
        Returns:
            int: The slot count for the needle beds.
        Returns:

        """
        return self.rightmost_slot - self.leftmost_slot

    @property
    def width(self) -> float:
        """
        Returns:
            float: The width of the needle bed element including any rendered labels.
        """
        w = self.settings.Needle_Width * (self.slot_count + 1.0)
        w += abs(self.settings.all_needle_shift(self.all_needle_rack, self.carriage_direction))
        if self.settings.render_left_labels:
            w += self.settings.side_label_width(self.render_sliders)
        if self.settings.render_right_labels:
            w += self.settings.side_label_width(self.render_sliders)
        return w

    @property
    def height(self) -> float:
        """
        Returns:
            float: The height of the needle bed element including any rendered labels.
        """
        h = 2.0 * self.settings.Needle_Height
        if self.render_sliders:
            h += 2.0 * self.settings.Needle_Height
        if self.settings.render_front_labels:
            h += self.settings.label_height
        if self.settings.render_back_labels:
            h += self.settings.label_height
        return h

    def has_slot(self, slot: int) -> bool:
        """
        Args:
            slot (int): The slot index of the needle bed.

        Returns:
            bool: True if that slot exists on the needle bed. False, otherwise.
        """
        return self.leftmost_slot <= slot <= self.rightmost_slot

    def has_needle(self, needle: Needle) -> bool:
        """
        Args:
            needle (Needle): The needle to find in the bed group.

        Returns:
            bool: True if the needle is rendered. False, otherwise.
        """
        if not self.has_slot(needle.slot_number):
            return False
        if needle.is_slider:
            return self.render_sliders
        else:
            return True

    def get_needle_box(self, needle: Needle) -> Needle_Box:
        """
        Args:
            needle (Needle): The needle to source in the needle bed.

        Returns:
            Needle_Box: The needle box on the needle bed.

        Raises:
            KeyError: The needle is not in the needle bed.
        """
        if not self.has_needle(needle):
            raise KeyError(f"{needle} is not rendered")
        elif needle.is_front:
            if needle.is_slider:
                assert self.front_slider_bed is not None
                return self.front_slider_bed[needle]
            else:
                return self.front_bed[needle]
        elif needle.is_slider:
            assert self.back_slider_bed is not None
            return self.back_slider_bed[needle]
        else:
            return self.back_bed[needle]

    def __contains__(self, item: int | Needle | str) -> bool:
        if isinstance(item, Needle):
            return self.has_needle(item)
        elif isinstance(item, int):
            return self.has_slot(item)
        else:
            return super().__contains__(item)

    @overload
    def __getitem__(self, item: Needle) -> Needle_Box: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: Needle | str) -> Needle_Box | Visualizer_Element:
        if isinstance(item, Needle):
            return self.get_needle_box(item)
        else:
            return super().__getitem__(item)
