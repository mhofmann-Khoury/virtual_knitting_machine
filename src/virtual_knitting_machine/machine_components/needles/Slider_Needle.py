"""Module for the Slider_Needle class used in virtual knitting machine operations.

This module provides the Slider_Needle class, which is a specialized type of needle that can only transfer loops but cannot be knit through.
Slider needles are commonly used in knitting machines for loop manipulation operations such as transfers and temporary loop storage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop

if TYPE_CHECKING:
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State

Machine_LoopT = TypeVar("Machine_LoopT", bound=Machine_Knit_Loop)


class Slider_Needle(Needle[Machine_LoopT]):
    """A specialized needle subclass for slider needles in knitting machines.

    Slider needles are needles that can hold and transfer loops but cannot be knit through.
    They are used for temporary loop storage and loop manipulation operations such as transfers between beds or complex stitch formations.

    This class inherits all functionality from the base Needle class but overrides specific properties to indicate its slider nature.
    """

    def __init__(
        self, is_front: bool, position: int, knitting_machine: Knitting_Machine_State[Machine_LoopT, Any] | None = None
    ) -> None:
        super().__init__(is_front, position, knitting_machine)

    def __str__(self) -> str:
        """Return string representation of the slider needle.

        Returns:
            str: String representation with 's' suffix (e.g., 'fs5' for front slider at position 5, 'bs3' for back slider at position 3).
        """
        if self.is_front:
            return f"fs{self.position}"
        else:
            return f"bs{self.position}"

    @property
    def is_slider(self) -> bool:
        """
        Returns:
            bool: Always returns True for Slider_Needle instances.
        """
        return True
