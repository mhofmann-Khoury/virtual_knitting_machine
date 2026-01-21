"""Module containing the Diagram_Settings class."""

from dataclasses import dataclass
from enum import Enum

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier


@dataclass(frozen=True)
class Diagram_Settings:
    """A data class containing the settings for a virtual knitting machine visualization."""

    # Fixed sizes
    Needle_Height: int = 20  # A constant value for the height of needle squares in the visualization.
    Needle_Width: int = 20  # A constant value for the Width of needle squares in the visualization.
    Carriage_Height: int = 30  # The height of the carriage element.
    Carriage_Width: int = 50  # The width of the carriage element.
    Label_Height: int = 15  # The height of text in a label.
    Side_Label_Width: int = 10  # The width of space reserved for the Needle bed side labels.
    Label_Char_Width: int = 10  # The width allocated to each char in a label.

    # Size Proportions
    Loop_Portion_Of_Needle: float = 0.6  # The proportion of the needle boxes taken up by a loop.
    Max_Loop_Portion_Of_Needle: float = (
        0.6  # The maximum portion of a needle that a loop stack can take up. This allows for some padding around the loops for clear visibility.
    )
    Loop_Stack_Overlap: float = 0.6  # The proportion of a loop circle covered by the loop on top of it in the stack.
    Minimum_Loop_Portion_of_Needle: float = (
        0.3  # The minimum proportion of a needle that a loop can take up when shrunk to fit a stack.
    )

    # Fill Colors
    Slider_Background_Color: str = "lightgrey"  # The background color of slider needles.
    Carriage_Color: str = "grey"  # The color of the carriage element
    Yarn_Fill_Lightening_Factor: float = 0.3  # The amount to lighten yarn colors for fill of loops and carrier shapes.

    # Stroke Colors
    Needle_Stroke_Color: str = "black"  # The color of the lines surrounding needle squares.

    # Stroke Widths
    Needle_Stroke_Width: int = 1  # The width of lines surrounding needle squares.
    Loop_Stroke_Width: int = 1  # The width of the circle-strokes for loops.
    Carrier_Stroke_Width: int = 1  # The width of triangle carrier outline.

    Left_Needle_Buffer: int = 0  # The number of empty slots to show on the left side of the diagram.
    Right_Needle_Buffer: int = 0  # The number of empty slots to show on the right side of the diagram.
    Label_Padding: int = 5  # The padding between labels and needle squares.

    # Rendering Options
    render_front_labels: bool = True  # If True, renders the indices of each needle on the front bed.
    render_back_labels: bool = True  # If True, renders the indices of each needle on the back bed.
    render_left_labels: bool = True  # If True, renders the labels to the left of the needle bed.
    render_right_labels: bool = True  # If True, render labels to the right of the needle bed.
    render_empty_sliders: bool = False  # If True, render sliders regardless whether there are active slider loops.
    render_carriers: bool = True  # If True, render the active carrier positions.
    render_carriage: bool = True  # If True, render the carriage.

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
    def loop_diameter(self) -> float:
        """
        Returns:
            float: The diameter of a solo-loop on a needle box.
        """
        return self.minimum_needle_size * self.Loop_Portion_Of_Needle

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
            float: The distance from the top edge of the needle to the top of the top loop in a stack of loops that takes up the maximum spacing of loop stacks in the needle box.
        """
        return (self.Needle_Height * (1.0 - self.Max_Loop_Portion_Of_Needle)) / 2

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
        stack_size = self.minimum_needle_size * self.Max_Loop_Portion_Of_Needle
        loops_in_stack = 1.0 + (self.loop_stack_shift_portion * (loop_count - 1))
        return max(stack_size / loops_in_stack, self.minimum_loop_diameter)

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


class Carrier_Yarn_Color_Defaults(Enum):
    """An enumeration of default yarn colors assigned to carriers"""

    c1 = "firebrick"  # str: The color of carrier 1 (brick red)
    c2 = "navy"  # str: The color of carrier 2 (dark navy blue)
    c3 = "darkgreen"  # str: The color of carrier 3 (deep green)
    c4 = "indigo"  # str: The color of carrier 4 (dark indigo)
    c5 = "darkgoldenrod"  # str: The color of carrier 5 (deep gold)
    c6 = "saddlebrown"  # str: The color of carrier 6 (saddle brown)
    c7 = "darkcyan"  # str: The color of carrier 7 (deep cyan)
    c8 = "purple"  # str: The color of carrier 8 (deep purple)
    c9 = "darkorange"  # str: The color of carrier 9 (dark orange)
    c10 = "darkslateblue"  # str: The color of carrier 10 (dark slate blue)

    @staticmethod
    def get_color_by_carrier_number(carrier_id: int | Yarn_Carrier) -> str:
        """
        Args:
            carrier_id (int | Yarn_Carrier): The carrier id or yarn-carrier to source a color for.

        Returns:
            str: The color name that is default for the given carrier.

        Raises:
            KeyError: If there is no default color for the given carrier.
        """
        c_name = f"c{carrier_id}" if isinstance(carrier_id, int) else str(carrier_id)
        return Carrier_Yarn_Color_Defaults[c_name].value
