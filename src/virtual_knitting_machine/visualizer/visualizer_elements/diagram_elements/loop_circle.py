"""Module containing the Loop_Circle class"""

from __future__ import annotations

from typing import Any

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_box import Needle_Box
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_shapes import Circle_Element


class Loop_Circle(Circle_Element):
    """
    Wrapper for SVG element that represents a loop placed on a needle in the diagram.
    """

    def __init__(
        self,
        loop: Machine_Knit_Loop,
        diagram_settings: Diagram_Settings,
        radius: float | None = None,
        y: float | None = None,
        **shape_kwargs: Any,
    ):
        """
        Args:
            loop (Machine_Knit_Loop): The loop being rendered.
            diagram_settings  (Diagram_Settings): The settings for the diagram being rendered.
            radius (float, optional): The radius of the loop circle. Defaults to the radius in the diagram settings.
            y (int, optional): The y position of the loop circle relative to the needle box. Defaults to the mid point of the needle box.
            **shape_kwargs (Any): Additional keyword arguments to pass to the shape.

        Notes:
            If this is the first loop in the stack, it will be centered on the needle box. Subsequent loops will be shifted outward from the needle beds.
        """
        self.settings: Diagram_Settings = diagram_settings
        self._loop: Machine_Knit_Loop = loop
        super().__init__(
            radius=self.settings.loop_radius if radius is None else radius,
            x=self.settings.Needle_Width // 2,
            y=self.settings.Needle_Height / 2 if y is None else y,
            name=self.loop_unique_id,
            stroke_width=self.settings.Loop_Stroke_Width,
            fill=self.settings.Yarn_Fill_Lightening_Factor,
            stroke=self._loop.yarn.properties.color,
            **shape_kwargs,
        )

    @property
    def loop_unique_id(self) -> str:
        """
        Returns:
            str: The unique string identifier of the loop based on its id, the carrier that formed it, and the needle it is formed on.
        """
        return f"{self.loop.loop_id}_on_c{self.loop.yarn.carrier.carrier_id}_on_{self.loop.holding_needle}"

    @property
    def loop(self) -> Machine_Knit_Loop:
        """
        Returns:
            Machine_Knit_Loop: The loop that this represents.
        """
        return self._loop


class Loop_Stack(Visualizer_Group):

    def __init__(self, loops: list[Machine_Knit_Loop], needle_box: Needle_Box, diagram_settings: Diagram_Settings):
        self.settings: Diagram_Settings = diagram_settings
        self._needle_box: Needle_Box = needle_box
        super().__init__(x=self._needle_box.global_x, y=self._needle_box.global_y, name=self.loop_stack_unique_name)
        self.loop_circles: list[Loop_Circle] = []
        if len(loops) == 1:
            self.loop_circles.append(Loop_Circle(loops[0], diagram_settings))
        else:
            loop_diameter = self.settings.stacked_loop_diameter(len(loops))
            loop_radius = loop_diameter / 2.0

            y_shift = loop_diameter * self.settings.loop_stack_shift_portion
            if self._needle_box.is_back:  # Shift upward from back beds.
                y = self.settings.Needle_Height - self.settings.loop_stack_top - loop_radius
                y_shift *= -1.0
            else:
                y = self.settings.loop_stack_top + loop_radius
            for i, loop in enumerate(reversed(loops)):
                loop_circle = Loop_Circle(
                    loop=loop, diagram_settings=self.settings, radius=loop_radius, y=y + (i * y_shift)
                )
                self.loop_circles.insert(0, loop_circle)
        for loop_circle in self.loop_circles:
            self.add_child(loop_circle)

    @property
    def loop_stack_unique_name(self) -> str:
        """
        Returns:
            str: The unique string identifier for the stack of loops ona specific needle.
        """
        return f"Loop_Stack_on_{self._needle_box.needle}"
