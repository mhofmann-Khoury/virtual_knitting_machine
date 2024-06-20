"""A Module containing the base class for Knitting Machine Warnings."""


class Knitting_Machine_Warning(RuntimeWarning):
    """
        Warnings about the state of the knitting machine that can be handled
    """

    def __init__(self, message: str, ignore_instructions: bool = False):
        ignore_str = ""
        if ignore_instructions:
            ignore_str = ". Ignoring Operation."
        self.message = f"\n\t{message}{ignore_str}"
        super().__init__(self.message)
