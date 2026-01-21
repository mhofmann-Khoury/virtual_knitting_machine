"""Module containing the Visualizer_Shape class and common shapes used in the diagrams."""

from __future__ import annotations

import math
from typing import Any

from svgwrite.shapes import Circle, Polygon, Rect

from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Visualizer_Element


class Visualizer_Shape(Visualizer_Element):

    def __init__(
        self,
        x: float,
        y: float,
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


class Polygon_Element(Visualizer_Shape):
    """
    A wrapper for Polygon SVG elements.
    """

    def __init__(
        self,
        points: list[tuple[float, float]],
        name: str,
        stroke_width: int,
        orientation: int | tuple[float, float] = 0,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ):
        """
        Args:
            points (list[tuple[float, float]]): The ordered coordinates of the vertices of the polygon element.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            orientation (int | tuple[int, int], optional):
                If given a tuple, the vertices will be oriented from the given coordinate x, y point (e.g., a center point).
                If given an integer, the vertices will be oriented from the vertex at that index.
                Defaults to orienting around the first point in the points list.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        self._points: list[tuple[float, float]] = points
        if isinstance(orientation, tuple):
            x, y = orientation
            exclude_index = -1
        else:
            x, y = self[orientation][0], self[orientation][1]
            exclude_index = orientation
        super().__init__(x, y, name, stroke_width, fill, stroke, **shape_kwargs)
        self._orient_from_origin(exclude_index)

    def _orient_from_origin(self, exclude_index: int = -1) -> None:
        """Adjusts the polygon vertices to be relative to x, y origin of this polygon.

        Args:
            exclude_index (int, optional): If an index is provided, that point is assumed to be the origin of the polygon element and should not be modified. Defaults to modifying all vertices.
        """
        self._points = [
            (v[0] + self.x, v[1] + self.y) if i != exclude_index else (v[0], v[1]) for i, v in enumerate(self._points)
        ]

    @property
    def x_coordinates(self) -> list[float]:
        """
        Returns:
            list[float]: The x coordinate values for each vertex in the polygon.
        """
        return [x for x, _y in self._points]

    @property
    def y_coordinates(self) -> list[float]:
        """
        Returns:
            list[float]: The y coordinate values for each vertex in the polygon.
        """
        return [y for _x, y in self._points]

    @property
    def global_points(self) -> list[tuple[float, float]]:
        """
        Returns:
            list[tuple[float, float]]: The global coordinates of the polygon vertices.
        """
        if self.parent is not None:
            return [(x + self.global_x, y + self.global_y) for x, y in self._points]
        else:
            return self._points

    def _build_svg_element(self) -> Polygon:
        return Polygon(
            points=self.global_points,
            id=self.name,
            **self._element_kwargs,
        )

    def __getitem__(self, item: int) -> tuple[float, float]:
        """
        Args:
            item (int): The index of the polygon vertice to return.

        Returns:
            tuple[float, float]: The coordinate of the indexed vertice.

        Raises:
            KeyError: If the index is out of bounds.
        """
        return self._points[item]

    def __len__(self) -> int:
        """
        Returns:
            int: The number of vertices in the polygon.
        """
        return len(self._points)


class Triangle_Element(Polygon_Element):
    """
    Wrapper class for equilateral Triangle SVG elements.
    The triangle points downward and is oriented to its bottom index.

    Attributes:
        side_length (int): The length of each side of the equilateral triangle.
    """

    def __init__(
        self,
        side_length: float,
        x: float,
        y: float,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ):
        """
        Initialize the Triangle SVG element.

        Args:
            side_length (float): The length of the side of the equilateral triangle.
            x (float): The x coordinate of the bottom vertex of the triangle.
            y (float): The y coordinate of the top vertex of the triangle.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        self.side_length: float = side_length
        super().__init__(
            points=[(x, y), self.top_left_vertex, self.top_right_vertex],
            orientation=0,
            name=name,
            stroke_width=stroke_width,
            fill=fill,
            stroke=stroke,
            **shape_kwargs,
        )

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
        return -1 * (self.side_length / 2), -1 * self.height

    @property
    def top_right_vertex(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The top right vertex of the equilateral triangle pointing downward.
        """
        return self.side_length / 2, -1 * self.height

    @property
    def bottom_vertex(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: The bottom vertex of the equilateral triangle pointing downward.
        """
        return self.x, self.y


class Rect_Element(Visualizer_Shape):
    """
    Wrapper class for Rectangle SVG elements.

    Attributes:
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.
    """

    def __init__(
        self,
        width: float,
        height: float,
        x: float,
        y: float,
        name: str,
        stroke_width: int,
        fill: str | float = "none",
        stroke: str | float = 0.7,
        **shape_kwargs: Any,
    ) -> None:
        """
        Initialize the Rectangle SVG element.

        Args:
            width (float): The width of the rectangle in pixels.
            height (float): The height of the rectangle in pixels.
            x (float): The x coordinate of the rectangle's top left corner.
            y (float): The y coordinate of the rectangle's top left corner.
            name (str): The name-id of the shape.
            stroke_width (int): The width of the outline of the shape.
            fill (str | int, optional): The fill color of the shape or the factor to lighten the stroke color by. Defaults to no fill color.
            stroke (str | float, optional): The color of the outline of the shape or the factor to darken the fill color by. Defaults to darkening the fill color by a factor of 0.7.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.
        """
        super().__init__(x, y, name, stroke_width, fill, stroke, **shape_kwargs)
        self.width: float = width
        self.height: float = height

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
        radius: float,
        x: float,
        y: float,
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
        self.radius: float = radius

    @property
    def diameter(self) -> float:
        """
        Returns:
            float: The diameter of the circle.
        """
        return self.radius * 2.0

    def _build_svg_element(self) -> Circle:
        return Circle(center=(self.global_x, self.global_y), id=self.name, r=self.radius, **self._element_kwargs)
