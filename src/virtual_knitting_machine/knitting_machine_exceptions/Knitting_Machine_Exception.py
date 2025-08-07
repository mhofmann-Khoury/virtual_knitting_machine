"""Module containing the base class for Knitting Machine Exceptions."""


class Knitting_Machine_Exception(Exception):
    """
        Superclass for All exceptions that would put the virtual knitting machine in an error state
    """

    def __init__(self, message: str) -> None:
        self.message = f"{self.__class__.__name__}: {message}"
        super().__init__(self.message)
