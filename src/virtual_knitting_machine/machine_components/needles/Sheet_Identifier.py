"""Module containing the Sheet_Identifier class for identifying sheets at a given gauge."""

from __future__ import annotations

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Sheet_Needle import (
    Sheet_Needle,
    Slider_Sheet_Needle,
)
from virtual_knitting_machine.machine_components.needles.Slider_Needle import (
    Slider_Needle,
)


class Sheet_Identifier:
    """
    Class used to identify sheets at a given gauge.
    """

    def __init__(self, sheet: int, gauge: int):
        assert gauge > 0, f"Knit Pass Error: Cannot make sheets for gauge {gauge}"
        assert 0 <= sheet < gauge, f"Cannot identify sheet {sheet} at gauge {gauge}"
        self._sheet: int = sheet
        self._gauge: int = gauge

    @property
    def sheet(self) -> int:
        """

        Returns:
            int: The position of the sheet in the gauge.
        """
        return self._sheet

    @property
    def gauge(self) -> int:
        """

        Returns:
            int: The number of active sheets.
        """
        return self._gauge

    def get_needle(self, needle: Needle) -> Sheet_Needle:
        """ Used to identify the sheet needle from a given base needle.
        Args:
            needle: Needle to access from sheet. Maybe a sheet needle which will be retargeted to this sheet.

        Returns:
            Sheet_Needle:
                The sheet needle at the given needle index and bed

        """
        pos = needle.position
        if isinstance(needle, Sheet_Needle):
            pos = needle.sheet_pos
        if isinstance(needle, Slider_Needle):
            return Slider_Sheet_Needle(needle.is_front, pos, self.sheet, self.gauge)
        else:
            return Sheet_Needle(needle.is_front, pos, self.sheet, self.gauge)

    def needle(self, is_front: bool, position: int) -> Sheet_Needle:
        """ Gets a needle within the sheet with specified position

        Args:
            is_front (bool): True if needle is on front bed.
            position (bool): The position within the sheet.

        Returns:
            Sheet_Needle:
                The specified sheet needle.
        """
        return Sheet_Needle(is_front, position, self.sheet, self.gauge)

    def __str__(self) -> str:
        return f"s{self.sheet}:g{self.gauge}"

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.sheet

    def __lt__(self, other: Sheet_Identifier | int) -> bool:
        return self.sheet < int(other)

    def __eq__(self, other: Sheet_Identifier | int) -> bool:
        if isinstance(other, Sheet_Identifier):
            return self.sheet == other.sheet and self.gauge == other.gauge
        else:
            return self.sheet == int(other)
