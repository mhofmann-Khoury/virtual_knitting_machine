"""A Module containing the base class for Knitting Machine Warnings."""


class Knitting_Machine_Warning(RuntimeWarning):
    """
        Warnings about the state of the knitting machine that can be handled
    """

    def __init__(self, message: str, ignore_instructions: bool = False) -> None:
        ignore_str = ""
        if ignore_instructions:
            ignore_str = ". Ignoring Operation."
        self.message = f"\n\t{self.__class__.__name__}: {message}{ignore_str}"
        super().__init__(self.message)
