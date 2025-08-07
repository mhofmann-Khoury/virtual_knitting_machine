"""Collection of Exceptions for error states that involve Yarn Carriers"""
from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier


class Yarn_Carrier_Exception(Knitting_Machine_Exception):

    def __init__(self, carrier_id: int | Yarn_Carrier, message: str) -> None:
        self.carrier_id: Yarn_Carrier | int = carrier_id
        super().__init__(message)


class Hooked_Carrier_Exception(Yarn_Carrier_Exception):
    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Cannot Hook {carrier_id} out because it is on the yarn inserting hook.")


class Inserting_Hook_In_Use_Exception(Yarn_Carrier_Exception):
    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Cannot bring carrier {carrier_id} out because the yarn inserting hook is in use.")


class Use_Inactive_Carrier_Exception(Yarn_Carrier_Exception):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Cannot use inactive yarn on carrier {carrier_id}.")


class Use_Cut_Yarn_Exception(Use_Inactive_Carrier_Exception):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id)


class Change_Active_Yarn_Exception(Yarn_Carrier_Exception):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Cannot change active yarn on carrier {carrier_id}.")


class Change_Active_Carrier_System_Exception(Yarn_Carrier_Exception):

    def __init__(self) -> None:
        super().__init__(-1, f"Cannot change active carrier system.")
