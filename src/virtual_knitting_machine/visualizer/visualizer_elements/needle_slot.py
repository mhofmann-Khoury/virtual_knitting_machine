"""Module containing the Needle_Slot class"""

from typing import overload

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import (
    Rect_Element,
    Text_Element,
    Visualizer_Element,
)
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group


class Needle_Slot(Visualizer_Group):
    """
    A wrapper class for an SVG Group containing a slot of needles and their labels.

    Attributes:
        settings (Diagram_Settings): The settings of the machine diagram.
        all_needle_rack (bool): True if the needle bed is set for all needle racking.
        rack (int): The racking of the needle beds.
        render_sliders (bool): If True, the slider beds are rendered.

    """

    def __init__(
        self,
        x_index: int,
        slot_number: int,
        rack: int,
        all_needle_rack: bool,
        diagram_settings: Diagram_Settings,
        render_sliders: bool = False,
    ) -> None:
        self.settings: Diagram_Settings = diagram_settings
        x = x_index * diagram_settings.Needle_Width
        if self.settings.render_left_labels:  # Add space for left labels
            x += diagram_settings.Needle_Width
        super().__init__(x, 0, f"slot_{slot_number}")
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self.render_sliders: bool = render_sliders
        self._slot_number: int = slot_number
        self._front_needle: Rect_Element | None = None
        self._back_needle: Rect_Element | None = None
        self._front_slider: Rect_Element | None = None
        self._back_slider: Rect_Element | None = None
        self._back_label: Text_Element | None = None
        self._front_label: Text_Element | None = None

    def _build_group(self) -> None:
        label_height = 0
        all_needle_alignment = int(self.settings.Needle_Width / 2) if self.all_needle_rack else 0
        if self.settings.render_back_labels:
            self._back_label = Text_Element(
                x=int(self.settings.Needle_Width / 2),
                y=self.settings.Needle_Height,
                label=str(self.slot_number - self.rack),
                name=f"label_b{self.slot_number - self.rack}",
                text_anchor="middle",
                alignment_baseline="baseline",
            )
            self.add_child(self._back_label)
            label_height += self.settings.Needle_Height + self.settings.Label_Padding
        # add back bed needle
        self._back_needle = Rect_Element(
            x=0,
            y=label_height,
            name=f"b{self.slot_number - self.rack}",
            width=self.settings.Needle_Width,
            height=self.settings.Needle_Height,
            stroke=self.settings.Needle_Stroke_Color,
            stroke_width=self.settings.Needle_Stroke_Width,
            fill="none",
        )
        self.add_child(self._back_needle)
        slider_height = 0
        if self.render_sliders:
            self._back_slider = Rect_Element(
                x=0,
                y=label_height + self.settings.Needle_Height,
                name=f"bs{self.slot_number - self.rack}",
                width=self.settings.Needle_Width,
                height=self.settings.Needle_Height,
                stroke=self.settings.Needle_Stroke_Color,
                stroke_width=self.settings.Needle_Stroke_Width,
                fill=self.settings.Slider_Background_Color,
            )
            self._front_slider = Rect_Element(
                x=all_needle_alignment,
                y=label_height + 2 * self.settings.Needle_Height,
                name=f"fs{self.slot_number}",
                width=self.settings.Needle_Width,
                height=self.settings.Needle_Height,
                stroke=self.settings.Needle_Stroke_Color,
                stroke_width=self.settings.Needle_Stroke_Width,
                fill=self.settings.Slider_Background_Color,
            )
            self.add_child(self._back_slider)
            self.add_child(self._front_slider)
            slider_height += self.settings.Needle_Height * 2
        self._front_needle = Rect_Element(
            x=all_needle_alignment,
            y=label_height + self.settings.Needle_Height + slider_height,
            name=f"f{self.slot_number}",
            width=self.settings.Needle_Width,
            height=self.settings.Needle_Height,
            stroke=self.settings.Needle_Stroke_Color,
            stroke_width=self.settings.Needle_Stroke_Width,
            fill="none",
        )
        self.add_child(self._front_needle)
        if self.settings.render_front_labels:
            self._front_label = Text_Element(
                x=all_needle_alignment + int(self.settings.Needle_Width / 2),
                y=2 * self.settings.Label_Padding + 3 * self.settings.Needle_Height + slider_height,
                label=str(self.slot_number),
                name=f"label_f{self.slot_number}",
                text_anchor="middle",
                alignment_baseline="hanging",
            )
            self.add_child(self._front_label)

    @property
    def front_needle(self) -> Rect_Element:
        """
        Returns:
            Rect_Element: The front needle element for the given slot.
        """
        if self._front_needle is None:
            self._build_group()
            assert self._front_needle is not None
        return self._front_needle

    @property
    def back_needle(self) -> Rect_Element:
        """
        Returns:
            Rect_Element: The back needle element for the given slot.
        """
        if self._back_needle is None:
            self._build_group()
            assert self._back_needle is not None
        return self._back_needle

    @property
    def front_slider(self) -> Rect_Element | None:
        """
        Returns:
            Rect_Element | None: The front slider element for the given slot or None if sliders were not rendered.
        """
        return self._front_slider

    @property
    def back_slider(self) -> Rect_Element | None:
        """
        Returns:
            Rect_Element: The back slider element for the given slot or None if sliders were not rendered.
        """
        return self._back_slider

    @property
    def slot_number(self) -> int:
        """
        Returns:
            int: The number of this slot.
        """
        return self._slot_number

    @overload
    def __getitem__(self, item: Needle) -> Rect_Element: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: Needle | str) -> Rect_Element | Visualizer_Element:
        """

        Args:
            item (Needle | str):
                The needle rectangle to retrieve from this slot
                or
                The name-id of a element that belongs to this slot.

        Returns:
            Rect_Element | Visualizer_Element:
                The needle rectangle element belonging to the given needle
                or
                The element with the given name-id.

        Raises:
            KeyError: If the needle does not belong to this slot or is not rendered or the name-id does not belong to this slot.
        """
        if isinstance(item, str):
            return super().__getitem__(item)
        elif item.is_front:
            if item.position != self.slot_number:
                raise KeyError(f"{item} is not in slot {self.slot_number}")
            if item.is_slider:
                if self.front_slider is None:
                    raise KeyError(f"{item} is not in slot {self.slot_number} which has no sliders")
                return self.front_slider
            else:
                return self.front_needle
        else:
            if item.position != self.slot_number - self.rack:
                raise KeyError(f"{item} is not in slot {self.slot_number} at racking {self.rack}")
            if item.is_slider:
                if self.back_slider is None:
                    raise KeyError(f"{item} is not in slot {self.slot_number} which has no sliders")
                return self.back_slider
            else:
                return self.back_needle

    def __int__(self) -> int:
        return self.slot_number

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Needle_Slot):
            return self.slot_number < other.slot_number
        else:
            raise TypeError(f"Cannot compare slot group to object of type {type(other)}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Needle_Slot):
            return self.slot_number == other.slot_number
        else:
            raise TypeError(f"Cannot compare slot group to object of type {type(other)}")

    def __hash__(self) -> int:
        return hash(self.name)
