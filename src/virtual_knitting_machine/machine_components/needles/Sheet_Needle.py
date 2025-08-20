"""Module for managing sheet needle construction for multi-sheet knitting operations.

This module provides classes for managing needles in a layered gauging schema used in  multi-sheet knitting.
It includes the Sheet_Needle class which extends the base Needle class to support gauge-based positioning, and the Slider_Sheet_Needle class for slider operations within sheets.
"""
from __future__ import annotations

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import (
    Slider_Needle,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)


class Sheet_Needle(Needle):
    """A needle class for managing needles in a layered gauging schema.

    Sheet needles are used in multi-sheet knitting where multiple layers of knitting are created simultaneously.
    This class extends the base Needle class to provide sheet-aware positioning and operations.

    Attributes:
        recorded_loops (list[Machine_Knit_Loop]): List of loops that have been recorded for this needle.
    """

    def __init__(self, is_front: bool, sheet_pos: int, sheet: int, gauge: int) -> None:
        """Initialize a sheet needle.

        Args:
            is_front (bool): True if this is a front bed needle, False for back bed.
            sheet_pos (int): The position of the needle within the sheet.
            sheet (int): The sheet number within the gauge.
            gauge (int): The number of layers supported by the gauge.
        """
        self._gauge: int = gauge
        self._sheet_pos: int = sheet_pos
        self._sheet: int = sheet
        super().__init__(is_front, Sheet_Needle.get_actual_pos(self.sheet_pos, self.sheet, self.gauge))
        self.recorded_loops: list[Machine_Knit_Loop] = []

    @property
    def gauge(self) -> int:
        """Get the gauge currently being used for knitting.

        Returns:
            int: The gauge (number of layers) currently knitting in.
        """
        return self._gauge

    @property
    def sheet_pos(self) -> int:
        """Get the position of the needle within its sheet.

        Returns:
            int: The position of the needle within the sheet.
        """
        return self._sheet_pos

    @property
    def sheet(self) -> int:
        """Get the sheet number of this needle.

        Returns:
            int: The position of the sheet in the gauge.
        """
        return self._sheet

    @staticmethod
    def get_sheet_pos(actual_pos: int, gauge: int) -> int:
        """Get the sheet position from an actual needle position at a given gauge.

        Args:
            actual_pos (int): The needle position on the bed.
            gauge (int): The number of layers supported by the gauge.

        Returns:
            int: The position in the sheet of a given needle position at a specific gauge.
        """
        return int(actual_pos / gauge)

    @staticmethod
    def get_sheet(actual_pos: int, sheet_pos: int, gauge: int) -> int:
        """Get the sheet number from needle position and sheet position at a given gauge.

        Args:
            actual_pos (int): The needle position on the bed.
            sheet_pos (int): The position in the sheet.
            gauge (int): The number of sheets supported by the gauge.

        Returns:
            int: The sheet of the needle given the gauging.
        """
        return actual_pos - (sheet_pos * gauge)

    @staticmethod
    def get_actual_pos(sheet_pos: int, sheet: int, gauge: int) -> int:
        """Get the actual needle position from sheet needle components.

        Args:
            sheet_pos (int): The position in the sheet.
            sheet (int): The sheet being used.
            gauge (int): The number of sheets supported by the gauge.

        Returns:
            int: The position of the needle on the bed.
        """
        return sheet + sheet_pos * gauge

    def offset_in_sheet(self, offset: int) -> Sheet_Needle:
        """Get a needle offset within the same sheet.

        Args:
            offset (int): Number of sheet positions to move.

        Returns:
            Sheet_Needle: The needle offset by the given value in the sheet (not actual needle positions).
        """
        return self + offset

    def main_needle(self) -> Sheet_Needle:
        """Get the non-slider needle at this needle position.

        Returns:
            Sheet_Needle: The non-slider needle at this needle position.
            If this is not a slider, this instance is returned.
        """
        if not self.is_slider:
            return self
        else:
            return Sheet_Needle(is_front=self.is_front, sheet_pos=self.sheet_pos, sheet=self.sheet, gauge=self.gauge)

    def gauge_neighbors(self) -> list[Sheet_Needle]:
        """Get list of needles that neighbor this needle in other sheets of the same gauge.

        Returns:
            list[Sheet_Needle]: List of needles that neighbor this loop in other gauges.
        """
        neighbors = []
        for i in range(0, self.gauge):
            if i != self.sheet:
                neighbors.append(Sheet_Needle(self.is_front, self.sheet_pos, i, self.gauge))
        return neighbors

    def __add__(self, other: Sheet_Needle | Needle | int) -> Sheet_Needle:
        """Add to this sheet needle's position.

        Args:
            other (Sheet_Needle | Needle | int): The needle or integer to add.

        Returns:
            Sheet_Needle: New sheet needle with the sum position.
        """
        position = other
        if isinstance(other, Sheet_Needle):
            position = other.sheet_pos
        elif isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, self.sheet_pos + position, self.sheet, self.gauge)

    def __radd__(self, other: Sheet_Needle | Needle | int) -> Sheet_Needle:
        """Right-hand add operation for sheet needle.

        Args:
            other (Sheet_Needle | Needle | int): The needle or integer to add.

        Returns:
            Sheet_Needle: New sheet needle with the sum position.
        """
        position = other
        if isinstance(other, Sheet_Needle):
            position = other.sheet_pos
        elif isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, position + self.sheet_pos, self.sheet, self.gauge)

    def __sub__(self, other: Sheet_Needle | Needle | int) -> Sheet_Needle:
        """Subtract from this sheet needle's position.

        Args:
            other (Sheet_Needle | Needle | int): The needle or integer to subtract.

        Returns:
            Sheet_Needle: New sheet needle with the difference position.
        """
        position = other
        if isinstance(other, Sheet_Needle):
            position = other.sheet_pos
        elif isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, self.sheet_pos - position, self.sheet, self.gauge)

    def __rsub__(self, other: Sheet_Needle | Needle | int) -> Sheet_Needle:
        """Right-hand subtract operation for sheet needle.

        Args:
            other (Sheet_Needle | Needle | int): The needle or integer to subtract from.

        Returns:
            Sheet_Needle: New sheet needle with the difference position.
        """
        position = other
        if isinstance(other, Sheet_Needle):
            position = other.sheet_pos
        elif isinstance(other, Needle):
            position = other.position
        return self.__class__(self.is_front, position - self.sheet_pos, self.sheet, self.gauge)


