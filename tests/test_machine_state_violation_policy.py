from unittest import TestCase

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Hooked_Carrier_Exception
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Passed_Machine_Error_Warning
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import (
    Knitting_Machine_Error_Policy,
)
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import (
    Violation,
    ViolationAction,
    ViolationResponse,
)


class TestMachine_State_With_Policy(TestCase):

    def setUp(self):
        self.policy = Knitting_Machine_Error_Policy()
        self.policy.set_response_for(
            Violation.RACKING_OUT_OF_RANGE,
            ViolationResponse(ViolationAction.WARN, handle=False, proceed_with_operation=True),
        )
        self.policy.set_response_for(
            Violation.INSERTING_HOOK_IN_USE,
            ViolationResponse(ViolationAction.WARN, handle=True, proceed_with_operation=True),
        )
        spec = Knitting_Machine_Specification(maximum_rack=1)
        self.machine: Knitting_Machine = Knitting_Machine(machine_specification=spec, violation_policy=self.policy)

    def test_bad_rack(self):
        with self.assertWarns(Passed_Machine_Error_Warning):
            self.machine.rack = (
                2  # Should raise a warning because the maximum rack was set to 1 but the policy is set ot warn.
            )
        self.assertEqual(
            2, self.machine.rack
        )  # Since policy is set to continue with the instruction, the rack should get set to the risky value anyway.

    def test_bad_inhook(self):
        self.machine.in_hook(1)
        with self.assertWarns(Passed_Machine_Error_Warning):
            self.machine.in_hook(2)  # Should warn based on policy
        self.assertTrue(
            2, self.machine.carrier_system.hooked_carrier.carrier_id
        )  # The hooked carrier should change to carrier 2

    def test_bad_out(self):
        self.machine.in_hook(1)
        try:
            self.machine.out(1)
            self.fail("Expected to fail since policy default is set not handle")
        except Hooked_Carrier_Exception as _e:
            pass
        self.policy.set_response_for(
            Violation.HOOKED_CARRIER, ViolationResponse(ViolationAction.WARN, handle=True, proceed_with_operation=True)
        )
        with self.assertWarns(Passed_Machine_Error_Warning):
            self.machine.out(1)
        self.assertIsNone(self.machine.carrier_system.hooked_carrier)
        self.assertIs(0, len(self.machine.carrier_system.active_carriers))
