"""Module containing the Needle Bed Group class."""

from typing import overload

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_group import Needle_Group
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_slot import Needle_Slot
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Text_Element, Visualizer_Element
from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_group import Visualizer_Group


class Needle_Bed_Group(Visualizer_Group):
    """
    Wrapper class for the groupings that form the Needle Bed diagram.

    Attributes:
        render_sliders (bool): True if the slider beds are rendered, False otherwise.
        leftmost_slot (int): The leftmost needle slot to render from.
        rightmost_slot (int): The rightmost needle slot to render to.
        rack (int): The racking alignment of the needle beds.
        all_needle_rack (bool): The all needle rack setting to render.
        settings (Diagram_Settings): The machine diagram settings.
        slots (dict[int, Needle_Slot]): A mapping from slot indies to the rendered needle slots.
        left_label: Visualizer_Group | None: The optional label on the left side of the diagram.
        right_label: Visualizer_Group | None: The optional label on the right side of the diagram.
    """

    def __init__(
        self,
        leftmost_slot: int,
        rightmost_slot: int,
        rack: int,
        all_needle_rack: bool,
        render_sliders: bool,
        diagram_settings: Diagram_Settings,
        x: int = 0,
        y: int = 0,
        name: str = "NeedleBed",
    ):
        """
        Constructor for the Needle Bed Group class.
        Args:
            leftmost_slot (int): The leftmost needle slot to render from.
            rightmost_slot (int): The rightmost needle slot to render to.
            rack (int): The racking alignment of the needle beds.
            all_needle_rack (bool): The all needle rack setting to render.
            render_sliders (bool): True if the slider beds are rendered, False otherwise.
            diagram_settings (Diagram_Settings): The machine diagram settings.
            x (int): The x coordinate to orient the needle bed around.
            y (int): The y coordinate to orient the needle bed around.
            name (str, optional): The name id of the Needle Bed Group. Defaults to "NeedleBed".
        """
        super().__init__(x, y, name)
        self.render_sliders: bool = render_sliders
        self.leftmost_slot: int = leftmost_slot
        self.rightmost_slot: int = rightmost_slot
        self.rack: int = rack
        self.all_needle_rack: bool = all_needle_rack
        self.settings: Diagram_Settings = diagram_settings
        self.left_label: Visualizer_Group | None = None
        if self.settings.render_left_labels:
            self.left_label = Visualizer_Group(x=0, y=0, name="Left_Bed_Labels")
            self._add_side_labels(self.left_label)
            self.add_child(self.left_label)
        self.slots: dict[int, Needle_Slot] = {}
        self.right_label: Visualizer_Group | None = None
        self._build_slots()

    def _build_slots(self) -> None:
        right_most_slot = None
        for x_index, slot_number in enumerate(range(self.leftmost_slot, self.rightmost_slot + 1)):
            slot = Needle_Slot(
                x_index, slot_number, self.rack, self.all_needle_rack, self.settings, self.render_sliders
            )
            self.slots[slot_number] = slot
            self.add_child(slot)
            right_most_slot = slot

        if self.settings.render_right_labels:
            assert right_most_slot is not None
            self.right_label = Visualizer_Group(
                x=right_most_slot.x + self.settings.Needle_Width + self.settings.Label_Padding,
                y=0,
                name="Right_Bed_Labels",
            )
            self._add_side_labels(self.right_label)
            self.add_child(self.right_label)

    def _add_side_labels(self, label_group: Visualizer_Group) -> None:
        """
        Add the text labels for a needle bed side label group.
        Args:
            label_group (Visualizer_Group): The group for either the left or right labels of the needle bed.
        """

        all_needle_alignment = int(self.settings.Needle_Width / 2) if self.all_needle_rack else 0
        y_value = (
            self.settings.Needle_Height + int(self.settings.Needle_Height / 2) + self.settings.Label_Padding
            if self.settings.render_back_labels
            else 0
        )
        b_label = Text_Element(
            0, y_value, "B", f"B_{label_group.name}", text_anchor="start", alignment_baseline="middle"
        )
        y_value += self.settings.Needle_Height
        label_group.add_child(b_label)
        if self.render_sliders:
            bs_label = Text_Element(
                0, y_value, "BS", f"B_{self.settings.Label_Padding}", text_anchor="start", alignment_baseline="middle"
            )
            y_value += self.settings.Needle_Height
            label_group.add_child(bs_label)
            fs_label = Text_Element(
                0 + all_needle_alignment,
                y_value,
                "FS",
                f"FS_{self.settings.Label_Padding}",
                text_anchor="start",
                alignment_baseline="middle",
            )
            y_value += self.settings.Needle_Height
            label_group.add_child(fs_label)
        f_label = Text_Element(
            0 + all_needle_alignment,
            y_value,
            "F",
            f"F_{self.settings.Label_Padding}",
            text_anchor="start",
            alignment_baseline="middle",
        )
        label_group.add_child(f_label)

    def has_slot(self, slot: int) -> bool:
        """
        Args:
            slot (int): A slot index to find in the rendered needle bed.

        Returns:
            bool: True if the slot is in this rendering. False, otherwise
        """
        return slot in self.slots

    def get_slot(self, slot: int) -> Needle_Slot:
        """
        Args:
            slot (int): A slot index to find in the rendered needle bed.

        Returns:
            Needle_Slot: The slot at that index.

        Raises:
            KeyError: If the slot is in this rendering.
        """
        return self.slots[slot]

    def has_needle(self, needle: Needle) -> bool:
        """
        Args:
            needle (Needle): A needle to find in this rendering.

        Returns:
            bool: True if the slot is in this rendering. False, otherwise.
        """
        if needle.is_slider and (not self.render_sliders):
            return False
        return self.has_slot(needle.slot_number(self.rack))

    def get_needle_group(self, needle: Needle) -> Needle_Group:
        """
        Args:
            needle (Needle): A needle to find in this rendering.

        Returns:
            Needle_Group: The needle group representing that needle in the diagram.

        Raises:
            KeyError: If the needle is not in the rendering.
        """
        if not self.has_needle(needle):
            raise KeyError(f"{needle} is not in this rendered slots {list(self.slots.keys())}.")
        slot = self.get_slot(needle.slot_number(self.rack))
        return slot[needle]

    def __contains__(self, item: int | Needle | str) -> bool:
        if isinstance(item, Needle):
            return self.has_needle(item)
        elif isinstance(item, int):
            return self.has_slot(item)
        else:
            return super().__contains__(item)

    @overload
    def __getitem__(self, item: int) -> Needle_Slot: ...

    @overload
    def __getitem__(self, item: Needle) -> Needle_Group: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: int | Needle | str) -> Needle_Slot | Needle_Group | Visualizer_Element:
        if isinstance(item, Needle):
            return self.get_needle_group(item)
        elif isinstance(item, int):
            return self.get_slot(item)
        else:
            return super().__getitem__(item)
