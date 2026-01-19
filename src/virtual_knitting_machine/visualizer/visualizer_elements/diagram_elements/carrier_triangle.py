"""Module containing the Carrier Triangle class"""

from typing import Any

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Triangle_Element


class Carrier_Triangle(Triangle_Element):
    """
    Wrapper for the SVG element that represents carriers as downward pointed triangles aligned above the needle bed.
    """

    def __init__(
        self,
        carrier: Yarn_Carrier,
        needle_index: int,
        diagram_settings: Diagram_Settings,
        **shape_kwargs: Any,
    ) -> None:
        """
        Args:
            carrier (Yarn_Carrier): The carrier represented by this element.
            needle_index (int): The index of the needle this carrier sits above. Note that this may not match the slot number if the needle bed is not rendered from the 0th needle.
            diagram_settings (Diagram_Settings): The diagram settings used to draw the carrier.
            **shape_kwargs (Any): Keyword arguments used to draw the carrier triangle.
        """
        self._carrier: Yarn_Carrier = carrier
        self.settings: Diagram_Settings = diagram_settings
        if not self.left_of_needle:
            needle_index += 1
        super().__init__(
            side_length=self.settings.carrier_size,
            x=self.settings.x_of_needle(needle_index),
            y=-1 * self.settings.Label_Padding,
            name=f"c{self.carrier_id}",
            stroke_width=self.settings.Carrier_Stroke_Width,
            fill=self.settings.Yarn_Fill_Lightening_Factor,
            stroke=self.carrier.yarn.properties.color,
            **shape_kwargs,
        )

    @property
    def left_of_needle(self) -> bool:
        """
        Returns:
            bool: True if the carrier moved leftward to its position. False otherwise.
        """
        return self.carrier.last_direction is Carriage_Pass_Direction.Leftward

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: The id of the carrier that this represents.
        """
        return self._carrier.carrier_id

    @property
    def carrier(self) -> Yarn_Carrier:
        """
        Returns:
            Yarn_Carrier: The carrier represented by this element.
        """
        return self._carrier
