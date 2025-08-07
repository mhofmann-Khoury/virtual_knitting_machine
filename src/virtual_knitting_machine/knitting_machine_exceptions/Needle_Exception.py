"""Module containing common Machine Knitting Exceptions that involve needles."""
from __future__ import annotations
from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Needle_Exception(Knitting_Machine_Exception):
    def __init__(self, needle: Needle, message: str) -> None:
        self.needle = needle
        super().__init__(message)


class Slider_Loop_Exception(Needle_Exception):
    def __init__(self, needle: Needle) -> None:
        super().__init__(needle, f"Slider {needle} cannot form a new loop")


class Clear_Needle_Exception(Needle_Exception):
    def __init__(self, needle: Needle) -> None:
        super().__init__(needle, f"Cannot use {needle} until sliders are clear")


class Xfer_Dropped_Loop_Exception(Needle_Exception):

    def __init__(self, needle: Needle) -> None:
        super().__init__(needle, f"Cannot transfer dropped loop to target needle {needle}")


class Misaligned_Needle_Exception(Needle_Exception):

    def __init__(self, start_needle: Needle, target_needle: Needle) -> None:
        self.target_needle = target_needle
        super().__init__(start_needle, f"Needles {start_needle} and {target_needle} are not aligned.")

    @property
    def start_needle(self) -> Needle:
        """
        :return: Property used to have multiple names for start needle.
        """
        return self.needle
