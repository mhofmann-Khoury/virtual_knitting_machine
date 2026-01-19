"""Module containing the Needle_Group class"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Rect_Element

if TYPE_CHECKING:
    from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_bed_element import (
        Needle_Bed_Element,
    )


class Needle_Box(Rect_Element):

    def __init__(self, needle: Needle, bed_element: Needle_Bed_Element, **shape_kwargs: Any):
        self.needle: Needle = needle
        self.bed: Needle_Bed_Element = bed_element
        super().__init__(
            width=self.settings.Needle_Width,
            height=self.settings.Needle_Height,
            x=self._x_from_settings,
            y=0,
            name=f"{self.needle}",
            stroke_width=self.settings.Needle_Stroke_Width,
            stroke="black",
            fill=self.settings.Slider_Background_Color if self.is_slider else "none",
            **shape_kwargs,
        )

    @property
    def _x_from_settings(self) -> int:
        """
        Returns:
            int: The x position of the needle based on the needle type and the slot.
        """
        return self.settings.x_of_needle(self.bed.index_of_needle(self.needle))

    @property
    def _y_from_settings(self) -> int:
        """
        Returns:
            int: The y position of this needle based on the needle type and the slot.
        """
        if self.is_front:
            return (
                self.settings.front_slider_y
                if self.is_slider
                else self.settings.front_needle_y(self.bed.render_sliders)
            )
        else:
            return self.settings.back_slider_y if self.is_slider else self.settings.back_needle_y

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

    def slot_number(self, rack: int) -> int:
        """
        Args:
            rack (int): The racking alignment to access the slot number form.
        Returns:
            int: The slot number (front bed alignment) of this needle.
        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.needle.slot_number(rack)

    @property
    def all_needle_rack(self) -> bool:
        """
        Returns:
            bool: True if the needle bed is set for all needle racking.
        """
        return self.bed.all_needle_rack

    @property
    def settings(self) -> Diagram_Settings:
        """
        Returns:
            Diagram_Settings: The settings of the diagram.
        """
        return self.bed.settings
