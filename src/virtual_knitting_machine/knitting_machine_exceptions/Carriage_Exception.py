from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class Carriage_Exception(Knitting_Machine_Exception):
    def __init__(self, carriage, message: str):
        self.carriage = carriage
        super().__init__(message)


class Carriage_Cannot_Reach_Position_In_Given_Direction(Carriage_Exception):

    def __init__(self, carriage, current_position:int, target_position: int, given_direction: Carriage_Pass_Direction):
        self.current_position = current_position
        self.given_direction = given_direction
        self.target_position = target_position
        super().__init__(carriage, f"Cannot move from {current_position} to {target_position} in direction {given_direction}.")


class Carriage_Cannot_Move_In_Direction(Carriage_Exception):

    def __init__(self, carriage, given_direction: Carriage_Pass_Direction):
        self.given_direction = given_direction
        super().__init__(carriage, f"Cannot move to in {given_direction} direction from carriage position {carriage.current_needle_position}")