class Slider_Sheet_Needle(Sheet_Needle, Slider_Needle):
    """A slider needle class for use in gauging schema.

    This class combines the functionality of Sheet_Needle and Slider_Needle to provide
    slider needle capabilities within a multi-sheet knitting environment.
    """

    def __init__(self, is_front: bool, sheet_pos: int, sheet: int, gauge: int) -> None:
        """Initialize a slider sheet needle.

        Args:
            is_front (bool): True if this is a front bed needle, False for back bed.
            sheet_pos (int): The position of the needle within the sheet.
            sheet (int): The sheet number within the gauge.
            gauge (int): The number of layers supported by the gauge.
        """
        super().__init__(is_front, sheet_pos, sheet, gauge)


def get_sheet_needle(needle: Needle, gauge: int, slider: bool = False) -> Sheet_Needle:
    """Convert a standard needle to a sheet needle with the given gauge.

    Args:
        needle (Needle): The original needle to convert.
        gauge (int): The gauge of the sheet.
        slider (bool, optional): True if returning a slider needle. Defaults to False.

    Returns:
        Sheet_Needle: Sheet needle created from the standard needle given the gauging schema.
    """
    sheet_pos = Sheet_Needle.get_sheet_pos(needle.position, gauge)
    sheet = Sheet_Needle.get_sheet(needle.position, sheet_pos, gauge)
    if slider:
        return Slider_Sheet_Needle(needle.is_front, sheet_pos, sheet, gauge)
    else:
        return Sheet_Needle(needle.is_front, sheet_pos, sheet, gauge)
