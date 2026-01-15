"""Module containing the Needle_Slot class"""

from typing import overload

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.needle_group import Needle_Group
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Text_Element, Visualizer_Element
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
        super().__init__(self.settings.x_of_needle(x_index), 0, f"slot_{slot_number}")
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self.render_sliders: bool = render_sliders
        self._slot_number: int = slot_number
        self._back_label: Text_Element | None = None
        if self.settings.render_back_labels:
            self._back_label = Text_Element(
                x=int(self.settings.Needle_Width / 2),
                y=self.settings.back_label_y,
                label=str(self.back_needle_position),
                name=f"label_b{self.back_needle_position}",
                text_anchor="middle",
                alignment_baseline="baseline",
            )
            self.add_child(self._back_label)
        self._back_needle: Needle_Group = Needle_Group(Needle(is_front=False, position=self.back_needle_position), self)
        self.add_child(self._back_needle)
        self._front_slider: Needle_Group | None = None
        self._back_slider: Needle_Group | None = None
        if self.render_sliders:
            self._back_slider = Needle_Group(Slider_Needle(is_front=False, position=self.back_needle_position), self)
            self._front_slider = Needle_Group(Slider_Needle(is_front=True, position=self.slot_number), self)
            self.add_child(self._back_slider)
            self.add_child(self._front_slider)
        self._front_needle: Needle_Group = Needle_Group(Needle(is_front=True, position=self.slot_number), self)
        self.add_child(self._front_needle)
        self._front_label: Text_Element | None = None
        if self.settings.render_front_labels:
            self._front_label = Text_Element(
                x=self._front_needle.x + int(self.settings.Needle_Width / 2),
                y=self.settings.front_label_y(self.render_sliders),
                label=str(self.slot_number),
                name=f"label_f{self.slot_number}",
                text_anchor="middle",
                alignment_baseline="hanging",
            )
            self.add_child(self._front_label)

    @property
    def front_needle(self) -> Needle_Group:
        """
        Returns:
            Needle_Group: The front needle element for the given slot.
        """
        return self._front_needle

    @property
    def back_needle(self) -> Needle_Group:
        """
        Returns:
            Needle_Group: The back needle element for the given slot.
        """
        return self._back_needle

    @property
    def front_slider(self) -> Needle_Group | None:
        """
        Returns:
            Needle_Group | None: The front slider element for the given slot or None if sliders were not rendered.
        """
        return self._front_slider

    @property
    def back_slider(self) -> Needle_Group | None:
        """
        Returns:
            Needle_Group: The back slider element for the given slot or None if sliders were not rendered.
        """
        return self._back_slider

    @property
    def slot_number(self) -> int:
        """
        Returns:
            int: The number of this slot.
        """
        return self._slot_number

    @property
    def back_needle_position(self) -> int:
        """

        Returns:
            int: The position of the back needle in this slot at the given racking.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.

        """
        return self.slot_number - self.rack

    @overload
    def __getitem__(self, item: Needle) -> Needle_Group: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: Needle | str) -> Needle_Group | Visualizer_Element:
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
            if item.position != self.back_needle_position:
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
