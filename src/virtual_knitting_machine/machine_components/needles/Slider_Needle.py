"""Module for the Slider_Needle class used in virtual knitting machine operations.

This module provides the Slider_Needle class, which is a specialized type of needle that can only transfer loops but cannot be knit through.
Slider needles are commonly used in knitting machines for loop manipulation operations such as transfers and temporary loop storage.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, TypeGuard, TypeVar

from virtual_knitting_machine.machine_components.needles.Needle import Needle, Needle_Specification
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
        self, is_front: bool, position: int, knitting_machine: Knitting_Machine_State[Machine_LoopT, Any]
    ) -> None:
        super().__init__(is_front, position, knitting_machine)

    @property
    def is_slider(self) -> bool:
        """
        Returns:
            bool: Always returns True for Slider_Needle instances.
        """
        return True

    @staticmethod
    def iterates_over_sliders(sliders: Iterable[Needle_Specification]) -> TypeGuard[Slider_Needle]:
        """
        Args:
            sliders (Iterable[Needle_Specification]): The needles to iterate over and determine that they are all Sliders.

        Returns:
            bool, TypeGuard[Needle]: Returns true if all elements in sliders are Slider Needle objects. Typing system will recognize this guarantee.
        """
        return all(isinstance(n, Slider_Needle) for n in sliders)
