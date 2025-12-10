"""A module containing the base class for knitting machine warnings.
This module provides the foundational warning class that all knitting machine-specific warnings inherit from,
standardizing warning message formatting and handling behavior across the virtual knitting machine system."""

import inspect


def get_user_warning_stack_level_from_virtual_knitting_machine_package() -> int:
    """
    Returns:
        int: The stack level pointing to first caller outside this library.
    """
    # Get the root package name
    package_name = __name__.split(".")[0]  # e.g., "virtual_knitting_machine"

    frame = inspect.currentframe()
    if frame is None:  # Some Python implementations might not support frames
        return 2  # Reasonable default

    try:
        stack_level = 0
        while frame:
            # Get the module name from the frame's globals
            frame_module = frame.f_globals.get("__name__", "")

            # Check if this frame is from our package
            if not frame_module.startswith(package_name + ".") and frame_module != package_name:
                # This frame is outside our package!
                return stack_level

            stack_level += 1
            frame = frame.f_back

        return stack_level if stack_level > 0 else 2
    finally:
        # Clean up frame reference to avoid reference cycles
        del frame


class Knitting_Machine_Warning(RuntimeWarning):
    """Base class for warnings about the state of the knitting machine that can be handled gracefully.
    This class provides standardized warning message formatting and supports configurable instruction ignoring behavior for different types of machine state issues.
    """

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
