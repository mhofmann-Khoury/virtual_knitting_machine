"""
Contains the Knitting Visualizer class.
"""

from svgwrite import Drawing

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.machine_state_protocol import Knitting_Machine_State_Protocol
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.carriage_element import Carriage_Element
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.carrier_triangle import Carrier_Triangle
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.float_path import (
    Float_Orientation_To_Neighbors,
    Float_Path,
)
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.loop_circle import Loop_Circle
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_bed_visualizer_group import (
    Needle_Bed_Group,
)
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.yarn_inserting_hook_block import (
    Yarn_Inserting_Hook_Block,
)


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
        self.leftmost_slot: int = ls
        self.rightmost_slot: int = rs
        show_sliders = self.settings.render_empty_sliders or not self.machine_state.sliders_are_clear
        self.needle_bed_group: Needle_Bed_Group = Needle_Bed_Group(
            self.leftmost_slot,
            self.rightmost_slot,
            self.machine_state.rack,
            self.machine_state.all_needle_rack,
            show_sliders,
            self.settings,
        )
        self.loops: dict[Machine_Knit_Loop, Loop_Circle] = {}
        self._add_active_loops()
        self.floats: set[Float_Path] = set()
        self._add_active_floats()
        self.carriers: set[Carrier_Triangle] = set()
        if self.settings.render_carriers:
            self._add_active_carriers()
        self.yarn_inserting_hook_block: Yarn_Inserting_Hook_Block | None = (
            Yarn_Inserting_Hook_Block(
                show_sliders, self.machine_state.hook_position - self.leftmost_slot, self.needle_count, self.settings
            )
            if self.machine_state.hook_position is not None
            else None
        )
        carriage_on_diagram = self.leftmost_slot <= self.machine_state.current_needle_slot < self.rightmost_slot
        self.carriage_block: Carriage_Element | None = (
            Carriage_Element(
                self.machine_state.last_direction,
                self.machine_state.transferring,
                self.machine_state.current_needle_slot - self.leftmost_slot,
                show_sliders,
                self.settings,
            )
            if self.settings.render_carriage and carriage_on_diagram
            else None
        )

    @property
    def needle_count(self) -> int:
        """
        Returns:
            int: The number of needle slots rendered on this diagram.
        """
        return self.rightmost_slot + 1 - self.leftmost_slot

    def _get_bed_slots(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range from the left to right needle slots.
        """
        left_most_slot, right_most_slot = self.machine_state.slot_range
        left_most_slot -= self.settings.Left_Needle_Buffer
        right_most_slot += self.settings.Right_Needle_Buffer
        return left_most_slot, right_most_slot

    def index_of_slot(self, slot: int) -> int:
        """
        Args:
            slot (int): The slot to be indexed from the left side of the diagram.

        Returns:
            int: The index of the given slot based on the leftmost slot rendered in this diagram.
        """
        return slot - self.leftmost_slot

    def _add_active_floats(self) -> None:
        """
        Renders the floats between active loops on the diagram.
        """
        for loop1, loop2 in self.machine_state.active_floats():
            loop_circle1 = self.loops[loop1]
            loop_circle2 = self.loops[loop2]
            needle_1 = loop1.holding_needle
            assert needle_1 is not None
            needle_2 = loop2.holding_needle
            assert needle_2 is not None
            loops_crossed = self.machine_state.loops_crossed_by_float(loop1, loop2)
            # filter to loops that share a bed with at least one loop in the float
            loops_crossed = {
                l
                for l in loops_crossed
                if l.holding_needle is not None and l.holding_needle.is_front in (needle_1.is_front, needle_2.is_front)
            }
            orientation = Float_Orientation_To_Neighbors.Along_Bed
            if len(loops_crossed) > 0:
                if not any(l > loop1 or l > loop2 for l in loops_crossed):  # All loops are older than float
                    orientation = Float_Orientation_To_Neighbors.Curve_Into_Bed
                elif not any(l < loop1 or l < loop2 for l in loops_crossed):  # All loops are younger than the float.
                    orientation = Float_Orientation_To_Neighbors.Curve_Away_From_Bed
            self.floats.add(
                Float_Path(
                    loop_circle1, loop_circle2, self.machine_state.rack, self.settings, same_bed_orientation=orientation
                )
            )

    def _add_active_loops(self) -> None:
        """
        Renders the loop-circles for each active loop on the diagram.
        """
        for loop in sorted(self.machine_state.active_loops):
            needle = loop.holding_needle
            assert needle is not None
            self.loops[loop] = Loop_Circle(loop, self.needle_bed_group[needle], self.settings)

    def _add_active_carriers(self) -> None:
        """
        Renders the carrier triangles for active carriers on the diagram.
        """
        for carrier in self.machine_state.active_carriers:
            assert carrier.slot_position is not None
            self.carriers.add(
                Carrier_Triangle(
                    carrier=carrier,
                    needle_index=self.index_of_slot(carrier.slot_position),
                    diagram_settings=self.settings,
                )
            )

    def render(self, drawing: Drawing) -> None:
        """
        Render the complete visualization by building all layers.

        Args:
            drawing (Drawing): The drawing to add teh diagram to.
        """
        # Add layers to drawing in order (bottom to top)
        self.needle_bed_group.add_to_drawing(drawing)
        for float_line in self.floats:
            float_line.add_to_drawing(drawing)
        for loop_circle in self.loops.values():
            loop_circle.add_to_drawing(drawing)
        for carrier_triangle in self.carriers:
            carrier_triangle.add_to_drawing(drawing)
        if self.yarn_inserting_hook_block is not None:
            self.yarn_inserting_hook_block.add_to_drawing(drawing)
        if self.carriage_block is not None:
            self.carriage_block.add_to_drawing(drawing)

    def save(self, filename: str) -> None:
        """
        Save the rendered visualization to an SVG file.

        Args:
            filename (str): Path to save the SVG file.
        """
        drawing = self._new_drawing()
        self.render(drawing)
        drawing.saveas(filename)
        format_svg(filename)

    def get_svg_string(self) -> str:
        """
        Get the SVG as a string (useful for displaying in notebooks or web).

        Returns:
            str: The SVG content as a string.
        """
        drawing = self._new_drawing()
        self.render(drawing)
        return str(drawing.tostring())

    def _new_drawing(self) -> Drawing:
        """
        Returns:
            Drawing: An empty drawing sized for the diagram."""
        return Drawing(
            size=(f"{self.settings.Drawing_Width}px", f"{self.settings.Drawing_Height}px"),
            viewBox=f"0 0 {self.settings.Drawing_Width} {self.settings.Drawing_Height}",
        )
