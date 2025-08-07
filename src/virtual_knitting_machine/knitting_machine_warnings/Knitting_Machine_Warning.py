"""A module containing the base class for knitting machine warnings.
This module provides the foundational warning class that all knitting machine-specific warnings inherit from,
standardizing warning message formatting and handling behavior across the virtual knitting machine system."""


class Knitting_Machine_Warning(RuntimeWarning):
    """Base class for warnings about the state of the knitting machine that can be handled gracefully.
    This class provides standardized warning message formatting and supports configurable instruction ignoring behavior for different types of machine state issues."""

    def __init__(self, message: str, ignore_instructions: bool = False) -> None:
        """Initialize a knitting machine warning with formatted message.

        Args:
            message (str): The descriptive warning message about the machine state issue.
            ignore_instructions (bool, optional): Whether this warning indicates that the operation should be ignored. Defaults to False.
        """
        ignore_str = ""
        if ignore_instructions:
            ignore_str = ". Ignoring Operation."
        self.message = f"\n\t{self.__class__.__name__}: {message}{ignore_str}"
        super().__init__(self.message)
