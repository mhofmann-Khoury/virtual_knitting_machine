"""Module containing the components of Float Paths in machine state diagrams."""

from enum import Enum
from typing import Any

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.loop_circle import Loop_Circle
from virtual_knitting_machine.visualizer.visualizer_elements.path_elements import Path_Element, Path_Type


class Float_Type(Enum):
    """Enumeration mapping the orientation of a float relative to its neighboring loops to a specific type of curve best used to represent it."""

    Direct_Neighbor = "direct line"  # Floats between adjacent needles are best shown by lines.
    Behind_Neighbors = "downward arc"  # Longer floats on the same bed that cross behind neighboring loops.
    In_Front_Of_Neighbors = "upward arc"  # Longer floats on the same bed that cross in front of neighboring loops.
    Crosses_Beds = "s-curve"  # Floats that cross over the beds diagonally.
    Simple_Line = "long line"  # A simple default pattern when complex curves cannot be inferred.

    @property
    def path_type(self) -> Path_Type:
        """
        Returns:
            Path_Type: The path type used to create the specified float curvature.
        """
        if self in [Float_Type.Direct_Neighbor, Float_Type.Simple_Line]:
            return Path_Type.Line
        else:
            return Path_Type.Cubic


class Float_Orientation_To_Neighbors(Enum):
    """Enumeration of possible orientations of a float along a single bed."""

    Curve_Into_Bed = "curve into bed"
    Curve_Away_From_Bed = "curve away from bed"
    Along_Bed = "along bed"

    def float_type_by_bed(self, is_front_bed: bool) -> Float_Type:
        """
        Args:
            is_front_bed (bool): True if both loops are on a front bed. False if they are on a back bed.

        Returns:
            Float_Type: Float type based on the orientation of the float and the given bed of its loops.

        Notes:
            This method assumes the floats are both on the same bed.
        """
        if self is Float_Orientation_To_Neighbors.Along_Bed:
            return Float_Type.Simple_Line
        elif self is Float_Orientation_To_Neighbors.Curve_Into_Bed:
            if is_front_bed:
                return Float_Type.Behind_Neighbors
            else:
                return Float_Type.In_Front_Of_Neighbors
        elif is_front_bed:
            return Float_Type.In_Front_Of_Neighbors
        else:
            return Float_Type.Behind_Neighbors


class Float_Path(Path_Element):
    """
    Forms a path between to loop circles in the diagram.

    Automatically adjusts the curvature of the path based on the relative positions of the loops and the assigned orientation to the loops already on that bed.
    """

    def __init__(
        self,
        loop_1: Loop_Circle,
        loop_2: Loop_Circle,
        rack: int,
        diagram_settings: Diagram_Settings,
        same_bed_orientation: Float_Orientation_To_Neighbors = Float_Orientation_To_Neighbors.Curve_Away_From_Bed,
        **path_kwargs: Any,
    ) -> None:
        self.loop_circle_1: Loop_Circle = loop_1
        self.loop_circle_2: Loop_Circle = loop_2
        self.rack = rack
        self.settings: Diagram_Settings = diagram_settings
        self.same_bed_orientation: Float_Orientation_To_Neighbors = same_bed_orientation
        super().__init__(
            loop_1.global_x,
            loop_1.global_y,
            loop_2.global_x,
            loop_2.global_y,
            name=self.float_unique_id,
            stroke=self.loop_1.yarn.properties.color,
            stroke_width=self.settings.Loop_Stroke_Width,
            path_type=self.path_type,
            **path_kwargs,
        )
        self._set_control_points_by_float_type()

    @property
    def same_bed(self) -> bool:
        """
        Returns:
            bool: True if both loops are on the same bed. Otherwise, False.
        """
        return self.needle_1.is_front == self.needle_2.is_front and self.needle_1.is_slider == self.needle_2.is_slider

    @property
    def same_slot(self) -> bool:
        """
        Returns:
            bool: True if both loops are on a needle on the same slot. Otherwise, False.
        """
        return self.needle_1.slot_number(self.rack) == self.needle_2.slot_number(self.rack)

    @property
    def float_type(self) -> Float_Type:
        """
        Returns:
            Float_Type: The type of float curve to draw based on the relationship between the loops.
        """
        if self.same_slot or (self.same_bed and abs(self.needle_1.position - self.needle_2.position) == 1):
            return Float_Type.Direct_Neighbor
        elif not self.same_bed:
            return Float_Type.Crosses_Beds
        else:
            return self.same_bed_orientation.float_type_by_bed(self.needle_1.is_front)

    @property
    def path_type(self) -> Path_Type:
        """
        Returns:
            Path_Type: The path type that determines the curve of the float based on its relationship to other loops.
        """
        return self.float_type.path_type

    def _set_control_points_by_float_type(self) -> None:
        if self.path_type is Path_Type.Line:
            self._path_type = Path_Type.Line
            self.control_points = []
        elif self.float_type is Float_Type.Behind_Neighbors:
            self.set_cubic_downward_curve(peak_of_curve=(self.settings.Needle_Height / 2) + 2)
        elif self.float_type is Float_Type.In_Front_Of_Neighbors:
            self.set_cubic_upward_curve(peak_of_curve=(self.settings.Needle_Height / 2) + 2)
        else:
            self.set_cubic_crossing_curve()

    @property
    def loop_1(self) -> Machine_Knit_Loop:
        """
        Returns:
            Machine_Knit_Loop: The first loop in this float.
        """
        return self.loop_circle_1.loop

    @property
    def loop_2(self) -> Machine_Knit_Loop:
        """
        Returns:
            Machine_Knit_Loop: The second loop in this float.
        """
        return self.loop_circle_2.loop

    @property
    def needle_1(self) -> Needle:
        """
        Returns:
            Needle: The needle holding the first loop in the float.
        """
        if self.loop_1.holding_needle is None:
            raise ValueError(f"{self.loop_1} is not on a needle and does not form an active float")
        return self.loop_1.holding_needle

    @property
    def needle_2(self) -> Needle:
        """
        Returns:
            Needle: The needle holding the second loop in the float.
        """
        if self.loop_2.holding_needle is None:
            raise ValueError(f"{self.loop_2} is not on a needle and does not form an active float")
        return self.loop_2.holding_needle

    @property
    def float_unique_id(self) -> str:
        """
        Returns:
            str: The unique string identifier of the loop based on its id, the carrier that formed it, and the needle it is formed on.
        """
        return f"{self.loop_1.loop_id}_on_{self.needle_1}_to_{self.loop_2.loop_id}_on_{self.needle_2}"
