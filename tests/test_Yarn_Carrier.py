"""Comprehensive unit tests for the Yarn_Carrier class."""

import unittest

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import (
    Violation,
    ViolationAction,
    ViolationResponse,
)


class TestYarnCarrier(unittest.TestCase):
    """Test cases for the Yarn_Carrier class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.machine = Knitting_Machine()
        self.carrier_id = 5
        self.carrier = self.machine.get_carrier(self.carrier_id)

    def test_initialization_default(self):
        """Test carrier initialization with default parameters."""
        carrier = self.machine.get_carrier(10)

        self.assertEqual(carrier.carrier_id, 10)
        self.assertFalse(carrier.is_active)
        self.assertFalse(carrier.is_hooked)
        self.assertFalse(carrier.position_on_bed.on_bed)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Rightward)

    def test_set_position_none(self):
        """Test position property setter with None."""
        self.machine.set_response_for(
            Violation.INACTIVE_CARRIER,
            ViolationResponse(ViolationAction.IGNORE, handle=False, proceed_with_operation=True),
        )
        self.carrier.set_position(None)
        self.assertFalse(self.carrier.position_on_bed.on_bed)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

    def test_position_property_setter_front(self):
        """Test position property setter with integer."""
        self.carrier.is_active = True
        self.carrier.set_position(self.machine.get_specified_needle(True, 15))
        self.assertEqual(self.carrier.slot_number, 15)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

    def test_position_property_setter_back(self):
        """Test position property setter with integer."""
        self.carrier.is_active = True
        self.carrier.set_position(self.machine.get_specified_needle(False, 15))
        self.assertEqual(self.carrier.slot_number, 15)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

    def test_bring_in_inactive_carrier(self):
        """Test bring_in method with inactive carrier."""
        self.assertFalse(self.carrier.is_active)

        self.carrier.bring_in()

        self.assertTrue(self.carrier.is_active)

    def test_bring_in_active_carrier_warns(self):
        """Test bring_in method with active carrier triggers warning."""
        self.carrier.is_active = True

        with self.assertWarns(In_Active_Carrier_Warning):
            self.carrier.bring_in()

        self.assertTrue(self.carrier.is_active)  # Should remain active

    def test_inhook_method(self):
        """Test inhook method activates and hooks carrier."""
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)

        self.carrier.inhook()

        self.assertTrue(self.carrier.is_active)
        self.assertTrue(self.carrier.is_hooked)

    def test_inhook_already_active_warns(self):
        """Test inhook method warns when carrier already active."""
        self.carrier.is_active = True

        with self.assertWarns(In_Active_Carrier_Warning):
            self.carrier.inhook()

        self.assertTrue(self.carrier.is_active)
        self.assertTrue(self.carrier.is_hooked)

    def test_releasehook_method(self):
        """Test releasehook method unhooks carrier."""
        self.carrier.is_hooked = True

        self.carrier.releasehook()

        self.assertFalse(self.carrier.is_hooked)

    def test_out_active_carrier(self):
        """Test out method with active carrier."""
        self.carrier.is_active = True

        self.carrier.out()

        self.assertFalse(self.carrier.is_active)

    def test_out_inactive_carrier_warns(self):
        """Test out method with inactive carrier triggers warning."""
        self.assertFalse(self.carrier.is_active)

        with self.assertWarns(Out_Inactive_Carrier_Warning):
            self.carrier.out()

        self.assertFalse(self.carrier.is_active)  # Should remain inactive

    def test_outhook_unhooked_carrier(self):
        """Test outhook method with unhooked carrier."""
        self.carrier.is_active = True
        self.assertFalse(self.carrier.is_hooked)

        self.carrier.outhook()

        self.assertFalse(self.carrier.is_active)

    def test_less_than_comparison_with_integer(self):
        """Test less than comparison with integer."""
        carrier_3 = self.machine.get_carrier(3)
        carrier_7 = self.machine.get_carrier(7)

        self.assertTrue(carrier_3 < 5)
        self.assertFalse(carrier_7 < 5)
        self.assertFalse(carrier_7 < 7)

    def test_less_than_comparison_with_carrier(self):
        """Test less than comparison with another carrier."""
        carrier_3 = self.machine.get_carrier(3)
        carrier_7 = self.machine.get_carrier(7)

        self.assertTrue(carrier_3 < carrier_7)
        self.assertFalse(carrier_7 < carrier_3)

    def test_hash_function(self):
        """Test hash function uses carrier ID."""
        carrier_10 = self.machine.get_carrier(10)
        carrier_20 = self.machine.get_carrier(6)

        self.assertEqual(hash(carrier_10), 10)
        self.assertEqual(hash(carrier_20), 6)

        # Same ID should have same hash
        another_carrier_10 = self.machine.get_carrier(10)
        self.assertEqual(hash(carrier_10), hash(another_carrier_10))

    def test_integer_conversion(self):
        """Test integer conversion returns carrier ID."""
        carrier_15 = self.machine.get_carrier(6)
        self.assertEqual(int(carrier_15), 6)

    def test_state_transitions_comprehensive(self):
        """Test comprehensive state transitions."""
        # Initial state
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertFalse(self.carrier.position_on_bed.on_bed)

        # Bring in and hook
        self.carrier.inhook()
        self.assertTrue(self.carrier.is_active)
        self.assertTrue(self.carrier.is_hooked)
        self.assertFalse(self.carrier.position_on_bed.on_bed)

        # Set position
        self.carrier.set_position(self.machine.get_specified_needle(True, 10))
        self.assertEqual(self.carrier.slot_number, 10)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

        # Release hook
        self.carrier.releasehook()
        self.assertTrue(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertEqual(self.carrier.slot_number, 10)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

        # Out
        self.carrier.out()
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertFalse(self.carrier.position_on_bed.on_bed)
