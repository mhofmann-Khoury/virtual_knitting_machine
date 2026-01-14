"""Module containing the Loop_Circle class"""

from typing import Any

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Circle_Element


class Loop_Circle(Circle_Element):
    """
    Wrapper for SVG element that represents a loop placed on a needle in the diagram.
    """

    def __init__(
        self,
        x: int,
        y: int,
        loop: Machine_Knit_Loop,
        diagram_settings: Diagram_Settings,
        fill: str | float = 0.3,
        stroke: str | float | None = None,
        **shape_kwargs: Any,
    ):
        """
        Args:
            x (int): The x coordinate of the center of this loop relative to the needle it is placed on.
            y (int): The y coordinate of the center of this loop relative to the needle it is placed on.
            loop (Machine_Knit_Loop): The loop being rendered.
            diagram_settings  (Diagram_Settings): The settings for the diagram being rendered.
            fill (str | float, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to lightening the stroke color by a factor of 0.3
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to the color of the yarn.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        self.settings: Diagram_Settings = diagram_settings
        self._loop: Machine_Knit_Loop = loop
        if stroke is None:
            stroke = self._loop.yarn.properties.color
        super().__init__(
            self.settings.loop_radius,
            x,
            y,
            self.loop_unique_id,
            stroke_width=self.settings.Loop_Stroke_Width,
            fill=fill,
            stroke=stroke,
            **shape_kwargs,
        )

    @property
    def loop_unique_id(self) -> str:
        """
        Returns:
            str: The unique string identifier of the loop based on its id, the carrier that formed it, and the needle it is formed on.
        """
        return f"{self.loop.loop_id}_on_c{self.loop.yarn.carrier.carrier_id}_on_{self.loop.holding_needle}"

    @property
    def loop(self) -> Machine_Knit_Loop:
        """
        Returns:
            Machine_Knit_Loop: The loop that this represents.
        """
        return self._loop
