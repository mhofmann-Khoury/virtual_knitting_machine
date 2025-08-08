"""Comprehensive unit tests for the Yarn_Carrier class."""
import unittest
import warnings

from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Change_Active_Yarn_Exception, Hooked_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import In_Active_Carrier_Warning, Out_Inactive_Carrier_Warning
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
        self.assertIsNone(carrier.position)

    def test_yarn_property_getter(self):
        """Test yarn property getter."""
        self.assertEqual(self.carrier.yarn, self.carrier._yarn)

    def test_yarn_property_setter_active_carrier_raises_exception(self):
        """Test yarn property setter raises exception when carrier is active."""
        self.carrier.is_active = True

        yarn_props = Yarn_Properties()
        with self.assertRaises(Change_Active_Yarn_Exception):
            self.carrier.yarn = yarn_props

    def test_position_property_getter(self):
        """Test position property getter."""
        self.assertIsNone(self.carrier.position)

        self.carrier._position = 10
        self.assertEqual(self.carrier.position, 10)

    def test_position_property_setter_none(self):
        """Test position property setter with None."""
        self.carrier.position = None
        self.assertIsNone(self.carrier.position)

    def test_position_property_setter_integer(self):
        """Test position property setter with integer."""
        self.carrier.position = 15
        self.assertEqual(self.carrier.position, 15)

    def test_position_property_setter_needle(self):
        """Test position property setter with needle object."""
        needle = Needle(is_front=True, position=25)

        self.carrier.position = needle
        self.assertEqual(self.carrier.position, 25)

    def test_is_active_property_getter(self):
        """Test is_active property getter."""
        self.assertFalse(self.carrier.is_active)

        self.carrier._is_active = True
        self.assertTrue(self.carrier.is_active)

    def test_is_active_property_setter_true(self):
        """Test is_active property setter with True."""
        self.carrier.is_active = True
        self.assertTrue(self.carrier._is_active)

    def test_is_active_property_setter_false(self):
        """Test is_active property setter with False clears hook and position."""
        self.carrier._is_hooked = True
        self.carrier._position = 10

        self.carrier.is_active = False

        self.assertFalse(self.carrier._is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.position)

    def test_is_hooked_property_getter(self):
        """Test is_hooked property getter."""
        self.assertFalse(self.carrier.is_hooked)

        self.carrier._is_hooked = True
        self.assertTrue(self.carrier.is_hooked)

    def test_is_hooked_property_setter(self):
        """Test is_hooked property setter."""
        self.carrier.is_hooked = True
        self.assertTrue(self.carrier._is_hooked)

        self.carrier.is_hooked = False
        self.assertFalse(self.carrier._is_hooked)

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

    def test_carrier_id_property(self):
        """Test carrier_id property."""
        self.assertEqual(self.carrier.carrier_id, self.carrier_id)

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
        self.assertIsNone(self.carrier.position)

        # Bring in and hook
        self.carrier.inhook()
        self.assertTrue(self.carrier.is_active)
        self.assertTrue(self.carrier.is_hooked)

        # Set position
        self.carrier.position = 10
        self.assertEqual(self.carrier.position, 10)

        # Release hook
        self.carrier.releasehook()
        self.assertTrue(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertEqual(self.carrier.position, 10)

        # Out
        self.carrier.out()
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.position)

    def test_deactivation_clears_all_states(self):
        """Test that deactivating carrier clears all states."""
        # Set up active, hooked carrier with position
        self.carrier._is_active = True
        self.carrier._is_hooked = True
        self.carrier._position = 15

        # Deactivate
        self.carrier.is_active = False

        # All states should be cleared
        self.assertFalse(self.carrier.is_active)
        self.assertFalse(self.carrier.is_hooked)
        self.assertIsNone(self.carrier.position)

    def test_position_setting_with_float_conversion(self):
        """Test position setting converts float to int."""
        self.carrier.position = 12.7
        self.assertEqual(self.carrier.position, 12)

    def test_multiple_carriers_independence(self):
        """Test that multiple carriers maintain independent states."""
        carrier1 = Yarn_Carrier(1)
        carrier2 = Yarn_Carrier(2)

        # Activate only carrier1
        carrier1.is_active = True
        carrier1.position = 10

        # Verify independence
        self.assertTrue(carrier1.is_active)
        self.assertFalse(carrier2.is_active)
        self.assertEqual(carrier1.position, 10)
        self.assertIsNone(carrier2.position)

    def test_hash_consistency_across_operations(self):
        """Test hash remains consistent across operations."""
        initial_hash = hash(self.carrier)

        # Perform various operations
        self.carrier.bring_in()
        self.carrier.position = 5
        self.carrier.is_hooked = True
        self.carrier.out()

        # Hash should remain the same (based only on carrier_id)
        self.assertEqual(hash(self.carrier), initial_hash)

    def test_comparison_edge_cases(self):
        """Test comparison edge cases."""
        carrier_0 = Yarn_Carrier(0)
        carrier_negative = Yarn_Carrier(-1)

        self.assertTrue(carrier_negative < carrier_0)
        self.assertTrue(carrier_0 < self.carrier)  # self.carrier has ID 5

    def test_warning_messages_contain_carrier_id(self):
        """Test that warning messages contain the carrier ID."""
        self.carrier.is_active = True

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            self.carrier.bring_in()

            self.assertEqual(len(warning_list), 1)
            warning_instance = warning_list[0].message
            self.assertEqual(warning_instance.carrier_id, self.carrier_id)

    def test_exception_messages_contain_carrier_id(self):
        """Test that exception messages contain the carrier ID."""
        self.carrier.is_active = True

        try:
            self.carrier.yarn = Yarn_Properties()
            self.fail("Expected Change_Active_Yarn_Exception")
        except Change_Active_Yarn_Exception as e:
            self.assertEqual(e.carrier_id, self.carrier_id)
