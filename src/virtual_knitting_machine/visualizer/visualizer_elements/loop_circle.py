"""Module containing the Loop_Circle class"""

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Circle_Element


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
        fill_color: str | None,
        line_color: str | None = None,
    ):
        """
        Args:
            x (int): The x coordinate of this loop relative to the needle it is placed on.
            y (int): The y coordinate of this loop relative to the needle it is placed on.
            loop (Machine_Knit_Loop): The loop being rendered.
            diagram_settings  (Diagram_Settings): The settings for the diagram being rendered.
            fill_color (str, optional): The name of the fill color of this circle. Defaults to the color of the yarn that formed this loop.
            line_color (str, optional): The color of the stroke around the circle. Defaults to a darkened version of the fill color.
        """
        self.settings: Diagram_Settings = diagram_settings
        self._loop: Machine_Knit_Loop = loop
        if fill_color is None:
            fill_color = self._loop.yarn.properties.color
        super().__init__(
            x,
            y,
            self.loop_unique_id,
            self.settings.loop_radius,
            auto_darken_stroke=line_color is None,
            fill=fill_color,
            stroke=line_color,
            stroke_width=self.settings.Loop_Stroke_Width,
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
