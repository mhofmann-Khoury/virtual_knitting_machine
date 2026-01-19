"""Module containing the Carriage Trapezoid diagram element."""

from typing import Any

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Polygon_Element


class Carriage_Element(Polygon_Element):

    def __init__(
        self,
        last_direction: Carriage_Pass_Direction,
        is_transferring: bool,
        needle_index: int,
        render_sliders: bool,
        diagram_settings: Diagram_Settings,
        **shape_kwargs: Any,
    ):
        self._transferring: bool = is_transferring
        self.last_direction: Carriage_Pass_Direction = last_direction
        self.settings: Diagram_Settings = diagram_settings
        self._needle_index: int = needle_index
        if not self.leftward:  # shift to right side of needle in rightward direction.
            self._needle_index += 1
        self._render_sliders: bool = render_sliders
        super().__init__(
            self.carriage_vertices,
            name="Carriage",
            stroke_width=self.settings.Needle_Stroke_Width,
            orientation=0,
            fill=self.settings.Carriage_Color,
            stroke="black",
            **shape_kwargs,
        )

    @property
    def leftward(self) -> bool:
        """
        Returns:
            bool: True if the carriage is moving leftward.
        """
        return self.last_direction is Carriage_Pass_Direction.Leftward

    @property
    def carriage_origin(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The origin of the carriage derived from its current position.

        Notes:
            The x origin of the carriage is derived from the needle position that the carriage sits at.
            The Y origin of the carriage is positioned below the needle bed and labels.
            When transferring, the carriage is shown as a box with ambiguous direction.
            When not transferring, the carriage is shown as an arrow with origin as the point of the direction it is moving.
        """
        x = self.settings.x_of_needle(self._needle_index)
        y = 2.0 * self.settings.Needle_Height
        if not self._transferring:
            y += self.settings.Carriage_Height / 2
        if self._render_sliders:
            y += 2.0 * self.settings.Needle_Height
        if self.settings.render_front_labels:
            y += self.settings.Needle_Height

        return x, y

    @property
    def carriage_vertices(self) -> list[tuple[float, float]]:
        """
        Returns:
            list[tuple[float, float]]: The vertices that draw the carriage in its current state.
        """
        points = [self.carriage_origin]
        if self._transferring:
            if self.leftward:
                points.extend(
                    [
                        (self.settings.Carriage_Width, 0),  # Left of origin
                        (self.settings.Carriage_Width, self.settings.Carriage_Height),  # left and down from origin
                        (0, self.settings.Carriage_Height),  # down from origin
                    ]
                )
            else:
                points.extend(
                    [
                        (-1 * self.settings.Carriage_Width, 0),  # right of origin
                        (
                            -1 * self.settings.Carriage_Width,
                            self.settings.Carriage_Height,
                        ),  # right and down from origin
                        (0, self.settings.Carriage_Height),  # down from origin
                    ]
                )
        else:
            point_width = (1 / 3) * self.settings.Carriage_Width
            box_height = self.settings.Carriage_Height / 2
            if self.leftward:
                points.extend(
                    [
                        (point_width, -1 * box_height),  # Up half the height and left 1/3 of the width
                        (self.settings.Carriage_Width, -1 * box_height),  # left and up half the height
                        (self.settings.Carriage_Width, box_height),  # left and down half the height
                        (point_width, box_height),
                    ]
                )  # left 1/3 of the width and down half the height
            else:
                points.extend(
                    [
                        (-1 * point_width, -1 * box_height),  # right 1/3 of width and up half height
                        (-1 * self.settings.Carriage_Width, -1 * box_height),  # right and up half height
                        (-1 * self.settings.Carriage_Width, box_height),  # right and down half height
                        (-1 * point_width, box_height),  # right 1/3 of the width and up half the height
                    ]
                )
        return points
