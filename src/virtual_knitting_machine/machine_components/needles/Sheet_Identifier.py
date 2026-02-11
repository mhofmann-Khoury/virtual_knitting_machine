"""Module containing the Sheet_Identifier class for identifying sheets at a given gauge."""

from __future__ import annotations

from typing import cast

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
from virtual_knitting_machine.machine_components.needles.Needle import Needle


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

    def needle(
        self, is_front: bool, position_in_sheet: int, machine_state: Knitting_Machine_State, is_slider: bool = False
    ) -> Needle:
        """Gets a needle within the sheet with specified position

        Args:
            is_front (bool): True if needle is on front bed.
            position_in_sheet (bool): The position within the sheet.
            machine_state (Knitting_Machine_State): The state of the machine to get the needle from.
            is_slider (bool,): True if needle is a slider. Defaults to False.

        Returns:
            Needle: The needle in the machine state at the given sheet position.
        """
        return machine_state.get_specified_needle(
            is_front, Needle.needle_position_from_sheet_and_gauge(position_in_sheet, self.sheet, self.gauge), is_slider
        )

    def __str__(self) -> str:
        return f"s{self.sheet}:g{self.gauge}"

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.sheet

    def __lt__(self, other: Sheet_Identifier | int) -> bool:
        return self.sheet < int(other)

    def __eq__(self, other: object) -> bool:
        """

        Args:
            other (Sheet_Identifier | int): The other sheet identifier to compare to.

        Returns:
            bool:
                True if the two sheets are identical. False otherwise.
                If a Sheet Identifier is given, both the sheet and gauge must match. If an integer is given, only the sheet needs to match.

        """
        if isinstance(other, Sheet_Identifier):
            return self.sheet == other.sheet and self.gauge == other.gauge
        else:
            return self.sheet == cast(int, other)
