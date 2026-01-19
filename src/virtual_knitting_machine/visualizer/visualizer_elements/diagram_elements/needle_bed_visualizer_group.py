"""Module containing the Needle Bed Group class."""

from typing import overload

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.visualizer.diagram_settings import Diagram_Settings
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_bed_element import (
    Needle_Bed_Element,
)
from virtual_knitting_machine.visualizer.visualizer_elements.diagram_elements.needle_box import Needle_Box
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
    """

    def __init__(
        self,
        leftmost_slot: int,
        rightmost_slot: int,
        rack: int,
        all_needle_rack: bool,
        carriage_direction: Carriage_Pass_Direction,
        render_sliders: bool,
        diagram_settings: Diagram_Settings,
    ):
        """
        Constructor for the Needle Bed Group class.
        Args:
            leftmost_slot (int): The leftmost needle slot to render from.
            rightmost_slot (int): The rightmost needle slot to render to.
            rack (int): The racking alignment of the needle beds.
            all_needle_rack (bool): The all needle rack setting to render.
            carriage_direction (Carriage_Pass_Direction): The direction the carriage is moving in. Used to orient the back bed when all-needle racked.
            render_sliders (bool): True if the slider beds are rendered, False otherwise.
            diagram_settings (Diagram_Settings): The machine diagram settings.
        """
        self.render_sliders: bool = render_sliders
        self.leftmost_slot: int = leftmost_slot
        self.rightmost_slot: int = rightmost_slot
        self.rack: int = rack
        self.all_needle_rack: bool = all_needle_rack
        self.carriage_direction: Carriage_Pass_Direction = carriage_direction
        self.settings: Diagram_Settings = diagram_settings
        super().__init__(x=0, y=0, name="NeedleBed")
        self.back_bed: Needle_Bed_Element = Needle_Bed_Element(
            is_front=False,
            is_slider=False,
            leftmost_needle=self.back_leftmost,
            rightmost_needle=self.back_rightmost,
            all_needle_rack=self.all_needle_rack,
            carriage_direction=self.carriage_direction,
            render_sliders=self.render_sliders,
            diagram_setting=self.settings,
        )
        self.add_child(self.back_bed)
        self.front_bed: Needle_Bed_Element = Needle_Bed_Element(
            is_front=True,
            is_slider=False,
            leftmost_needle=self.leftmost_slot,
            rightmost_needle=self.rightmost_slot,
            all_needle_rack=self.all_needle_rack,
            carriage_direction=self.carriage_direction,
            render_sliders=self.render_sliders,
            diagram_setting=self.settings,
        )
        self.add_child(self.front_bed)
        self.back_slider_bed: Needle_Bed_Element | None = (
            Needle_Bed_Element(
                is_front=False,
                is_slider=True,
                leftmost_needle=self.leftmost_slot,
                rightmost_needle=self.rightmost_slot,
                all_needle_rack=self.all_needle_rack,
                carriage_direction=self.carriage_direction,
                render_sliders=self.render_sliders,
                diagram_setting=self.settings,
            )
            if self.render_sliders
            else None
        )
        if self.back_slider_bed is not None:
            self.add_child(self.back_slider_bed)
        self.front_slider_bed: Needle_Bed_Element | None = (
            Needle_Bed_Element(
                is_front=True,
                is_slider=True,
                leftmost_needle=self.back_leftmost,
                rightmost_needle=self.back_rightmost,
                all_needle_rack=self.all_needle_rack,
                carriage_direction=self.carriage_direction,
                render_sliders=self.render_sliders,
                diagram_setting=self.settings,
            )
            if self.render_sliders
            else None
        )
        if self.front_slider_bed is not None:
            self.add_child(self.front_slider_bed)

    @property
    def back_leftmost(self) -> int:
        """
        Returns:
            int: The leftmost position on the back bed.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.leftmost_slot - self.rack

    @property
    def back_rightmost(self) -> int:
        """
        Returns:
            int: The rightmost position on the back bed.

        Notes:
            Racking Calculations:
            * R = F - B
            * F = R + B
            * B = F - R.
        """
        return self.rightmost_slot - self.rack

    @property
    def slot_count(self) -> int:
        """
        Returns:
            int: The slot count for the needle beds.
        Returns:

        """
        return self.rightmost_slot - self.leftmost_slot

    def _add_side_labels(self, label_group: Visualizer_Group) -> None:
        """
        Add the text labels for a needle bed side label group.
        Args:
            label_group (Visualizer_Group): The group for either the left or right labels of the needle bed.
        """

        b_shift = self.settings.all_needle_shift(self.all_needle_rack, self.carriage_direction)

        def _y(row: int) -> int:
            """
            Args:
                row (int): The index of row that represents the needle bed.

            Returns:
                int: The y value for the label on the given bed-row.
            """
            return (self.settings.Needle_Height * row) + self.settings.Needle_Height // 2

        b_label = Text_Element(
            b_shift, _y(0), "B", f"B_{label_group.name}", text_anchor="middle", alignment_baseline="middle"
        )
        label_group.add_child(b_label)
        if self.render_sliders:
            bs_label = Text_Element(
                b_shift, _y(1), "BS", f"BS_{label_group.name}", text_anchor="middle", alignment_baseline="middle"
            )
            label_group.add_child(bs_label)
            fs_label = Text_Element(
                0,
                _y(2),
                "FS",
                f"FS_{label_group.name}",
                text_anchor="middle",
                alignment_baseline="middle",
            )
            label_group.add_child(fs_label)
        f_label = Text_Element(
            0,
            _y(3 if self.render_sliders else 1),
            "F",
            f"F_{label_group.name}",
            text_anchor="middle",
            alignment_baseline="middle",
        )
        label_group.add_child(f_label)

    def has_slot(self, slot: int) -> bool:
        """
        Args:
            slot (int): The slot index of the needle bed.

        Returns:
            bool: True if that slot exists on the needle bed. False, otherwise.
        """
        return self.leftmost_slot <= slot <= self.rightmost_slot

    def has_needle(self, needle: Needle) -> bool:
        """
        Args:
            needle (Needle): The needle to find in the bed group.

        Returns:
            bool: True if the needle is rendered. False, otherwise.
        """
        if not self.has_slot(needle.slot_number(self.rack)):
            return False
        if needle.is_slider:
            return self.render_sliders
        else:
            return True

    def get_needle_box(self, needle: Needle) -> Needle_Box:
        """
        Args:
            needle (Needle): The needle to source in the needle bed.

        Returns:
            Needle_Box: The needle box on the needle bed.

        Raises:
            KeyError: The needle is not in the needle bed.
        """
        if not self.has_needle(needle):
            raise KeyError(f"{needle} is not rendered")
        elif needle.is_front:
            if needle.is_slider:
                assert self.front_slider_bed is not None
                return self.front_slider_bed[needle]
            else:
                return self.front_bed[needle]
        elif needle.is_slider:
            assert self.back_slider_bed is not None
            return self.back_slider_bed[needle]
        else:
            return self.back_bed[needle]

    def __contains__(self, item: int | Needle | str) -> bool:
        if isinstance(item, Needle):
            return self.has_needle(item)
        elif isinstance(item, int):
            return self.has_slot(item)
        else:
            return super().__contains__(item)

    @overload
    def __getitem__(self, item: Needle) -> Needle_Box: ...

    @overload
    def __getitem__(self, item: str) -> Visualizer_Element: ...

    def __getitem__(self, item: Needle | str) -> Needle_Box | Visualizer_Element:
        if isinstance(item, Needle):
            return self.get_needle_box(item)
        else:
            return super().__getitem__(item)
