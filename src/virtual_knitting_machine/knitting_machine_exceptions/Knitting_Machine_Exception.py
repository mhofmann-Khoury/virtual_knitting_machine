"""Module containing the base class for Knitting Machine Exceptions."""


class Knitting_Machine_Exception(Exception):
    """
        Superclass for All exceptions that would put the virtual knitting machine in an error state
    """

    def __init__(self, message: str):
        self.message = f"Knitting Machine Exception: {message}"
        super().__init__(self.message)
