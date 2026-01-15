"""Module containing the Diagram_Settings class."""

from dataclasses import dataclass
from enum import Enum

from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier


@dataclass(frozen=True)
class Diagram_Settings:
    """A data class containing the settings for a virtual knitting machine visualization."""

    Drawing_Width: int = 400  # The width of the diagram in pixels.
    Drawing_Height: int = 400  # The height of the diagram in pixels.
    Needle_Height: int = 20  # A constant value for the height of needle squares in the visualization.
    Needle_Width: int = 20  # A constant value for the Width of needle squares in the visualization.
    Loop_Buffer: int = 6  # The padding from the edge of loop circles to the edge of the needle box.
    Slider_Background_Color: str = "lightgrey"  # The background color of slider needles.
    Needle_Stroke_Color: str = "black"  # The color of the lines surrounding needle squares.
    Needle_Stroke_Width: int = 1  # The width of lines surrounding needle squares.
    Loop_Stroke_Width: int = 1  # The width of the circle-strokes for loops.
    Carrier_Stroke_Width: int = 1  # The width of triangle carrier outline.
    Left_Needle_Buffer: int = 0  # The number of empty slots to show on the left side of the diagram.
    Right_Needle_Buffer: int = 0  # The number of empty slots to show on the right side of the diagram.
    Label_Padding: int = 5  # The padding between labels and needle squares.
    render_front_labels: bool = True  # If True, renders the indices of each needle on the front bed.
    render_back_labels: bool = True  # If True, renders the indices of each needle on the back bed.
    render_left_labels: bool = True  # If True, renders the labels to the left of the needle bed.
    render_right_labels: bool = True  # If True, render labels to the right of the needle bed.
    render_empty_sliders: bool = False  # If True, render sliders regardless whether there are active slider loops.
    render_carriers: bool = True  # If True, render the active carrier positions.
    Yarn_Fill_Lightening_Factor: float = 0.3  # The amount to lighten yarn colors for fill of loops and carrier shapes.

    @property
    def loop_radius(self) -> int:
        """
        Returns:
            int: The radius of loop circles based on the padding from the needle box walls.
        """
        return int((min(self.Needle_Height, self.Needle_Width) - self.Loop_Buffer) / 2)

    @property
    def carrier_size(self) -> int:
        """
        Returns:
            int: The side length of carrier triangles. Set to 1/3 of the needle width.
        """
        return self.Needle_Width // 3

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

        Notes:
            The labels are shifted down to provide space for the
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

    def x_of_needle(self, needle_index: int) -> int:
        """
        Args:
            needle_index (int): The index of the needle to render. Note that this may differ from the slot number if the needle bed does not render from slot 0.

        Returns:
            int: The x coordinate position of the left side of the needle slot in the diagram.
        """
        return (needle_index * self.Needle_Width) + (self.Needle_Width if self.render_left_labels else 0)


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
