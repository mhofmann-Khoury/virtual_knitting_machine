"""A Module containing warnings related to Yarn Carriers."""
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Yarn_Carrier_Warning


class Mismatched_Releasehook_Warning(Yarn_Carrier_Warning):

    def __init__(self, carrier_id: int):
        super().__init__(carrier_id,
                         f"Requested Releasehook with {carrier_id} but that was not on hook. Releasing existing yarn",
                         ignore_instruction=False)
