"""Module containing the Carrier Triangle class"""

from typing import Any

from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_box import Needle_Box
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Triangle_Element


class Carrier_Triangle(Triangle_Element):
    """
    Wrapper for the SVG element that represents carriers as downward pointed triangles aligned above the needle bed.
    """

    def __init__(
        self,
        carrier: Yarn_Carrier_State,
        needle_box: Needle_Box | float,
        diagram_settings: Diagram_Settings,
        **shape_kwargs: Any,
    ) -> None:
        """
        Args:
            carrier (Yarn_Carrier): The carrier represented by this element.
            needle_box (Needle_Box | float): The needle box to get the x-coordinate from or an x-coordinate.
            diagram_settings (Diagram_Settings): The diagram settings used to draw the carrier.
            **shape_kwargs (Any): Keyword arguments used to draw the carrier triangle.
        """
        self._carrier: Yarn_Carrier_State = carrier
        self.settings: Diagram_Settings = diagram_settings
        super().__init__(
            side_length=self.settings.carrier_size,
            x=needle_box.global_x if isinstance(needle_box, Needle_Box) else needle_box,
            y=-1.0 * self.settings.white_space_padding,
            name=f"c{self.carrier_id}",
            stroke_width=self.settings.Carrier_Stroke_Width,
            fill=self.settings.Yarn_Fill_Lightening_Factor,
            stroke=self.carrier.yarn.properties.color,
            **shape_kwargs,
        )

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: The id of the carrier that this represents.
        """
        return self._carrier.carrier_id

    @property
    def carrier(self) -> Yarn_Carrier_State:
        """
        Returns:
            Yarn_Carrier_State: The carrier represented by this element.
        """
        return self._carrier
