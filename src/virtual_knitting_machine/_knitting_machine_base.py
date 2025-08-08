"""Base class for the Knitting Machine. Used to resolve circular import errors."""

from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification


class _Base_Knitting_Machine:
    """Base class for the Knitting Machine. Used to resolve circular import errors."""

    def __init__(self, machine_specification: Knitting_Machine_Specification = Knitting_Machine_Specification(), knit_graph: Knit_Graph | None = None):
        """Initializes the base of a knitting machine with the given machine specification.
        Args:
            machine_specification (Knitting_Machine_Specification): The specification to build this machine from.
            knit_graph (Knit_Graph | None): The knit graph to start this machine with. If None, an empty knit graph is created.
        """
        self.machine_specification: Knitting_Machine_Specification = machine_specification
        if knit_graph is None:
            knit_graph = Knit_Graph()
        self.knit_graph: Knit_Graph = knit_graph

    @property
    def needle_count(self) -> int:
        """Get the needle width of the machine.

        Returns:
            int: The needle width of the machine.
        """
        return int(self.machine_specification.needle_count)

    @property
    def max_rack(self) -> int:
        """Get the maximum distance that the machine can rack.

        Returns:
            int: The maximum distance that the machine can rack.
        """
        return int(self.machine_specification.maximum_rack)

    def __len__(self) -> int:
        """Get the needle bed width of the machine.

        Returns:
            int: The needle bed width of the machine.
        """
        return self.needle_count
