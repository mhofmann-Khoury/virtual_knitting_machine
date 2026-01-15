from typing import Any

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.loop_circle import Loop_Circle
from virtual_knitting_machine.visualizer.visualizer_elements.path_elements import Path_Element


class Float_Line(Path_Element):
    """
    Forms a line between to loop circles in the diagram.
    """

    def __init__(self, loop_1: Loop_Circle, loop_2: Loop_Circle, **path_kwargs: Any):
        self.loop_circle_1: Loop_Circle = loop_1
        self.loop_circle_2: Loop_Circle = loop_2
        super().__init__(
            loop_1.global_x,
            loop_1.global_y,
            loop_2.global_x,
            loop_2.global_y,
            self.float_unique_id,
            stroke=self.loop_1.yarn.properties.color,
            **path_kwargs,
        )

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
