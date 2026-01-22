"""Comprehensive unit tests for the Yarn_Carrier_Set class."""

import unittest
import warnings

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Duplicate_Carriers_In_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import Yarn_Insertion_System


class TestYarnCarrierSet(unittest.TestCase):
    """Test cases for the Yarn_Carrier_Set class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # self.mock_carrier_system = Mock()
        self.carrier_system = Yarn_Insertion_System(Knitting_Machine())

    def test_initialization_single_integer(self):
        """Test initialization with single integer."""
        carrier_set = Yarn_Carrier_Set(5)

        self.assertEqual(len(carrier_set.carrier_ids), 1)
        self.assertEqual(carrier_set.carrier_ids[0], 5)
        self.assertFalse(carrier_set.many_carriers)

    def test_initialization_single_carrier(self):
        """Test initialization with single Yarn_Carrier object."""
        carrier = Yarn_Carrier(10)

        carrier_set = Yarn_Carrier_Set(carrier)

        self.assertEqual(len(carrier_set.carrier_ids), 1)
        self.assertEqual(carrier_set.carrier_ids[0], 10)

    def test_initialization_list_of_integers(self):
        """Test initialization with list of integers."""
        carrier_set = Yarn_Carrier_Set([1, 3, 5, 7])

        self.assertEqual(len(carrier_set.carrier_ids), 4)
        self.assertEqual(carrier_set.carrier_ids, [1, 3, 5, 7])
        self.assertTrue(carrier_set.many_carriers)

    def test_initialization_list_of_carriers(self):
        """Test initialization with list of Yarn_Carrier objects."""
        carriers = []
        for i in [2, 4, 6]:
            carrier = Yarn_Carrier(i)
            carriers.append(carrier)

        carrier_set = Yarn_Carrier_Set(carriers)

        self.assertEqual(len(carrier_set.carrier_ids), 3)
        self.assertEqual(carrier_set.carrier_ids, [2, 4, 6])

    def test_initialization_mixed_list(self):
        """Test initialization with mixed list of integers and carriers."""
        carrier = Yarn_Carrier(3)

        carrier_set = Yarn_Carrier_Set([2, carrier, 12])

        self.assertEqual(len(carrier_set.carrier_ids), 3)
        self.assertEqual(carrier_set.carrier_ids, [2, 3, 12])

    def test_initialization_with_duplicates_warns(self):
        """Test initialization with duplicates triggers warning and removes duplicates."""
        with self.assertWarns(Duplicate_Carriers_In_Set):
            carrier_set = Yarn_Carrier_Set([1, 3, 1, 5, 3])

        # Should only keep unique values
        self.assertEqual(len(carrier_set.carrier_ids), 3)
        self.assertEqual(set(carrier_set.carrier_ids), {1, 3, 5})

    def test_carrier_ids_property(self):
        """Test carrier_ids property."""
        carrier_set = Yarn_Carrier_Set([10, 20, 30])

        self.assertEqual(carrier_set.carrier_ids, [10, 20, 30])
        # Should return a reference to the actual list
        self.assertIs(carrier_set.carrier_ids, carrier_set._carrier_ids)

    def test_many_carriers_property_single(self):
        """Test many_carriers property with single carrier."""
        carrier_set = Yarn_Carrier_Set(5)
        self.assertFalse(carrier_set.many_carriers)

    def test_many_carriers_property_multiple(self):
        """Test many_carriers property with multiple carriers."""
        carrier_set = Yarn_Carrier_Set([1, 2])
        self.assertTrue(carrier_set.many_carriers)

    def test_get_carriers_single_carrier_returned(self):
        """Test get_carriers method when system returns single carrier."""
        carrier_set = Yarn_Carrier_Set(5)

        carriers = carrier_set.get_carriers(self.carrier_system)

        self.assertEqual(len(carriers), 1)
        self.assertEqual(carriers[0], 5)

    def test_get_carriers_multiple_carriers_returned(self):
        """Test get_carriers method when system returns multiple carriers."""
        carrier_set = Yarn_Carrier_Set([1, 2, 3])

        mock_carriers = [i for i in range(1, 4)]

        carriers = carrier_set.get_carriers(self.carrier_system)

        self.assertEqual(len(carriers), 3)
        for m, c in zip(mock_carriers, carriers):
            self.assertEqual(m, c.carrier_id)

    def test_string_representation_single_carrier(self):
        """Test string representation with single carrier."""
        carrier_set = Yarn_Carrier_Set(5)

        self.assertEqual(str(carrier_set), "5")
        self.assertEqual(repr(carrier_set), "5")

    def test_string_representation_multiple_carriers(self):
        """Test string representation with multiple carriers."""
        carrier_set = Yarn_Carrier_Set([1, 3, 5])

        self.assertEqual(str(carrier_set), "1 3 5")
        self.assertEqual(repr(carrier_set), "1 3 5")

    def test_hash_single_carrier(self):
        """Test hash function with single carrier."""
        carrier_set = Yarn_Carrier_Set(10)

        self.assertEqual(hash(carrier_set), 10)

    def test_hash_multiple_carriers(self):
        """Test hash function with multiple carriers."""
        carrier_set = Yarn_Carrier_Set([1, 2, 3])

        # Should hash the string representation
        expected_hash = hash("1 2 3")
        self.assertEqual(hash(carrier_set), expected_hash)

    def test_equality_with_none(self):
        """Test equality comparison with None."""
        carrier_set = Yarn_Carrier_Set(5)

        self.assertFalse(carrier_set is None)
        self.assertNotEqual(carrier_set, None)

    def test_equality_with_single_integer(self):
        """Test equality comparison with single integer."""
        carrier_set = Yarn_Carrier_Set(5)

        self.assertTrue(carrier_set == 5)
        self.assertFalse(carrier_set == 3)

    def test_equality_with_yarn_carrier(self):
        """Test equality comparison with Yarn_Carrier."""
        carrier_set = Yarn_Carrier_Set(8)

        carrier = Yarn_Carrier(8)

        self.assertTrue(carrier_set == carrier)

    def test_equality_multiple_carriers_wrong_length(self):
        """Test equality fails when lengths don't match."""
        carrier_set = Yarn_Carrier_Set([1, 2, 3])

        self.assertFalse(carrier_set == [1, 2])
        self.assertFalse(carrier_set == [1, 2, 3, 4])

    def test_equality_with_list(self):
        """Test equality comparison with list."""
        carrier_set = Yarn_Carrier_Set([1, 3, 5])

        self.assertTrue(carrier_set == [1, 3, 5])

    def test_equality_with_carrier_set(self):
        """Test equality comparison with another carrier set."""
        carrier_set1 = Yarn_Carrier_Set([1, 2, 3])
        carrier_set2 = Yarn_Carrier_Set([1, 2, 3])
        carrier_set3 = Yarn_Carrier_Set([1, 2, 4])

        self.assertTrue(carrier_set1 == carrier_set2)
        self.assertFalse(carrier_set1 == carrier_set3)

    def test_iteration(self):
        """Test iteration over carrier IDs."""
        carrier_set = Yarn_Carrier_Set([2, 4, 6])

        ids = list(carrier_set)
        self.assertEqual(ids, [2, 4, 6])

    def test_getitem_with_integer_index(self):
        """Test __getitem__ with integer index."""
        carrier_set = Yarn_Carrier_Set([10, 20, 30])

        self.assertEqual(carrier_set[0], 10)
        self.assertEqual(carrier_set[1], 20)
        self.assertEqual(carrier_set[2], 30)
        self.assertEqual(carrier_set[-1], 30)

    def test_getitem_with_slice(self):
        """Test __getitem__ with slice."""
        carrier_set = Yarn_Carrier_Set([10, 20, 30, 40])

        self.assertEqual(carrier_set[1:3], [20, 30])
        self.assertEqual(carrier_set[:2], [10, 20])
        self.assertEqual(carrier_set[2:], [30, 40])

    def test_len_method(self):
        """Test __len__ method."""
        empty_set = Yarn_Carrier_Set([])
        single_set = Yarn_Carrier_Set(5)
        multi_set = Yarn_Carrier_Set([1, 2, 3, 4])

        self.assertEqual(len(empty_set), 0)
        self.assertEqual(len(single_set), 1)
        self.assertEqual(len(multi_set), 4)

    def test_contains_with_integer(self):
        """Test __contains__ with integer."""
        carrier_set = Yarn_Carrier_Set([2, 4, 6, 8])

        self.assertTrue(2 in carrier_set)
        self.assertTrue(6 in carrier_set)
        self.assertFalse(1 in carrier_set)
        self.assertFalse(5 in carrier_set)

    def test_contains_with_yarn_carrier(self):
        """Test __contains__ with Yarn_Carrier object."""
        carrier_set = Yarn_Carrier_Set([3, 6, 9])

        carrier_in = Yarn_Carrier(6)
        carrier_out = Yarn_Carrier(5)

        self.assertTrue(carrier_in in carrier_set)
        self.assertFalse(carrier_out in carrier_set)

    def test_carrier_dat_id_single_carrier(self):
        """Test carrier_DAT_ID method with single carrier."""
        carrier_set = Yarn_Carrier_Set(7)

        self.assertEqual(carrier_set.carrier_DAT_ID(), 7)

    def test_carrier_dat_id_multiple_carriers(self):
        """Test carrier_DAT_ID method with multiple carriers."""
        carrier_set = Yarn_Carrier_Set([1, 2, 3])

        # Should be: 3*100 + 2*10 + 1*1 = 321 (reversed order)
        self.assertEqual(carrier_set.carrier_DAT_ID(), 123)

    def test_carrier_dat_id_complex_case(self):
        """Test carrier_DAT_ID method with complex case."""
        carrier_set = Yarn_Carrier_Set([5, 0, 8, 2])

        # Should be: 2*1000 + 8*100 + 0*10 + 5*1 = 2805
        self.assertEqual(carrier_set.carrier_DAT_ID(), 5082)

    def test_empty_carrier_set(self):
        """Test behavior with empty carrier set."""
        # Note: This tests edge case that may not be intended usage
        with warnings.catch_warnings():
            # Suppress warnings for this test
            warnings.simplefilter("ignore")
            carrier_set = Yarn_Carrier_Set([])

        self.assertEqual(len(carrier_set), 0)
        self.assertFalse(carrier_set.many_carriers)
        self.assertEqual(carrier_set.carrier_DAT_ID(), 0)

    def test_duplicate_handling_preserves_order(self):
        """Test that duplicate handling preserves order of first occurrence."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore duplicate warnings for this test
            carrier_set = Yarn_Carrier_Set([3, 1, 4, 1, 5, 3, 2])

        # Should preserve order: 3, 1, 4, 5, 2
        self.assertEqual(carrier_set.carrier_ids, [3, 1, 4, 5, 2])
