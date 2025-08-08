"""Comprehensive unit tests for the Knitting_Machine class."""
import unittest

from knit_graphs.Knit_Graph import Knit_Graph

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_exceptions.racking_errors import Max_Rack_Exception
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class TestKnittingMachine(unittest.TestCase):
    """Test cases for the Knitting_Machine class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.spec = Knitting_Machine_Specification()
        self.machine = Knitting_Machine(self.spec)

    def test_initialization_default(self):
        """Test machine initialization with default parameters."""
        machine = Knitting_Machine()

        self.assertIsInstance(machine.machine_specification, Knitting_Machine_Specification)
        self.assertIsNotNone(machine.front_bed)
        self.assertIsNotNone(machine.back_bed)
        self.assertIsNotNone(machine._carrier_system)
        self.assertIsNotNone(machine.carriage)
        self.assertEqual(machine._rack, 0)
        self.assertFalse(machine._all_needle_rack)
        self.assertIsInstance(machine.knit_graph, Knit_Graph)

    def test_initialization_custom_spec(self):
        """Test machine initialization with custom specification."""
        custom_spec = Knitting_Machine_Specification()
        custom_spec.needle_count = 100
        custom_spec.carrier_count = 5

        machine = Knitting_Machine(custom_spec)

        self.assertEqual(machine.machine_specification, custom_spec)
        self.assertEqual(machine.needle_count, 100)
        self.assertEqual(len(machine.carrier_system.carriers), 5)

    def test_max_rack_property(self):
        """Test max_rack property."""
        self.assertEqual(self.machine.max_rack, self.spec.maximum_rack)

    def test_carrier_system_property_getter(self):
        """Test carrier_system property getter."""
        self.assertEqual(self.machine.carrier_system, self.machine._carrier_system)

    def test_needle_count_property(self):
        """Test needle_count property."""
        self.assertEqual(self.machine.needle_count, self.spec.needle_count)

    def test_len_method(self):
        """Test __len__ method returns needle count."""
        self.assertEqual(len(self.machine), self.machine.needle_count)

    def test_get_needle_of_loop_front_bed(self):
        """Test get_needle_of_loop when loop is on front bed."""
        self.machine.in_hook(1)
        needle = Needle(True, 1)
        loops = self.machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)
        result = self.machine.get_needle_of_loop(loops[0])

        self.assertEqual(result, needle)

    def test_get_needle_of_loop_back_bed(self):
        """Test get_needle_of_loop when loop is on back bed."""
        self.machine.in_hook(1)
        needle = Needle(False, 1)
        loops = self.machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)
        self.assertTrue(self.machine[needle].has_loops)
        result = self.machine.get_needle_of_loop(loops[0])

        self.assertIsNotNone(result)
        self.assertEqual(result, needle)

    def test_get_needle_of_loop_not_held(self):
        """Test get_needle_of_loop when loop is not held."""
        loop = Machine_Knit_Loop(0, self.machine.carrier_system.carriers[0].yarn, Needle(True, 1))
        loop.drop()
        result = self.machine.get_needle_of_loop(loop)

        self.assertIsNone(result)

    def test_rack_property_getter(self):
        """Test rack property getter."""
        self.assertEqual(self.machine.rack, 0)

        self.machine._rack = 3
        self.assertEqual(self.machine.rack, 3)

    def test_all_needle_rack_property(self):
        """Test all_needle_rack property."""
        self.assertFalse(self.machine.all_needle_rack)

        self.machine._all_needle_rack = True
        self.assertTrue(self.machine.all_needle_rack)

    def test_rack_property_setter_valid_rack(self):
        """Test rack property setter with valid rack value."""
        self.machine.rack = 3

        self.assertEqual(self.machine._rack, 3)
        self.assertFalse(self.machine._all_needle_rack)

    def test_rack_property_setter_all_needle_positive(self):
        """Test rack property setter with positive all-needle racking."""
        self.machine.rack = 2.25

        self.assertEqual(self.machine._rack, 2)
        self.assertTrue(self.machine._all_needle_rack)

    def test_rack_property_setter_all_needle_negative(self):
        """Test rack property setter with negative all-needle racking."""
        self.machine.rack = -2.75

        self.assertEqual(self.machine._rack, -3)  # Adjusted down for negative
        self.assertTrue(self.machine._all_needle_rack)

    def test_rack_property_setter_exceeds_max_raises_exception(self):
        """Test rack property setter raises exception when exceeding max rack."""
        max_rack = self.machine.max_rack

        with self.assertRaises(Max_Rack_Exception):
            self.machine.rack = max_rack + 1

    def test_get_needle_with_needle_object(self):
        """Test get_needle method with Needle object."""
        needle = Needle(is_front=True, position=5)

        result = self.machine.get_needle(needle)

        self.assertIsInstance(result, Needle)
        self.assertTrue(result.is_front)
        self.assertEqual(result.position, 5)

    def test_get_needle_with_tuple_two_elements(self):
        """Test get_needle method with 2-element tuple."""
        result = self.machine.get_needle((False, 10))

        self.assertIsInstance(result, Needle)
        self.assertFalse(result.is_front)
        self.assertEqual(result.position, 10)

    def test_get_needle_with_tuple_three_elements_regular(self):
        """Test get_needle method with 3-element tuple for regular needle."""
        result = self.machine.get_needle((True, 15, False))

        self.assertIsInstance(result, Needle)
        self.assertFalse(result.is_slider)
        self.assertTrue(result.is_front)
        self.assertEqual(result.position, 15)

    def test_get_needle_with_tuple_three_elements_slider(self):
        """Test get_needle method with 3-element tuple for slider needle."""
        result = self.machine.get_needle((False, 8, True))

        self.assertIsInstance(result, Slider_Needle)
        self.assertTrue(result.is_slider)
        self.assertFalse(result.is_front)
        self.assertEqual(result.position, 8)

    def test_get_carrier_single_integer(self):
        """Test get_carrier method with single integer."""
        result = self.machine.get_carrier(3)

        self.assertIsInstance(result, Yarn_Carrier)
        self.assertEqual(result.carrier_id, 3)

    def test_get_carrier_carrier_set(self):
        """Test get_carrier method with carrier set."""
        carrier_set = Yarn_Carrier_Set([1, 3, 5])
        result = self.machine.get_carrier(carrier_set)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_getitem_with_needle(self):
        """Test __getitem__ with Needle object."""
        needle = Needle(is_front=True, position=7)
        result = self.machine[needle]

        self.assertIsInstance(result, Needle)
        self.assertEqual(result.position, 7)

    def test_getitem_with_tuple(self):
        """Test __getitem__ with tuple."""
        result = self.machine[(False, 12)]

        self.assertIsInstance(result, Needle)
        self.assertFalse(result.is_front)
        self.assertEqual(result.position, 12)

    def test_getitem_with_carrier(self):
        """Test __getitem__ with Yarn_Carrier."""
        carrier = self.machine.carrier_system.carriers[0]
        result = self.machine[carrier]

        self.assertEqual(result, carrier)

    def test_getitem_with_loop(self):
        """Test __getitem__ with Machine_Knit_Loop."""
        self.machine.in_hook(1)
        needle = Needle(False, 1)
        loops = self.machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)
        result = self.machine[loops[0]]

        self.assertEqual(result, needle)

    def test_getitem_invalid_type_raises_error(self):
        """Test __getitem__ with invalid type raises KeyError."""
        with self.assertRaises(KeyError):
            _ = self.machine["invalid_type"]

    def test_update_rack_changes_rack(self):
        """Test update_rack method when rack changes."""
        original_rack = self.machine.rack

        result = self.machine.update_rack(front_pos=10, back_pos=8)

        self.assertTrue(result)
        self.assertEqual(self.machine.rack, 2)  # 10 - 3 = 7
        self.assertNotEqual(self.machine.rack, original_rack)

    def test_update_rack_no_change(self):
        """Test update_rack method when rack doesn't change."""
        self.machine.rack = 4

        result = self.machine.update_rack(front_pos=10, back_pos=6)

        self.assertFalse(result)
        self.assertEqual(self.machine.rack, 4)  # Should remain 4

    def test_get_rack_static_method(self):
        """Test get_rack static method."""
        result = Knitting_Machine.get_rack(front_pos=15, back_pos=8)
        self.assertEqual(result, 7)  # 15 - 8 = 7

        result = Knitting_Machine.get_rack(front_pos=5, back_pos=10)
        self.assertEqual(result, -5)  # 5 - 10 = -5

    def test_get_aligned_needle_front_to_back(self):
        """Test get_aligned_needle from front to back bed."""
        self.machine.rack = 3
        front_needle = Needle(is_front=True, position=10)

        result = self.machine.get_aligned_needle(front_needle)

        self.assertFalse(result.is_front)
        self.assertEqual(result.position, 7)  # 10 - 3 = 7
        self.assertFalse(result.is_slider)

    def test_get_aligned_needle_back_to_front(self):
        """Test get_aligned_needle from back to front bed."""
        self.machine.rack = 2
        back_needle = Needle(is_front=False, position=8)

        result = self.machine.get_aligned_needle(back_needle)

        self.assertTrue(result.is_front)
        self.assertEqual(result.position, 10)  # 8 + 2 = 10
        self.assertFalse(result.is_slider)

    def test_get_aligned_needle_with_slider(self):
        """Test get_aligned_needle with slider option."""
        self.machine.rack = 1
        front_needle = Needle(is_front=True, position=5)

        result = self.machine.get_aligned_needle(front_needle, aligned_slider=True)

        self.assertFalse(result.is_front)
        self.assertEqual(result.position, 4)  # 5 - 1 = 4
        self.assertTrue(result.is_slider)

    def test_get_transfer_rack_front_to_back(self):
        """Test get_transfer_rack static method from front to back."""
        front_needle = Needle(is_front=True, position=12)
        back_needle = Needle(is_front=False, position=8)

        result = Knitting_Machine.get_transfer_rack(front_needle, back_needle)

        self.assertEqual(result, 4)  # 12 - 8 = 4

    def test_get_transfer_rack_back_to_front(self):
        """Test get_transfer_rack static method from back to front."""
        back_needle = Needle(is_front=False, position=6)
        front_needle = Needle(is_front=True, position=10)

        result = Knitting_Machine.get_transfer_rack(back_needle, front_needle)

        self.assertEqual(result, 4)  # 10 - 6 = 4

    def test_get_transfer_rack_same_bed_returns_none(self):
        """Test get_transfer_rack returns None for needles on same bed."""
        needle1 = Needle(is_front=True, position=5)
        needle2 = Needle(is_front=True, position=10)

        result = Knitting_Machine.get_transfer_rack(needle1, needle2)

        self.assertIsNone(result)

    def test_valid_rack_true(self):
        """Test valid_rack returns True when current rack is correct."""
        self.machine.rack = 4

        result = self.machine.valid_rack(front_pos=12, back_pos=8)

        self.assertTrue(result)  # 12 - 8 = 4, matches current rack

    def test_valid_rack_false(self):
        """Test valid_rack returns False when current rack is incorrect."""
        self.machine.rack = 3

        result = self.machine.valid_rack(front_pos=10, back_pos=5)

        self.assertFalse(result)  # 10 - 5 = 5, doesn't match rack 3

    def test_sliders_are_clear(self):
        """Test sliders_are_clear as loops are moved between sliders and front bed."""
        self.machine.in_hook(1)
        needle = Needle(False, 1)
        _loops = self.machine.tuck(Yarn_Carrier_Set(1), needle, Carriage_Pass_Direction.Leftward)
        self.assertTrue(self.machine.sliders_are_clear())
        self.machine.xfer(needle, to_slider=True)
        self.assertFalse(self.machine.sliders_are_clear())
        self.machine.xfer(Slider_Needle(is_front=True, position=1), to_slider=False)
        self.assertTrue(self.machine.sliders_are_clear())

    def test_loop_holding_accessor_methods(self):
        """Test loop-holding needle accessor methods."""
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        front_needle = Needle(True, 1)
        back_needle = Needle(False, 1)
        back_slider = Slider_Needle(False, 1)
        self.machine.tuck(cs, front_needle, Carriage_Pass_Direction.Leftward)
        self.assertTrue(len(self.machine.front_loops()) == 1)
        self.assertTrue(len(self.machine.back_loops()) == 0)
        self.assertTrue(len(self.machine.front_slider_loops()) == 0)
        self.assertTrue(len(self.machine.back_slider_loops()) == 0)
        self.assertTrue(len(self.machine.all_slider_loops()) == 0)
        self.assertTrue(len(self.machine.all_loops()) == 1)
        self.machine.xfer(front_needle, to_slider=True)
        self.assertTrue(len(self.machine.front_loops()) == 0)
        self.assertTrue(len(self.machine.back_loops()) == 0)
        self.assertTrue(len(self.machine.front_slider_loops()) == 0)
        self.assertTrue(len(self.machine.back_slider_loops()) == 1)
        self.assertTrue(len(self.machine.all_slider_loops()) == 1)
        self.assertTrue(len(self.machine.all_loops()) == 0)
        self.machine.xfer(back_slider, to_slider=False)
        self.machine.tuck(cs, back_needle, Carriage_Pass_Direction.Rightward)
        self.assertTrue(len(self.machine.front_loops()) == 1)
        self.assertTrue(len(self.machine.back_loops()) == 1)
        self.assertTrue(len(self.machine.front_slider_loops()) == 0)
        self.assertTrue(len(self.machine.back_slider_loops()) == 0)
        self.assertTrue(len(self.machine.all_slider_loops()) == 0)
        self.assertTrue(len(self.machine.all_loops()) == 2)

    def test_comprehensive_machine_workflow(self):
        """Test comprehensive machine workflow with multiple operations."""
        # Initialize machine
        machine = Knitting_Machine()

        # Test initial state
        self.assertEqual(machine.rack, 0)
        self.assertFalse(machine.all_needle_rack)
        self.assertTrue(machine.sliders_are_clear())

        # Test rack adjustment
        machine.rack = 2
        self.assertEqual(machine.rack, 2)

        # Test needle access
        front_needle = machine.get_needle((True, 10))
        self.assertTrue(front_needle.is_front)
        self.assertEqual(front_needle.position, 10)

        # Test aligned needle calculation
        aligned = machine.get_aligned_needle(front_needle)
        self.assertFalse(aligned.is_front)
        self.assertEqual(aligned.position, 8)  # 10 - 2 = 8
