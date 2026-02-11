"""A module containing the class structures needed to define a knitting machine specification.

This module provides enumerations for machine types and knitting positions,
as well as a dataclass specification that defines all the parameters and constraints for configuring a virtual knitting machine.
"""

from dataclasses import dataclass
from enum import Enum

from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


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


@dataclass(frozen=True)
class Knitting_Machine_Specification:
    """The complete specification of a knitting machine including machine type, physical constraints, and operational parameters.

    This dataclass defines all the configurable parameters that determine machine capabilities,
    limitations, and behavior during knitting operations.
    """

    machine: Knitting_Machine_Type = (
        Knitting_Machine_Type.SWG091N2
    )  # Knitting_Machine_Type: The type of knitting machine being represented
    gauge: int = 15  # int: The gauge of the knitting machine needles
    position: Knitting_Position = (
        Knitting_Position.Right
    )  # Knitting_Position: The positioning configuration for knitting operations
    carrier_count: int = 10  # int: Number of yarn carriers available on the machine
    needle_count: int = 540  # int: Total number of needles on each bed of the machine
    maximum_rack: int = 4  # int: Maximum racking distance the machine can achieve
    maximum_float: int = 20  # int: Maximum float length allowed (for future long float warnings)
    maximum_loop_hold: int = 4  # int: Maximum number of loops a single needle can hold
    hook_size: int = 5  # int: Size of the yarn insertion hook in needle positions
    carrier_colors: tuple[str, ...] = (
        "firebrick",
        "navy",
        "darkgreen",
        "indigo",
        "darkgoldenrod",
        "saddlebrown",
        "darkcyan",
        "purple",
        "darkorange",
        "darkslateblue",
    )
    """tuple[str, ...]: A tuple containing the default names of colors to assign to yarns based on the carrier id."""
    loop_class: type[Machine_Knit_Loop] = Machine_Knit_Loop
    # yarn_class: type[Machine_Knit_Yarn] = Machine_Knit_Yarn[Machine_Knit_Loop]

    def get_yarn_color(self, carrier_id: int) -> str:
        """
        Args:
            carrier_id (int): The carrier id of the carrier.

        Returns:
            str: A string for a color to assign to the yarn of a carrier.

        Notes:
            If the carrier id is greater than the given number of carrier colors, black will be the carrier color.
        """
        if carrier_id > 0:
            carrier_id -= 1
        if carrier_id < len(self.carrier_colors):
            return self.carrier_colors[carrier_id]
        else:
            return "black"
