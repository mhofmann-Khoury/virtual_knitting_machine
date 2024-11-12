"""A module containing the class structures needed to define a Knitting Machine."""
from dataclasses import dataclass
from enum import Enum


class Knitting_Machine_Type(Enum):
    """An enumeration of supported Knitting Machine Types that be represented by this library."""
    SWG091N2 = "SWG091N2"

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))


class Knitting_Position(Enum):
    """The position of knitting operations on executed on this virtual machine."""
    Left = "Left"
    Right = "Right"
    Center = "Center"
    Keep = "Keep"

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))


@dataclass
class Knitting_Machine_Specification:
    """The specification of a knitting machine"""
    machine: Knitting_Machine_Type = Knitting_Machine_Type.SWG091N2
    gauge: int = 15
    position: Knitting_Position = Knitting_Position.Right
    carrier_count: int = 10
    needle_count: int = 540
    maximum_rack: int = 4
