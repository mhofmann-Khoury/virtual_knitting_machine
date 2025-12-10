"""Comprehensive unit tests for the Yarn_Insertion_System class."""

import unittest
import warnings

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import (
    Hooked_Carrier_Exception,
    Inserting_Hook_In_Use_Exception,
    Use_Inactive_Carrier_Exception,
)
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    In_Active_Carrier_Warning,
    In_Loose_Carrier_Warning,
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import Yarn_Insertion_System


class TestYarnInsertionSystem(unittest.TestCase):
    """Test cases for the Yarn_Insertion_System class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock knitting machine
        self.machine = Knitting_Machine(Knitting_Machine_Specification(hook_size=5, maximum_float=20, carrier_count=5))
        self.system = self.machine.carrier_system

    def test_carrier_no_last_needle(self):
        self.system.inhook(1)
        self.assertIsNone(self.system[1].yarn.last_needle())
        self.assertTrue(self.system.yarn_is_loose(1))

    def test_initialization_default_carrier_count(self):
        """Test initialization with default carrier count."""
        system = Yarn_Insertion_System(self.machine)

        self.assertEqual(system.knitting_machine, self.machine)
        self.assertEqual(len(system.carriers), 10)  # Default count
        self.assertIsNone(system.hook_position)
        self.assertIsNone(system.hook_input_direction)
        self.assertFalse(system._searching_for_position)
        self.assertIsNone(system.hooked_carrier)

    def test_initialization_custom_carrier_count(self):
        """Test initialization with custom carrier count."""
        self.assertEqual(len(self.system.carriers), 5)

        # Verify carrier IDs are 1-based
        carrier_ids = [carrier.carrier_id for carrier in self.system.carriers]
        self.assertEqual(carrier_ids, [1, 2, 3, 4, 5])

    def test_searching_for_position_property_hook_available(self):
        """Test searching_for_position property when hook is available."""
        self.assertTrue(self.system.inserting_hook_available)
        self.assertFalse(self.system.searching_for_position)

    def test_searching_for_position_property_hook_in_use(self):
        """Test searching_for_position property when hook is in use."""
        self.system.inhook(1)
        self.system._searching_for_position = True

        self.assertFalse(self.system.inserting_hook_available)
        self.assertTrue(self.system.searching_for_position)

    def test_carrier_ids_property(self):
        """Test carrier_ids property."""
        carrier_ids = self.system.carrier_ids
        self.assertEqual(carrier_ids, [1, 2, 3, 4, 5])

    def test_inserting_hook_available_property_true(self):
        """Test inserting_hook_available property when hook is available."""
        self.assertIsNone(self.system.hooked_carrier)
        self.assertTrue(self.system.inserting_hook_available)

    def test_inserting_hook_available_property_false(self):
        """Test inserting_hook_available property when hook is in use."""
        self.system.inhook(1)
        self.assertFalse(self.system.inserting_hook_available)

    def test_active_carriers_property(self):
        """Test active_carriers property."""
        # Activate some carriers
        self.system.carriers[0].is_active = True
        self.system.carriers[2].is_active = True

        active_carriers = self.system.active_carriers
        self.assertEqual(len(active_carriers), 2)
        self.assertIn(self.system.carriers[0], active_carriers)
        self.assertIn(self.system.carriers[2], active_carriers)

    def test_conflicts_with_inserting_hook_no_hook(self):
        """Test conflicts_with_inserting_hook when hook is not active."""
        needle = Needle(True, 10)

        result = self.system.conflicts_with_inserting_hook(needle + 1)
        self.assertFalse(result)

    def test_conflicts_with_inserting_hook_leftward_conflict(self):
        """Test conflicts_with_inserting_hook with leftward direction conflict."""
        needle = Needle(True, 10)
        self.system.inhook(1)
        self.assertEqual(len(self.system.active_carriers), 1)
        self.assertTrue(self.system[1] in self.system.active_carriers)
        self.assertTrue(self.system[1].is_active)
        self.system.knitting_machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)

        result = self.system.conflicts_with_inserting_hook(needle + 1)
        self.assertTrue(result)

    def test_conflicts_with_inserting_hook_leftward_no_conflict(self):
        """Test conflicts_with_inserting_hook with leftward direction no conflict."""
        needle = Needle(True, 10)
        self.system.inhook(1)
        self.system.knitting_machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)

        result = self.system.conflicts_with_inserting_hook(needle)
        self.assertFalse(result)

    def test_missing_carriers_all_active(self):
        """Test missing_carriers when all carriers are active."""
        # Activate all carriers
        for carrier in self.system.carriers:
            carrier.is_active = True

        missing = self.system.missing_carriers([1, 2, 3])
        self.assertEqual(missing, [])

    def test_missing_carriers_some_inactive(self):
        """Test missing_carriers when some carriers are inactive."""
        # Activate only carrier 2
        self.system.carriers[1].is_active = True  # Carrier ID 2

        missing = self.system.missing_carriers([1, 2, 3])
        self.assertEqual(set(missing), {1, 3})

    def test_is_active_empty_list(self):
        """Test is_active with empty list returns True."""
        result = self.system.is_active([])
        self.assertTrue(result)

    def test_is_active_all_active(self):
        """Test is_active when all carriers are active."""
        self.system.carriers[0].is_active = True
        self.system.carriers[1].is_active = True

        result = self.system.is_active([1, 2])
        self.assertTrue(result)

    def test_is_active_some_inactive(self):
        """Test is_active when some carriers are inactive."""
        self.system.carriers[0].is_active = True
        # Carrier 2 remains inactive

        result = self.system.is_active([1, 2])
        self.assertFalse(result)

    def test_bring_in_active_carrier_warns(self):
        """Test bring_in with active carrier triggers warning."""
        self.system.inhook(1)

        with self.assertWarns(In_Active_Carrier_Warning):
            self.system.bring_in(1)

    def test_bring_in_loose_carrier_warns(self):
        """Test bring_in with loose carrier triggers warning."""
        with self.assertWarns(In_Loose_Carrier_Warning):
            self.system.bring_in(1)

    def test_inhook_hook_in_use_different_carrier_raises_exception(self):
        """Test inhook when hook is in use by different carrier raises exception."""
        self.system._hooked_carrier = self.system.carriers[1]  # Carrier 2 is hooked

        with self.assertRaises(Inserting_Hook_In_Use_Exception):
            self.system.inhook(1)  # Try to hook carrier 1

    def test_inhook_same_carrier_already_hooked(self):
        """Test inhook when same carrier is already hooked."""
        carrier = self.system.carriers[0]
        self.system._hooked_carrier = carrier

        self.system.inhook(1)

        # Should not raise exception, should proceed
        self.assertEqual(self.system.hooked_carrier, carrier)

    def test_releasehook_no_hooked_carrier(self):
        """Test releasehook when no carrier is hooked."""
        self.system.releasehook()

        # Should not raise exception
        self.assertIsNone(self.system.hooked_carrier)

    def test_out_inactive_carrier_warns(self):
        """Test out with inactive carrier triggers warning."""
        carrier = self.system.carriers[0]
        carrier.is_active = False

        with self.assertWarns(Out_Inactive_Carrier_Warning):
            self.system.out(1)

    def test_out_hooked_carrier_raises_exception(self):
        """Test out with hooked carrier raises exception."""
        carrier = self.system.carriers[0]
        carrier.is_active = True
        carrier.is_hooked = True

        with self.assertRaises(Hooked_Carrier_Exception):
            self.system.out(1)

    def test_outhook_hooked_carrier_raises_exception(self):
        """Test outhook with hooked carrier raises exception."""
        carrier = self.system.carriers[0]
        carrier.is_hooked = True

        with self.assertRaises(Hooked_Carrier_Exception):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", Out_Inactive_Carrier_Warning)
                self.system.outhook(1)

    def test_make_loops_inactive_carrier_raises_exception(self):
        """Test make_loops with inactive carrier raises exception."""
        with self.assertRaises(Use_Inactive_Carrier_Exception):
            self.system.make_loops([1], Needle(True, 1), Carriage_Pass_Direction.Leftward)

    def test_getitem_single_integer(self):
        """Test __getitem__ with single integer."""
        carrier = self.system[1]
        self.assertEqual(carrier.carrier_id, 1)

    def test_getitem_yarn_carrier_object(self):
        """Test __getitem__ with Yarn_Carrier object."""
        result = self.system[Yarn_Carrier(3)]
        self.assertEqual(result.carrier_id, 3)

    def test_getitem_yarn_carrier_set(self):
        """Test __getitem__ with Yarn_Carrier_Set."""
        result = self.system[Yarn_Carrier_Set([1, 3, 5])]
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].carrier_id, 1)
        self.assertEqual(result[2].carrier_id, 5)

    def test_getitem_list_single_item(self):
        """Test __getitem__ with single-item list returns single carrier."""
        result = self.system[[2]]
        self.assertEqual(result.carrier_id, 2)

    def test_getitem_list_multiple_items(self):
        """Test __getitem__ with multiple-item list returns list of carriers."""
        result = self.system[[1, 3, 4]]
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].carrier_id, 1)
        self.assertEqual(result[1].carrier_id, 3)
        self.assertEqual(result[2].carrier_id, 4)

    def test_getitem_invalid_carrier_id_raises_error(self):
        """Test __getitem__ with invalid carrier ID raises KeyError."""
        with self.assertRaises(KeyError):
            _ = self.system[0]  # Below valid range

        with self.assertRaises(KeyError):
            _ = self.system[10]  # Above valid range

    def test_carriers_are_1_indexed(self):
        """Test that carriers are 1-indexed internally."""
        # Carrier ID 1 should be at index 0
        carrier_1 = self.system[1]
        self.assertEqual(carrier_1.carrier_id, 1)
        self.assertIs(carrier_1, self.system.carriers[0])

        # Carrier ID 5 should be at index 4
        carrier_5 = self.system[5]
        self.assertEqual(carrier_5.carrier_id, 5)
        self.assertIs(carrier_5, self.system.carriers[4])

    def test_comprehensive_hook_workflow(self):
        """Test comprehensive hook workflow."""
        carrier = self.system.carriers[0]

        # Initial state
        self.assertTrue(self.system.inserting_hook_available)
        self.assertIsNone(self.system.hooked_carrier)

        # Hook carrier
        self.system.inhook(1)
        self.assertFalse(self.system.inserting_hook_available)
        self.assertEqual(self.system.hooked_carrier, carrier)
        self.assertTrue(self.system._searching_for_position)

        # Release hook
        self.system.releasehook()
        self.assertTrue(self.system.inserting_hook_available)
        self.assertIsNone(self.system.hooked_carrier)
        self.assertFalse(self.system._searching_for_position)
