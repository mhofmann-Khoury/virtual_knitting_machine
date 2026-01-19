"""
Module containing the Needle_Bed_Element class
"""

from typing import overload

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_box import Needle_Box
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Text_Element, Visualizer_Element
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group


class Needle_Bed_Element(Visualizer_Group):

    def __init__(
        self,
        is_front: bool,
        is_slider: bool,
        leftmost_needle: int,
        rightmost_needle: int,
        all_needle_rack: bool,
        carriage_direction: Carriage_Pass_Direction,
        render_sliders: bool,
        diagram_setting: Diagram_Settings,
    ):
        self.render_sliders = render_sliders
        self.carriage_direction: Carriage_Pass_Direction = carriage_direction
        self.all_needle_rack: bool = all_needle_rack
        self.settings: Diagram_Settings = diagram_setting
        self.rightmost_needle: int = rightmost_needle
        self.leftmost_needle: int = leftmost_needle
        self.is_slider: bool = is_slider
        self.is_front: bool = is_front
        super().__init__(self.bed_x_shift, self.settings.Needle_Height * self.bed_row, self.unique_bed_name)
        self.needle_boxes: dict[int, Needle_Box] = {}
        self.labels: dict[int, Text_Element] = {}
        self._build_needles()

    @property
    def needle_count(self) -> int:
        """
        Returns:
            int: The number of needle boxes rendered in the bed.
        """
        return self.rightmost_needle - self.leftmost_needle

    def on_bed(self, needle: Needle) -> bool:
        """
        Args:
            needle (Needle): Needle to check if it belongs to this bed.

        Returns:
            bool: True if this needle belongs to this bed. False otherwise.

        Notes:
            This does not check that the needle is rendered within the diagram's window. Only that it belongs to this bed.
            For full index checking, use in operator.
        """
        return needle.is_front == self.is_front and needle.is_slider == self.is_slider

    def index_of_needle(self, needle: int | Needle) -> int:
        """
        Args:
            needle (int | Needle): The needle or position of a needle to index on this bed.

        Returns:
            int: The index of that needle on this bed.

        Raise:
            KeyError: If the given needle or position is not being rendered on this bed.
        """
        if isinstance(needle, Needle) and not self.on_bed(needle):
            raise KeyError(f"{needle} does not belong to this bed")
        if int(needle) not in self:
            raise KeyError(
                f"{needle} outside the bounds of the diagram from {self.leftmost_needle} to {self.rightmost_needle}"
            )
        return int(needle) - self.leftmost_needle

    def _build_needles(self) -> None:
        def _needle(n: int) -> Needle:
            if self.is_slider:
                return Slider_Needle(is_front=self.is_front, position=n)
            else:
                return Needle(is_front=self.is_front, position=n)

        for needle_position in range(self.leftmost_needle, self.rightmost_needle + 1):
            needle = _needle(needle_position)
            n_box = Needle_Box(needle, self)
            self.needle_boxes[needle_position] = n_box
            if self.add_label:
                if self.is_back:
                    self.labels[needle_position] = Text_Element(
                        x=n_box.x + self.settings.Needle_Width // 2,
                        y=-1 * self.settings.Label_Padding,
                        label=str(needle_position),
                        name=f"label_{needle}",
                        text_anchor="middle",
                        alignment_baseline="baseline",
                    )
                else:
                    self.labels[needle_position] = Text_Element(
                        x=n_box.x + self.settings.Needle_Width // 2,
                        y=self.settings.Needle_Height + self.settings.Label_Padding,
                        label=str(needle_position),
                        name=f"label_{needle}",
                        text_anchor="middle",
                        alignment_baseline="hanging",
                    )

        for nbox in self.needle_boxes.values():
            self.add_child(nbox)
        for label in self.labels.values():
            self.add_child(label)

    @property
    def bed_x_shift(self) -> int:
        """
        Returns:
            int: The amount to horizontally shift this bed based on its position and all needle racking.
        """
        return self.settings.all_needle_shift(self.all_needle_rack, self.carriage_direction) if self.is_back else 0

    @property
    def is_back(self) -> bool:
        """
        Returns:
            bool: True if this a back bed.
        """
        return not self.is_front

    @property
    def add_label(self) -> bool:
        """
        Returns:
            bool: True if this bed should also have labels
        """
        return (not self.is_slider) and (
            (self.is_front and self.settings.render_front_labels) or (self.is_back and self.settings.render_back_labels)
        )

    @property
    def unique_bed_name(self) -> str:
        """
        Returns:
            str: The unique name of the bed element.
        """
        if self.is_front:
            if self.is_slider:
                return "FS_Bed"
            else:
                return "F_Bed"
        elif self.is_slider:
            return "BS_Bed"
        else:
            return "B_Bed"

    @property
    def bed_row(self) -> int:
        """
        Returns:
            int: The index of the row that this bed belongs to.
        """
        if self.is_back:
            if self.is_slider:
                return 1
            else:
                return 0
        elif self.is_slider:
            return 2
        elif self.render_sliders:
            return 3
        else:
            return 1

    @overload
    def __getitem__(self, item: int | Needle) -> Needle_Box: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: int | Needle | str) -> Visualizer_Element:
        if isinstance(item, Needle) and not self.on_bed(item):
            raise KeyError(f"{item} is not on {self.name} bed.")
        if isinstance(item, (int, Needle)):
            return self.needle_boxes[int(item)]
        else:
            return super().__getitem__(item)

    def __contains__(self, item: int | Needle | str) -> bool:
        if isinstance(item, Needle):
            return self.on_bed(item) and self.leftmost_needle <= item.position <= self.rightmost_needle
        elif isinstance(item, int):
            return self.leftmost_needle <= item <= self.rightmost_needle
        else:
            return super().__contains__(item)
