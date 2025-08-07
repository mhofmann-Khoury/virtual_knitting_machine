""" A Module containing warnings related to the Yarn carrier system."""
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier


class Yarn_Carrier_Warning(Knitting_Machine_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier, message: str, ignore_instruction: bool = False) -> None:
        self.carrier_id: int | Yarn_Carrier = carrier_id
        super().__init__(message, ignore_instruction)


class Multiple_Yarn_Definitions_Warning(Yarn_Carrier_Warning):
    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Multiple definitions for yarn on carrier {carrier_id}", ignore_instruction=True)


class Release_Wrong_Carrier_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier, hooked_carrier_id: int | None | Yarn_Carrier) -> None:
        self.hooked_carrier_id: Yarn_Carrier | None | int = hooked_carrier_id
        current_carrier_statement = f"Carrier {self.hooked_carrier_id} is on Yarn-Inserting_Hook"
        if self.hooked_carrier_id is None:
            current_carrier_statement = f"No carrier is on the Yarn-Inserting Hook."
        super().__init__(carrier_id, f"Tried to release carrier {carrier_id} which is not on yarn-inserting hook.\n\t{current_carrier_statement}", ignore_instruction=True)


class Loose_Release_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier, loops_before_release: int, loose_loop_count: int) -> None:
        self.loops_before_release: int = loops_before_release
        self.loose_loop_count: int = loose_loop_count
        super().__init__(carrier_id, f"Released loose yarn on carrier {carrier_id} with {loops_before_release} stabling loops but requested {loose_loop_count}.")


class Defined_Active_Yarn_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Defined active yarn on carrier {carrier_id}", ignore_instruction=True)


class In_Active_Carrier_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Tried to bring in {carrier_id} but it is already active", ignore_instruction=True)


class In_Loose_Carrier_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Tried to bring in {carrier_id} but carrier is loose. Try in-hooking {carrier_id}", ignore_instruction=False)


class Out_Inactive_Carrier_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int | Yarn_Carrier) -> None:
        super().__init__(carrier_id, f"Cannot bring carrier {carrier_id} out because it is not active.", ignore_instruction=True)


class Duplicate_Carriers_In_Set(Yarn_Carrier_Warning):
    def __init__(self, carrier_id: int | Yarn_Carrier, carrier_set: list[int]):
        self.carrier_set: list[int] = carrier_set
        super().__init__(carrier_id, f"Removed last duplicate {carrier_id} form {carrier_set}", ignore_instruction=False)


class Long_Float_Warning(Yarn_Carrier_Warning):
    def __init__(self, carrier_id: int | Yarn_Carrier, prior_needle: Needle, next_needle: Needle, max_float_len: int):
        self.prior_needle: Needle = prior_needle
        self.next_needle: Needle = next_needle
        self.max_float_len: int = max_float_len
        super().__init__(carrier_id, f"Long float greater than {self.max_float_len} formed between {self.prior_needle} and {self.next_needle}.", ignore_instruction=False)
