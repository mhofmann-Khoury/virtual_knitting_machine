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
            x=self.settings.x_of_needle(self.bed.index_of_needle(self.needle)),
            y=0,
            name=f"{self.needle}",
            stroke_width=self.settings.Needle_Stroke_Width,
            stroke="black",
            fill=self.settings.Slider_Background_Color if self.is_slider else "none",
            **shape_kwargs,
        )

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
