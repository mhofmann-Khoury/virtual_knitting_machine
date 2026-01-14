"""Module containing the Diagram_Settings class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Diagram_Settings:
    """A data class containing the settings for a virtual knitting machine visualization."""

    Drawing_Width: int = 400  # The width of the diagram in pixels.
    Drawing_Height: int = 400  # The height of the diagram in pixels.
    Needle_Height: int = 20  # A constant value for the height of needle squares in the visualization.
    Needle_Width: int = 20  # A constant value for the Width of needle squares in the visualization.
    Loop_Buffer: int = (
        6  # A constant value for the padding from the edge of loop circles to the edge of the needle box.
    )
    Loop_Stack_X_Shift: int = 1  # The number of pixels that stack loops are shifted rightward.
    Loop_Stack_Y_Shift: int = 1  # The number of pixels that stack loops are shifted downward.
    Max_Loop_Stack: int = 3  # The maximum number of loops that will be rendered in a stack.
    Slider_Background_Color: str = "lightgrey"  # The background color of slider needles.
    Needle_Stroke_Color: str = "black"  # The color of the lines surrounding needle squares.
    Needle_Stroke_Width: int = 1  # The width of lines surrounding needle squares.
    Loop_Stroke_Width: int = 1  # The width of the circle-strokes for loops.
    Left_Needle_Buffer: int = 0  # The number of empty slots to show on the left side of the diagram.
    Right_Needle_Buffer: int = 0  # The number of empty slots to show on the right side of the diagram.
    Label_Padding: int = 5  # The padding between labels and needle squares.
    Needle_Bed_Left_Buffer: int = 0  # The amount of white space reserved on the left side of the needle bed.
    Needle_Bed_Top_Buffer: int = 0  # The amount of white space reserved above the needle bed.
    render_front_labels: bool = True  # If True, renders the indices of each needle on the front bed.
    render_back_labels: bool = True  # If True, renders the indices of each needle on the back bed.
    render_left_labels: bool = (
        True  # If True, renders the labels for the needle bed rows on the left side of the diagram.
    )
    render_right_labels: bool = (
        True  # If True, renders the labels for the needle bed rows on the right side fo the diagram.
    )
    render_empty_sliders: bool = (
        False  # If True, diagrams will render sliders regardless whether there are active slider loops.
    )
    stack_loops: bool = (
        False  # If True, loops will be rendered as a stack on the needle. Otherwise, only the top active loop will be rendered.
    )

    @property
    def loop_radius(self) -> int:
        """
        Returns:
            int: The radius of loop circles based on the padding from the needle box walls.
        """
        return int((min(self.Needle_Height, self.Needle_Width) - self.Loop_Buffer) / 2)

    @property
    def back_needle_y(self) -> int:
        """
        Returns:
            int: The y position of back-needles in the diagram.
        """
        return self.Needle_Height + self.Label_Padding if self.render_back_labels else 0

    @property
    def back_label_y(self) -> int:
        """
        Returns:
            int: The Y position of back-bed labels in the diagram.
        """
        return self.Needle_Height

    @property
    def back_slider_y(self) -> int:
        """
        Returns:
            int: The Y position of back-bed sliders in the diagram.
        """
        return self.back_needle_y + self.Needle_Height

    @property
    def front_slider_y(self) -> int:
        """
        Returns:
            int: The Y position of front-bed sliders in the diagram.
        """
        return self.back_slider_y + self.Needle_Height

    def front_needle_y(self, with_sliders: bool) -> int:
        """
        Args:
            with_sliders (bool): If True, add the height of both sliders to this position. Otherwise, only include height of the back needle.

        Returns:
            int: The y position of front-needle in the diagram.
        """
        return self.Needle_Height + (self.front_slider_y if with_sliders else self.back_needle_y)

    def front_label_y(self, with_sliders: bool) -> int:
        """
        Args:
            with_sliders (bool): If True, add the height of both sliders to this position. Otherwise, only include height of the back needle.

        Returns:
            int: The y position of front-bed label in the diagram.
        """
        return self.Label_Padding + self.front_needle_y(with_sliders) + self.Needle_Height
