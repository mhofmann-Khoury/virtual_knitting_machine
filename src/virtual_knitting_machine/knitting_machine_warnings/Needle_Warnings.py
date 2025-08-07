"""A module containing warnings related to needles."""
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Needle_Warning(Knitting_Machine_Warning):

    def __init__(self, needle: Needle, message: str) -> None:
        self.needle: Needle = needle
        super().__init__(message)


class Needle_Holds_Too_Many_Loops(Needle_Warning):

    def __init__(self, needle: Needle, max_loop_allowance: int) -> None:
        self.max_loop_allowance: int = max_loop_allowance
        super().__init__(needle, f"{needle} has reached maximum hold with loops {needle.held_loops} >= {max_loop_allowance}")


class Transfer_From_Empty_Needle(Needle_Warning):

    def __init__(self, needle: Needle) -> None:
        super().__init__(needle, f"Transferring from empty needle {needle}")


class Knit_on_Empty_Needle_Warning(Needle_Warning):
    def __init__(self, needle: Needle) -> None:
        super().__init__(needle, f"Knitting on empty needle {needle}")
