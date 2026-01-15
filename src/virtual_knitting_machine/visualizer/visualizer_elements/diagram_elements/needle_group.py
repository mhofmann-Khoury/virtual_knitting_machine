"""Module containing the Needle_Group class"""

from __future__ import annotations

from typing import TYPE_CHECKING

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Rect_Element

if TYPE_CHECKING:
    from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_slot import Needle_Slot


class Needle_Group(Visualizer_Group):

    def __init__(self, needle: Needle, slot: Needle_Slot):
        self.needle: Needle = needle
        self.slot: Needle_Slot = slot
        if self.slot.slot_number != self.slot_number:
            raise ValueError(f"{needle} does not belong to slot {slot}")
        super().__init__(self._x_from_settings(), self._y_from_settings(), name=str(needle))
        fill = self.settings.Slider_Background_Color if self.is_slider else "none"
        self._needle_box: Rect_Element = Rect_Element(
            width=self.settings.Needle_Width,
            height=self.settings.Needle_Height,
            x=0,
            y=0,
            name=f"{self.name}_box",
            stroke_width=self.settings.Needle_Stroke_Width,
            fill=fill,
            stroke=self.settings.Needle_Stroke_Color,
        )
        self.add_child(self._needle_box)

    def _x_from_settings(self) -> int:
        """
        Returns:
            int: The x position of the needle based on the needle type and the slot.
        """
        return 0 if self.is_back or not self.all_needle_rack else int(self.settings.Needle_Width / 2)

    def _y_from_settings(self) -> int:
        """
        Returns:
            int: The y position of this needle based on the needle type and the slot.
        """
        if self.is_front:
            return (
                self.settings.front_slider_y
                if self.is_slider
                else self.settings.front_needle_y(self.slot.render_sliders)
            )
        else:
            return self.settings.back_slider_y if self.is_slider else self.settings.back_needle_y

    @property
    def needle_box(self) -> Rect_Element:
        """
        Returns:
            Rect_Element: The rectangle element that represents this needle.
        """
        return self._needle_box

    @property
    def is_front(self) -> bool:
        """
        Returns:
            bool: True if this represents a front bed needle. False otherwise.
        """
        return self.needle.is_front

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if this represents a back bed needle. False otherwise.
        """
        return self.needle.is_back

    @property
    def is_slider(self) -> bool:
        """
        Returns:
            bool: True if this represents a slider bed needle. False otherwise.
        """
        return self.needle.is_slider

    @property
    def position(self) -> int:
        """
        Returns:
            int: The index of this needle in its bed.
        """
        return self.needle.position

    @property
    def slot_number(self) -> int:
        """
        Returns:
            int: The slot number (front bed alignment) of this needle.
        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.position + (0 if self.is_front else self.rack)

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the needle bed is set for all needle racking.
        """
        return self.slot.all_needle_rack

    @property
    def rack(self) -> int:
        """
        Returns:
            int: The racking alignment of the needle bed.
        """
        return self.slot.rack

    @property
    def settings(self) -> Diagram_Settings:
        """
        Returns:
            Diagram_Settings: The settings of the diagram.
        """
        return self.slot.settings
