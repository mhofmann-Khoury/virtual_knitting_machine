"""Module for the Slider_Needle class."""
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Slider_Needle(Needle):
    """
    A Needle subclass for slider needles which an only transfer loops, but not be knit through
    """

    def __init__(self, is_front: bool, position: int):
        super().__init__(is_front, position)

    def __str__(self):
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

    def is_clear(self, machine_state):
        """
        a needle is clear if it is a sliding needle or if its associated slider needle is empty
        :param machine_state: not used by slider
        :return: True if needle is clear
        """
        return True

    def __add__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position + position)

    def __radd__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position + self.position)

    def __sub__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position - position)

    def __rsub__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position - self.position)

    def __mul__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position * position)

    def __rmul__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position * self.position)

    def __truediv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position / position)

    def __rtruediv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position / self.position)

    def __floordiv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position // position)

    def __rfloordiv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position // position)

    def __mod__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, self.position % position)

    def __rmod__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Slider_Needle(self.is_front, position % self.position)

    def __pow__(self, power, modulo=None):
        position = power
        if isinstance(power, Needle):
            position = power.position
        return Slider_Needle(self.is_front, self.position ** position)

    def __rpow__(self, power, modulo=None):
        position = power
        if isinstance(power, Needle):
            position = power.position
        return Slider_Needle(self.is_front, position ** self.position)
