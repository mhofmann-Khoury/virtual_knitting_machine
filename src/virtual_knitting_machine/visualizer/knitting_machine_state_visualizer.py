"""
Contains the Knitting Visualizer class.
"""

from typing import cast

from svgwrite import Drawing

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier_State
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.carriage_element import Carriage_Element
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.carrier_legend import Carrier_Legend
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.carrier_triangle import Carrier_Triangle
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.float_path import (
    Float_Orientation_To_Neighbors,
    Float_Path,
)
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.loop_circle import Loop_Circle, Loop_Stack
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
        machine_state: Knitting_Machine_State,
        diagram_settings: Diagram_Settings | None = None,
    ) -> None:
        """

        Args:
            machine_state (Knitting_Machine_State): The machine state to render. Should be a Knitting_Machine or a snapshot.
            diagram_settings (Diagram_Settings): The diagram settings for this rendering.
        """
        self.machine_state: Knitting_Machine_State = machine_state
        if diagram_settings is None:
            diagram_settings = Diagram_Settings()
        self.settings: Diagram_Settings = diagram_settings
        ls, rs = self._get_bed_slots()
        self.leftmost_slot: int = ls
        self.rightmost_slot: int = rs
        self.shows_sliders: bool = self.settings.render_empty_sliders or not self.machine_state.sliders_are_clear
        self.carriers_in_legend: set[Yarn_Carrier_State] = set()
        self.needle_bed_group: Needle_Bed_Group = Needle_Bed_Group(
            self.leftmost_slot,
            self.rightmost_slot,
            self.machine_state.rack,
            self.machine_state.all_needle_rack,
            self.machine_state.carriage.last_direction,
            self.shows_sliders,
            self.settings,
        )
        self.loop_stacks: dict[Needle, Loop_Stack] = {}
        self.loops: dict[Machine_Knit_Loop, Loop_Circle] = {}
        self._add_active_loops()
        self.floats: set[Float_Path] = set()
        self._add_active_floats()
        self.carriers: set[Carrier_Triangle] = set()
        if self.settings.render_carriers:
            self._add_active_carriers()
        self.legend: Carrier_Legend | None = (
            Carrier_Legend(
                x=self.needle_bed_group.width + self.min_x,
                y=0,
                diagram_settings=self.settings,
                carriers=self.carriers_in_legend,
            )
            if self.settings.render_legend and len(self.carriers_in_legend) > 0
            else None
        )
        if self.machine_state.carrier_system.hook_position is None:
            self.yarn_inserting_hook_block: Yarn_Inserting_Hook_Block | None = None
        else:
            self.yarn_inserting_hook_block = Yarn_Inserting_Hook_Block(
                self.shows_sliders,
                self.machine_state.carrier_system.hook_position - self.leftmost_slot,
                cast(Yarn_Carrier_State, self.machine_state.carrier_system.hooked_carrier),
                self.needle_count,
                self.settings,
            )
        carriage_on_diagram = (
            self.leftmost_slot <= self.machine_state.carriage.current_needle_slot < self.rightmost_slot
        )
        self.carriage_block: Carriage_Element | None = (
            Carriage_Element(
                self.machine_state.carriage.last_direction,
                self.machine_state.carriage.transferring,
                self.machine_state.carriage.current_needle_slot - self.leftmost_slot,
                self.shows_sliders,
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

    @property
    def size(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The size of this diagram by its width and height.
        """
        width = self.needle_bed_group.width
        if self.legend is not None:
            width += self.legend.width()
        height = self.needle_bed_group.height
        if not self.settings.render_back_labels and len(self.carriers) > 0:
            height += self.settings.carriage_height + self.settings.white_space_padding
        if self.carriage_block is not None:
            height += self.settings.carriage_height
        if self.legend is not None:
            height = max(height, self.legend.height())
        return width, height

    def _get_bed_slots(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The range from the left to right needle slots.
        """
        left_most_slot, right_most_slot = self.machine_state.slot_range
        left_most_slot -= self.settings.Left_Needle_Buffer
        right_most_slot += self.settings.Right_Needle_Buffer
        return left_most_slot, right_most_slot

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
        for needle in self.machine_state.all_loops():
            self.loop_stacks[needle] = Loop_Stack(needle.held_loops, self.needle_bed_group[needle], self.settings)
        for needle in self.machine_state.all_slider_loops():
            self.loop_stacks[needle] = Loop_Stack(needle.held_loops, self.needle_bed_group[needle], self.settings)
        for loop_stack in self.loop_stacks.values():
            self.loops.update({l.loop: l for l in loop_stack.loop_circles})
            self.carriers_in_legend.update({l.loop.yarn.carrier for l in loop_stack.loop_circles})

    def _add_active_carriers(self) -> None:
        """
        Renders the carrier triangles for active carriers on the diagram.
        """
        for carrier in self.machine_state.carrier_system.active_carriers:
            between_needles = carrier.between_needles
            assert between_needles is not None
            left_needle, right_needle = between_needles[0], between_needles[1]
            if right_needle not in self.needle_bed_group:
                if left_needle not in self.needle_bed_group:
                    continue  # Carrier is not on the bed, skip it
                needle_box = self.needle_bed_group[left_needle].global_x + self.settings.Needle_Width
            else:
                needle_box = self.needle_bed_group[right_needle]
            self.carriers.add(
                Carrier_Triangle(
                    carrier=carrier,
                    needle_box=needle_box,
                    diagram_settings=self.settings,
                )
            )
            self.carriers_in_legend.add(carrier)

    def render(self) -> Drawing:
        """
        Render the complete visualization by building all layers.
        """
        drawing = self._new_diagram_drawing()
        # Add layers to drawing in order (bottom to top)
        self.needle_bed_group.add_to_drawing(drawing)
        for float_line in self.floats:
            float_line.add_to_drawing(drawing)
        for loop_stack in self.loop_stacks.values():
            loop_stack.add_to_drawing(drawing)
        for carrier_triangle in self.carriers:
            carrier_triangle.add_to_drawing(drawing)
        if self.legend is not None:
            self.legend.add_to_drawing(drawing)
        if self.yarn_inserting_hook_block is not None:
            self.yarn_inserting_hook_block.add_to_drawing(drawing)
        if self.carriage_block is not None:
            self.carriage_block.add_to_drawing(drawing)
        return drawing

    def save(self, filename: str) -> None:
        """
        Save the rendered visualization to an SVG file.

        Args:
            filename (str): Path to save the SVG file.
        """
        drawing = self.render()
        drawing.saveas(filename)
        format_svg(filename)

    @property
    def min_x(self) -> float:
        """
        Returns:
            float: The minimum x-coordinate of the viewport.
        """
        min_x = 0.0
        if (
            self.machine_state.all_needle_rack
            and self.machine_state.carriage.last_direction is Carriage_Pass_Direction.Leftward
        ):
            min_x = self.settings.all_needle_shift(
                self.machine_state.all_needle_rack, self.machine_state.carriage.last_direction
            )
        if self.settings.render_left_labels:
            min_x -= self.settings.side_label_width(self.shows_sliders)
        return min_x

    def _new_diagram_drawing(self) -> Drawing:
        """
        Returns:
            Drawing: An empty drawing sized for the diagram."""
        width, height = self.size
        min_y = 0
        if self.settings.render_back_labels:
            min_y -= self.settings.label_height
        elif len(self.carriers) > 0:
            min_y -= self.settings.carrier_size + self.settings.white_space_padding
        return Drawing(
            size=(f"{width}px", f"{height}px"),
            viewBox=f"{self.min_x} {min_y} {width} {height}",
        )
