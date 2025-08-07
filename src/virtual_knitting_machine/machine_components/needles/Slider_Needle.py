"""Module for the Slider_Needle class."""
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Slider_Needle(Needle):
    """
    A Needle subclass for slider needles which an only transfer loops, but not be knit through
    """

    def __init__(self, is_front: bool, position: int):
        super().__init__(is_front, position)

    def __str__(self) -> str:
        if self.is_front:
            return f"fs{self.position}"
        else:
            return f"bs{self.position}"

    @property
    def is_slider(self) -> bool:
        """
        :return: True if the needle is a slider
        """
        return True
