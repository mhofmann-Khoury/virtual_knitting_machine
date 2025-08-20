"""A module containing the class structures needed to define a knitting machine specification.

This module provides enumerations for machine types and knitting positions,
as well as a dataclass specification that defines all the parameters and constraints for configuring a virtual knitting machine.
"""
from dataclasses import dataclass
from enum import Enum


class Knitting_Machine_Type(Enum):
    """An enumeration of supported knitting machine types that can be represented by this library.

    Currently, supports the SWG091N2 whole garment knitting machine model with potential for additional machine types in the future.
    """
    SWG091N2 = "SWG091N2"

    def __str__(self) -> str:
        """Return string representation of the machine type.

        Returns:
            str: The name of the machine type.
        """
        return self.name

    def __repr__(self) -> str:
        """Return string representation of the machine type.

        Returns:
            str: String representation of the machine type.
        """
        return str(self)

    def __hash__(self) -> int:
        """Return hash value for the machine type.

        Returns:
            int: Hash value based on string representation.
        """
        return hash(str(self))


class Knitting_Position(Enum):
    """The position configuration for knitting operations executed on the virtual machine.

    This enumeration defines where knitting operations are positioned on the machine bed,
    affecting how the machine interprets needle positions and carriage movements.
    """
    Left = "Left"  # Notes that the pattern will be positioned starting on te left most needle of the machine.
    Right = "Right"  # Notes that the pattern will be positioned ending on the rightmost needle of the machine.
    Center = "Center"  # Centers the pattern on the needle beds.
    Keep = "Keep"  # Notes that the pattern will be knit on exactly the needles specified.

    def __str__(self) -> str:
        """Return string representation of the knitting position.

        Returns:
            str: The name of the knitting position.
        """
        return self.name

    def __repr__(self) -> str:
        """Return string representation of the knitting position.

        Returns:
            str: String representation of the knitting position.
        """
        return str(self)

    def __hash__(self) -> int:
        """Return hash value for the knitting position.

        Returns:
            int: Hash value based on string representation.
        """
        return hash(str(self))


@dataclass
class Knitting_Machine_Specification:
    """The complete specification of a knitting machine including machine type, physical constraints, and operational parameters.

    This dataclass defines all the configurable parameters that determine machine capabilities,
    limitations, and behavior during knitting operations.
    """
    machine: Knitting_Machine_Type = Knitting_Machine_Type.SWG091N2  #: The type of knitting machine being represented
    gauge: int = 15  #: The gauge of the knitting machine needles
    position: Knitting_Position = Knitting_Position.Right  #: The positioning configuration for knitting operations
    carrier_count: int = 10  #: Number of yarn carriers available on the machine
    needle_count: int = 540  #: Total number of needles on each bed of the machine
    maximum_rack: int = 4  #: Maximum racking distance the machine can achieve
    maximum_float: int = 20  #: Maximum float length allowed (for future long float warnings)
    maximum_loop_hold: int = 4  #: Maximum number of loops a single needle can hold
    hook_size: int = 5  #: Size of the yarn insertion hook in needle positions
