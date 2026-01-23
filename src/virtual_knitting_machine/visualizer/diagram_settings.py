"""Module containing the Diagram_Settings class."""

from dataclasses import dataclass

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Text_Element


@dataclass(frozen=True)
class Diagram_Settings:
    """A data class containing the settings for a virtual knitting machine visualization."""

    # Fixed sizes
    Needle_Height: int = 20  # A constant value for the height of needle squares in the visualization.
    Needle_Width: int = 20  # A constant value for the Width of needle squares in the visualization.

    # Size Proportions
    Loop_Stack_Overlap: float = 0.6  # The proportion of a loop circle covered by the loop on top of it in the stack.
    White_Space_Padding_Proportional_to_Needle: float = 0.25  # The padding between labels and needle squares.
    Minimum_Loop_Portion_of_Needle: float = 0.2  # The minimum size of loops proportional to needles.
    Carriage_Height_in_Needles: float = 1.5  # The height of the carriage element relative to the height of needles.
    Carriage_Width_in_Needles: float = 2.0  # The width of the carriage element relative to the width of needles.

    # Fill Colors
    Slider_Background_Color: str = "lightgrey"  # The background color of slider needles.
    Carriage_Color: str = "grey"  # The color of the carriage element
    Yarn_Fill_Lightening_Factor: float = 0.3  # The amount to lighten yarn colors for fill of loops and carrier shapes.

    # Stroke Colors
    Needle_Stroke_Color: str = "black"  # The color of the lines surrounding needle squares.

    # Font Parameters
    font_family: str = "Arial"  # The font used throughout the diagram.
    font_size: int = 14  # The font size (height in pixels of a tall character).

    # Stroke Widths
    Needle_Stroke_Width: int = 1  # The width of lines surrounding needle squares.
    Loop_Stroke_Width: int = 1  # The width of the circle-strokes for loops.
    Carrier_Stroke_Width: int = 1  # The width of triangle carrier outline.

    # Rendering Options
    Left_Needle_Buffer: int = 0  # The number of empty slots to show on the left side of the diagram.
    Right_Needle_Buffer: int = 0  # The number of empty slots to show on the right side of the diagram.
    render_front_labels: bool = True  # If True, renders the indices of each needle on the front bed.
    render_back_labels: bool = True  # If True, renders the indices of each needle on the back bed.
    render_left_labels: bool = True  # If True, renders the labels to the left of the needle bed.
    render_right_labels: bool = True  # If True, render labels to the right of the needle bed.
    render_empty_sliders: bool = False  # If True, render sliders regardless whether there are active slider loops.
    render_carriers: bool = True  # If True, render the active carrier positions.
    render_carriage: bool = True  # If True, render the carriage.
    render_legend: bool = True  # If True, render the legend of carrier colors.

    @property
    def carriage_height(self) -> int:
        """
        Returns:
            int: The height of the carriage element.
        """
        return int(self.Needle_Height * self.Carriage_Height_in_Needles)

    @property
    def carriage_width(self) -> int:
        """
        Returns:
            int: The width of the carriage element.
        """
        return int(self.Needle_Width * self.Carriage_Width_in_Needles)

    @property
    def white_space_padding(self) -> int:
        """
        Returns:
            int: The required white space padding around elements.
        """
        return int(self.minimum_needle_size * self.White_Space_Padding_Proportional_to_Needle)

    @property
    def label_height(self) -> int:
        """
        Returns:
            int: The reserved vertical spacing for a label including whitespace padding.
        """
        return self.font_size + self.white_space_padding

    def side_label_width(self, has_sliders: bool) -> float:
        """
        Args:
            has_sliders (bool): True if the sliders were rendered.

        Returns:
            float: The approximate width of the needle bed side labels based on the font size.
        """
        if self.render_empty_sliders or has_sliders:
            return Text_Element.approximate_text_width(2, self.font_size) + 2 * self.white_space_padding
        else:
            return Text_Element.approximate_text_width(1, self.font_size) + 2 * self.white_space_padding

    def all_needle_shift(self, is_all_needle_rack: bool, carriage_direction: Carriage_Pass_Direction) -> int:
        """
        Args:
            is_all_needle_rack (bool): If True, the back beds are shifted to align with the carriage direction.
            carriage_direction (Carriage_Pass_Direction): Direction of the carriage.

        Returns:
            int: The amount to shift back bed x coordinates for a given all needle shift

        Notes:
            If not all needle racking, this is the same as the front-bed's x-coordinate.
            In a leftward all needle alignment, the bed is shifted leftward.
            In a rightward all needle alignment, the bed is shifted rightward
        """
        if is_all_needle_rack:
            if carriage_direction is Carriage_Pass_Direction.Leftward:
                return -1 * (self.Needle_Width // 2)
            else:
                return self.Needle_Width // 2
        else:
            return 0

    @property
    def minimum_needle_size(self) -> int:
        """
        Returns:
            int: The smallest dimension of a needle box.
        """
        return min(self.Needle_Height, self.Needle_Width)

    @property
    def loop_diameter(self) -> int:
        """
        Returns:
            int: The diameter of a solo-loop on a needle box.
        """
        return self.minimum_needle_size - self.white_space_padding

    @property
    def minimum_loop_diameter(self) -> float:
        """
        Returns:
            float: The minimum diameter to render a loop on a needle box.
        """
        return self.minimum_needle_size * self.Minimum_Loop_Portion_of_Needle

    @property
    def loop_radius(self) -> float:
        """
        Returns:
            float: The radius of loop circles based on their proportion of a needle box.
        """
        return self.loop_diameter / 2

    @property
    def loop_stack_shift_portion(self) -> float:
        """
        Returns:
            float: The portion of a loops diameter to shift by when stacking multiple loops on a single needle box.
        """
        return 1.0 - self.Loop_Stack_Overlap

    @property
    def loop_stack_top(self) -> float:
        """
        Returns:
            float: The distance from the top edge of the needle to the top of the top loop stack.
        """
        return self.white_space_padding / 2

    def stacked_loop_diameter(self, loop_count: int) -> float:
        """
        Args:
            loop_count (int): The number of loops to stack on a needle box.

        Returns:
            float: The diameter of the stacked loops adjusted for the number overlapping loops in the stack.

        Notes:
            The diameter is based on the number of loops in a stack, however a minimum diameter is set to ensure that loops are clearly rendered.
        """
        if loop_count == 1:
            return self.loop_diameter
        loops_in_stack = 1.0 + (self.loop_stack_shift_portion * (loop_count - 1))
        return max(self.loop_diameter / loops_in_stack, self.minimum_loop_diameter)

    @property
    def carrier_size(self) -> int:
        """
        Returns:
            int: The side length of carrier triangles. Set to 1/3 of the needle width.
        """
        return self.Needle_Width // 3

    def x_of_needle(self, needle_index: int) -> int:
        """
        Args:
            needle_index (int): The index of the needle to render. Note that this may differ from the slot number if the needle bed does not render from slot 0.

        Returns:
            int: The x coordinate position of the left side of the needle slot in the diagram.
        """
        return needle_index * self.Needle_Width
