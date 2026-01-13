"""Module containing the Diagram_Settings class."""

from dataclasses import dataclass


@dataclass
class Diagram_Settings:
    """A data class containing the settings for a virtual knitting machine visualization."""

    Drawing_Width: int = 400  # The width of the diagram in pixels.
    Drawing_Height: int = 400  # The heigth of the diagram in pixels.
    Needle_Height: int = 20  # A constant value for the height of needle squares in the visualization.
    Needle_Width: int = 20  # A constant value for the Width of needle squares in the visualization.
    Slider_Background_Color: str = "lightgrey"  # The background color of slider needles.
    Needle_Stroke_Color: str = "black"  # The color of the lines surrounding needle squares.
    Needle_Stroke_Width: int = 1  # The width of lines surrounding needle squares.
    Left_Needle_Buffer: int = 1  # The number of empty slots to show on the left side of the diagram.
    Right_Needle_Buffer: int = 1  # The number of empty slots to show on the right side of the diagram.
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
