"""
Module containing the Yarn Inserting Hook Block class.
"""

from typing import Any

from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Rect_Element


class Yarn_Inserting_Hook_Block(Rect_Element):
    """A black box aligned with the middle of the needle beds used to show the range of needles blocked by the yarn-inserting hook."""

    def __init__(
        self,
        rendered_sliders: bool,
        hook_index: int,
        needle_count_on_bed: int,
        diagram_settings: Diagram_Settings,
        **shape_kwargs: Any,
    ):
        """
        Args:
            rendered_sliders (bool): True if the diagram has rendered slider beds to orient the block around.
            hook_index (int): The index of the yarn-inserting hook.
            needle_count_on_bed (int): The number of needles rendered on the needle bed.
            diagram_settings (Diagram_Settings): The diagram settings object used to render the diagram.
            **shape_kwargs (Any): Additional keyword arguments used to render the block.
        """
        self.settings: Diagram_Settings = diagram_settings
        y = self.settings.front_slider_y if rendered_sliders else self.settings.front_needle_y(with_sliders=False)
        y -= self.settings.Needle_Height // 2
        needle_width = needle_count_on_bed - hook_index
        width = self.settings.Needle_Width * needle_width
        super().__init__(
            width=width,
            height=self.settings.Needle_Height,
            x=self.settings.x_of_needle(hook_index),
            y=y,
            name="Yarn_Inserting_Hook",
            stroke_width=self.settings.Needle_Stroke_Width,
            fill="black",
            stroke="black",
            **shape_kwargs,
        )
