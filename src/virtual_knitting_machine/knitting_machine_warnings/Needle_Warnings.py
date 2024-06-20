"""A module containing warnings related to needles."""
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning


class Needle_Warning(Knitting_Machine_Warning):

    def __init__(self, needle, message: str):
        self.needle = needle
        super().__init__(message)


class Needle_Holds_Too_Many_Loops(Needle_Warning):

    def __init__(self, needle):
        super().__init__(needle, f"{needle} has reached maximum hold with loops {needle.held_loops}")


class Transfer_From_Empty_Needle(Needle_Warning):

    def __init__(self, needle):
        super().__init__(needle, f"Transferring from empty needle {needle}")


class Knit_on_Empty_Needle_Warning(Needle_Warning):
    def __init__(self, needle):
        super().__init__(needle, f"Knitting on empty needle {needle}")
