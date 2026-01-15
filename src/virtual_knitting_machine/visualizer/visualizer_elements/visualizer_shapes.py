"""Module containing the Visualizer_Shape class and common shapes used in the diagrams."""

from __future__ import annotations

import math
from typing import Any

from svgwrite.shapes import Circle, Polygon, Rect

from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Visualizer_Element


class Visualizer_Shape(Visualizer_Element):

    def __init__(
        self,
        x: int,
        y: int,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ):
        """
        Args:
            x (int): The x coordinate of the shape.
            y (int): The y coordinate of the shape.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        super().__init__(x, y, name, **shape_kwargs)
        self.stroke_width: int = stroke_width
        if isinstance(fill, float):
            if isinstance(stroke, float):
                fill = "none"
                stroke = "black"
            else:
                fill = self.fill_from_stroke(stroke, fill)
        elif isinstance(stroke, float):
            stroke = self.stroke_from_fill(fill, stroke)
        self.fill: str = fill
        self.stroke: str = stroke
        self.stroke: str = stroke
        self._element_kwargs["fill"] = self.fill
        self._element_kwargs["stroke"] = self.stroke
        self._element_kwargs["stroke_width"] = self.stroke_width


class Triangle_Element(Visualizer_Shape):
    """
    Wrapper class for equilateral Triangle SVG elements.
    The triangle points downward and is positioned around a center point.

    Attributes:
        side_length (int): The length of each side of the equilateral triangle.
    """

    def __init__(
        self,
        side_length: int,
        x: int,
        y: int,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ):
        """
        Initialize the Triangle SVG element.

        Args:
            side_length (int): The length of the side of the equilateral triangle.
            x (int): The x coordinate of the bottom vertex of the triangle.
            y (int): The y coordinate of the top vertex of the triangle.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        super().__init__(x, y, name, stroke_width, fill, stroke, **shape_kwargs)
        self.side_length: int = side_length

    @property
    def height(self) -> float:
        """
        Returns:
            float: The height of the equilateral triangle.
        """
        return self.side_length * math.sqrt(3) / 2

    @property
    def top_left_vertex(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The top left vertex of the equilateral triangle pointing downward.
        """
        return self.global_x - (self.side_length / 2), self.global_y - self.height

    @property
    def top_right_vertex(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The top right vertex of the equilateral triangle pointing downward.
        """
        return self.global_x + (self.side_length / 2), self.global_y - self.height

    @property
    def bottom_vertex(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]: The bottom vertex of the equilateral triangle pointing downward.
        """
        return self.global_x, self.global_y

    def _build_svg_element(self) -> Polygon:
        return Polygon(
            points=[self.top_left_vertex, self.bottom_vertex, self.top_right_vertex],
            id=self.name,
            **self._element_kwargs,
        )


class Rect_Element(Visualizer_Shape):
    """
    Wrapper class for Rectangle SVG elements.

    Attributes:
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.
    """

    def __init__(
        self,
        width: int,
        height: int,
        x: int,
        y: int,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ) -> None:
        """
        Initialize the Rectangle SVG element.

        Args:
            width (int): The width of the rectangle in pixels.
            height (int): The height of the rectangle in pixels.
            x (int): The x coordinate of the rectangle's top left corner.
            y (int): The y coordinate of the rectangle's top left corner.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        super().__init__(x, y, name, stroke_width, fill, stroke, **shape_kwargs)
        self.width: int = width
        self.height: int = height

    def _build_svg_element(self) -> Rect:
        return Rect(
            insert=(self.global_x, self.global_y), id=self.name, size=(self.width, self.height), **self._element_kwargs
        )


class Circle_Element(Visualizer_Shape):
    """
    Wrapper class for Circle SVG elements.

    Attributes:
        radius (int): The radius of the circle.
    """

    def __init__(
        self,
        radius: int,
        x: int,
        y: int,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ):
        """
        Initialize the Circle SVG element.

        Args:
            radius (int): The radius of the circle in pixels.
            x (int): The x coordinate of the rectangle's top left corner.
            y (int): The y coordinate of the rectangle's top left corner.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        super().__init__(x, y, name, stroke_width, fill, stroke, **shape_kwargs)
        self.radius: int = radius

    def _build_svg_element(self) -> Circle:
        return Circle(center=(self.global_x, self.global_y), id=self.name, r=self.radius, **self._element_kwargs)
