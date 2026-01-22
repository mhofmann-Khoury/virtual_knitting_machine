"""Comprehensive unit tests for the Yarn_Carrier class."""

import unittest

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Hooked_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier


class TestYarnCarrier(unittest.TestCase):
    """Test cases for the Yarn_Carrier class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.carrier_id = 5
        self.carrier = Yarn_Carrier(self.carrier_id)

    def test_initialization_default(self):
        """Test carrier initialization with default parameters."""
        carrier = Yarn_Carrier(10)

        self.assertEqual(carrier.carrier_id, 10)
        self.assertFalse(carrier.is_active)
        self.assertFalse(carrier.is_hooked)
        self.assertIsNone(carrier.slot_position)

    def test_set_position_none(self):
        """Test position property setter with None."""
        self.carrier.set_position(None)
        self.assertIsNone(self.carrier.slot_position)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

    def test_position_property_setter_front(self):
        """Test position property setter with integer."""
        self.carrier.is_active = True
        self.carrier.set_position(Needle(True, 15))
        self.assertEqual(self.carrier.needle, Needle(True, 15))
        self.assertEqual(self.carrier.slot_position, 15)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

    def test_position_property_setter_back(self):
        """Test position property setter with integer."""
        self.carrier.is_active = True
        self.carrier.set_position(Needle(False, 15))
        self.assertEqual(self.carrier.needle, Needle(False, 15))
        self.assertEqual(self.carrier.slot_position, 15)
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

    def test_outhook_hooked_carrier_raises_exception(self):
        """Test outhook method with hooked carrier raises exception."""
        self.carrier.is_hooked = True

        with self.assertRaises(Hooked_Carrier_Exception):
            self.carrier.outhook()

    def test_less_than_comparison_with_integer(self):
        """Test less than comparison with integer."""
        carrier_3 = Yarn_Carrier(3)
        carrier_7 = Yarn_Carrier(7)

        self.assertTrue(carrier_3 < 5)
        self.assertFalse(carrier_7 < 5)
        self.assertFalse(carrier_7 < 7)

    def test_less_than_comparison_with_carrier(self):
        """Test less than comparison with another carrier."""
        carrier_3 = Yarn_Carrier(3)
        carrier_7 = Yarn_Carrier(7)

        self.assertTrue(carrier_3 < carrier_7)
        self.assertFalse(carrier_7 < carrier_3)

    def test_hash_function(self):
        """Test hash function uses carrier ID."""
        carrier_10 = Yarn_Carrier(10)
        carrier_20 = Yarn_Carrier(20)

        self.assertEqual(hash(carrier_10), 10)
        self.assertEqual(hash(carrier_20), 20)

        # Same ID should have same hash
        another_carrier_10 = Yarn_Carrier(10)
        self.assertEqual(hash(carrier_10), hash(another_carrier_10))

    def test_integer_conversion(self):
        """Test integer conversion returns carrier ID."""
        carrier_15 = Yarn_Carrier(15)
        self.assertEqual(int(carrier_15), 15)

    def test_state_transitions_comprehensive(self):
        """Test comprehensive state transitions."""
        # Initial state
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.slot_position)

        # Bring in and hook
        self.carrier.inhook()
        self.assertTrue(self.carrier.is_active)
        self.assertTrue(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.slot_position)

        # Set position
        self.carrier.set_position(Needle(True, 10))
        self.assertEqual(self.carrier.slot_position, 10)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

        # Release hook
        self.carrier.releasehook()
        self.assertTrue(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertEqual(self.carrier.slot_position, 10)
        self.assertIs(self.carrier.last_direction, Carriage_Pass_Direction.Leftward)

        # Out
        self.carrier.out()
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.slot_position)
