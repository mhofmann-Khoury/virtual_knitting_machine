"""Module containing exceptions raised that involve racking."""

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception


class Max_Rack_Exception(Knitting_Machine_Exception):

    def __init__(self, racking: float, max_rack: float):
        self.max_rack = max_rack
        self.racking = racking
        super().__init__(f"Cannot perform racking of {racking}. Max rack allowed is {max_rack}")
