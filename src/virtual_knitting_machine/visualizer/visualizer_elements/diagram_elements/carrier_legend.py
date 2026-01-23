"""Module containing the Carrier_Legend class"""

from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Text_Anchor, Text_Element
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group


class Carrier_Legend(Visualizer_Group):

    def __init__(self, x: float, y: float, diagram_settings: Diagram_Settings, carriers: set[Yarn_Carrier_State]):
        self.settings: Diagram_Settings = diagram_settings
        super().__init__(x, y, name="Carrier_Legend")
        sorted_carriers = sorted(carriers)  # Sort carriers by carrier id.
        self.carrier_labels: list[Text_Element] = [
            Text_Element(
                x=0,
                y=self.settings.label_height * i,
                label=f"C{c.carrier_id}",
                font_family=self.settings.font_family,
                font_size=self.settings.font_size,
                is_bold=True,
                text_anchor=Text_Anchor.start,
                font_color=c.yarn.properties.color,
            )
            for i, c in enumerate(sorted_carriers)
        ]
        for c_label in self.carrier_labels:
            self.add_child(c_label)

    def width(self) -> float:
        """
        Returns:
            float: The width of the carrier legend based on the width of the labels.
        """
        return (
            max(c_label.approximate_label_width for c_label in self.carrier_labels) + self.settings.white_space_padding
        )

    def height(self) -> float:
        """
        Returns:
            float: The total height of the carrier legend based on the height of the labels.
        """
        return len(self.carrier_labels) * self.settings.label_height
