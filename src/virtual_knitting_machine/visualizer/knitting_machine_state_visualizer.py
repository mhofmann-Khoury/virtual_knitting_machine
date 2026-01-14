"""
Contains the Knitting Visualizer class.
"""

from svgwrite import Drawing

from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.machine_state_protocol import Knitting_Machine_State_Protocol
from virtual_knitting_machine.visualizer.visualizer_elements.needle_bed_visualizer_group import Needle_Bed_Group


def format_svg(svg_file: str) -> None:
    """
    Processes a given svg file and adds whitespace to make it human-readable.
    White space includes new lines for every tag and tabs to show which tags are within other tags.
    Args:
        svg_file (str): The name of the svg file to reformat
    """
    import xml.dom.minidom as minidom

    # Read the SVG file
    with open(svg_file) as f:
        svg_content = f.read()

    # Parse and pretty-print
    dom = minidom.parseString(svg_content)
    pretty_svg = dom.toprettyxml(indent="  ")

    # Remove the XML declaration line if you don't want it
    # pretty_svg = '\n'.join(pretty_svg.split('\n')[1:])

    # Write back to file
    with open(svg_file, "w") as f:
        f.write(pretty_svg)


class Knitting_Machine_State_Visualizer:
    """
    Renders a given knitting machine state in an SVG format similar to diagrams used ACT Lab publications.
    """

    def __init__(
        self,
        machine_state: Knitting_Machine_State_Protocol,
        diagram_settings: Diagram_Settings | None = None,
    ) -> None:
        """

        Args:
            machine_state (Knitting_Machine_State_Protocol): The machine state to render. Should be a Knitting_Machine or a snapshot.
            diagram_settings (Diagram_Settings): The diagram settings for this rendering.
        """
        self.machine_state: Knitting_Machine_State_Protocol = machine_state
        if diagram_settings is None:
            diagram_settings = Diagram_Settings()
        self.settings: Diagram_Settings = diagram_settings
        ls, rs = self._get_bed_slots()
        show_sliders = self.settings.render_empty_sliders or not self.machine_state.sliders_are_clear
        self.needle_bed_group: Needle_Bed_Group = Needle_Bed_Group(
            ls, rs, self.machine_state.rack, self.machine_state.all_needle_rack, show_sliders, self.settings
        )
        for needle in self.machine_state.all_slider_loops():
            for loop in needle.held_loops:
                self.needle_bed_group.add_loop_to_needle(needle, loop)
        for needle in self.machine_state.all_loops():
            for loop in needle.held_loops:
                self.needle_bed_group.add_loop_to_needle(needle, loop)

        for loop1, loop2 in self.machine_state.active_floats():
            self.needle_bed_group.add_float_line(loop1, loop2)

        self.drawing: Drawing = Drawing(
            size=(f"{self.settings.Drawing_Width}px", f"{self.settings.Drawing_Height}px"),
            viewBox=f"0 0 {self.settings.Drawing_Width} {self.settings.Drawing_Height}",
        )

    def render(self) -> Drawing:
        """
        Render the complete visualization by building all layers.

        Returns:
            Drawing: The complete SVG drawing.
        """
        # Add layers to drawing in order (bottom to top)
        self.needle_bed_group.add_to_drawing(self.drawing)
        for float_line in self.needle_bed_group.floats:
            float_line.add_to_drawing(self.drawing)
        for loop_circle in self.needle_bed_group.loops.values():
            loop_circle.add_to_drawing(self.drawing)
        return self.drawing

    def save(self, filename: str) -> None:
        """
        Save the rendered visualization to an SVG file.

        Args:
            filename (str): Path to save the SVG file.
        """
        self.render()
        self.drawing.saveas(filename)
        format_svg(filename)

    def get_svg_string(self) -> str:
        """
        Get the SVG as a string (useful for displaying in notebooks or web).

        Returns:
            str: The SVG content as a string.
        """
        self.render()
        return str(self.drawing.tostring())

    def _get_bed_slots(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range from the left to right needle slots.
        """
        left_most_slot, right_most_slot = self.machine_state.slot_range
        left_most_slot -= self.settings.Left_Needle_Buffer
        right_most_slot += self.settings.Right_Needle_Buffer
        return left_most_slot, right_most_slot
