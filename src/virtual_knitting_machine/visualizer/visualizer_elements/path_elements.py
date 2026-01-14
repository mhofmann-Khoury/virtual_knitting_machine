"""A module containing SVG Path elements and subclasses for different path types."""

from __future__ import annotations

from enum import Enum
from typing import Any

from svgwrite.path import Path

from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Visualizer_Element


class Path_Type(Enum):
    """Enumeration of common allowed path types.
    The value of the enumeration is equal to the expected number of control points for the path type."""

    Line = 0
    Quadratic = 1
    Cubic = 2


class Path_Element(Visualizer_Element):
    """
    Wrapper class for Path SVG elements, particularly useful for creating curves and splines.

    Attributes:
        path_type (Path_Type): Type of path to form with this path element.

    """

    def __init__(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        name: str,
        stroke: str,
        control_points: list[tuple[int, int]] | None = None,
        path_type: Path_Type = Path_Type.Line,
        darken_stroke: bool = True,
        **path_kwargs: Any,
    ):
        """
        Initialize the Path SVG element.

        Args:
            start_x (int): The x coordinate of the path's starting point relative to its parent.
            start_y (int): The y coordinate of the path's starting point relative to its parent.
            end_x (int): The x coordinate of the path's ending point relative to its parent.
            end_y (int): The y coordinate of the path's ending point relative to its parent.
            name (str): The name of the path element used as the element id.
            stroke (str): The name of the stroke color used for this path.
            control_points (list[tuple[int, int]], optional): The control points of the path. Defaults to an empty list to form lines.
            path_type (Path_Type): The type of path element this SVG element represents. This should match the provided number of control points.
            darken_stroke (bool, optional): If True, the stroke color is automatically darkened (as in a fill color for loops on a yarn). Defaults to True.
            **path_kwargs (Any): Keyword arguments to configure the Path SVG element. Usually includes "stroke_width".
        """
        super().__init__(start_x, start_y, name)
        self._end_x: int = end_x
        self._end_y: int = end_y
        self.path_type: Path_Type = path_type
        self.control_points: list[tuple[int, int]] = [] if control_points is None else control_points
        self._path_kwargs: dict[str, Any] = path_kwargs
        if darken_stroke:
            stroke = self.darken_color(stroke)
        self._path_kwargs["stroke"] = stroke

    @property
    def path_data(self) -> str:
        """
        Returns:
            str: The SVG path data string to form the path's specific curve.
        """
        if self.path_type == Path_Type.Cubic:
            return self.cubic_bezier_path_data
        elif self.path_type == Path_Type.Quadratic:
            return self.quadratic_bezier_path_data
        else:  # Default to lines because any number of control points can be ignored to from a line
            return self.line_path_data

    @property
    def start_x(self) -> int:
        """
        Returns:
            int: The x coordinate of the path's starting point relative to its parent.
        """
        return self.global_x

    @property
    def start_y(self) -> int:
        """
        Returns:
            int: The y coordinate of the path's starting point relative to its parent.
        """
        return self.global_y

    @property
    def end_x(self) -> int:
        """
        Returns:
            int: The end x coordinate of the path.
        """
        return self._end_x

    @property
    def end_y(self) -> int:
        """
        Returns:
            int: The end y coordinate of the path.
        """
        return self._end_y

    def control_x(self, cp_index: int = 1) -> int:
        """
        Args:
            cp_index (int, optional): Index of the control point. Defaults to first control point.

        Returns:
            int: The x coordinate of the specified control point.
        """
        return self.control_points[cp_index][0]

    def control_y(self, cp_index: int = 1) -> int:
        """
        Args:
            cp_index (int, optional): Index of the control point. Defaults to first control point.

        Returns:
            int: The y coordinate of the specified control point.
        """
        return self.control_points[cp_index][1]

    @property
    def line_path_data(self) -> str:
        """
        Create a straight line path.

        Visual appearance: A direct straight line from start to end point.

        Use cases:
        - Connecting loops on the same needle bed (vertical connections).
        - Drawing grid lines or reference marks.
        - Simple direct connections where curves are not needed.
        - Representing tight yarn segments with no slack.

        Returns:
            str: The Path data string used to create a straight line path.
        """
        return f"M {self.start_x},{self.start_y} L {self.end_x},{self.end_y}"

    @property
    def quadratic_bezier_path_data(self) -> str:
        """
         Create a quadratic Bézier curve with one control point.

        Visual appearance:
            A smooth parabolic curve that bends toward the control point.
            The curve is always tangent to the line from start to control and from control to end.
            Creates a single, symmetric arc.

        Use cases:
        * Simple yarn floats between adjacent needles (gentle arc)
        * Connecting parent and child loops in stitch diagrams
        * Tuck operations where yarn curves around a needle
        * Any connection requiring a single smooth bend
        * When you want a simpler, more predictable curve than cubic Bezier

        Default behavior:
            If control point not specified, places it at the midpoint between start and end, offset perpendicular to create a gentle arc.

        Returns:
            str: SVG path data string for the quadratic Bézier curve.
        """
        if len(self.control_points) == 0:
            control_x = (self.start_x + self.end_x) // 2
            # Offset perpendicular to the line for a natural arc
            control_y = (self.start_y + self.end_y) // 2 - abs(self.end_x - self.start_x) // 4
        else:
            control_x = self.control_x(1)
            control_y = self.control_y(1)
        return f"M {self.start_x},{self.start_y} Q {control_x},{control_y} {self.end_x},{self.end_y}"

    @property
    def cubic_bezier_path_data(self) -> str:
        """
        Create a cubic Bézier curve with two control points.

        Visual appearance:
            A smooth S-curve or complex curve that can change direction.
            The curve starts tangent to the line from start to control1 and ends tangent to the line from control2 to end. Can create S-shapes, loops, and complex paths.

        Use cases:
        * Long yarn floats across multiple needles (creates natural drape).
        * Yarn paths that need to avoid obstacles (can curve around other elements).
        * Connecting loops on opposite beds with graceful curves.
        * Split operations where yarn paths diverge smoothly.
        * Transfer operations showing yarn movement across beds.
        * Any complex path requiring more control than quadratic Bezier.

        This is the most flexible curve type, allowing for sophisticated yarn representations.

        Returns:
            str: SVG path data string for the cubic Bézier curve.
        """
        if len(self.control_points) != 2:
            raise ValueError("Cubic Bezier curve requires 2 control points.")
        return f"M {self.start_x},{self.start_y} C {self.control_x(1)},{self.control_y(1)} {self.control_x(2)},{self.control_y(2)} {self.end_x},{self.end_y}"

    def _build_svg_element(self) -> Path:
        return Path(d=self.path_data, id=self.name, **self._path_kwargs)
