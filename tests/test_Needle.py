"""Comprehensive unit tests for the Needle class."""
import random
import unittest
from unittest.mock import Mock

from knit_graphs.Pull_Direction import Pull_Direction

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class TestNeedle(unittest.TestCase):
    """Test cases for the Needle class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.front_pos = random.randint(0, 540)
        self.back_pos = random.randint(0, 540)
        self.front_needle = Needle(is_front=True, position=self.front_pos)
        self.back_needle = Needle(is_front=False, position=self.back_pos)

    def test_initialization(self):
        """Test needle initialization with various parameters."""
        # Test front needle
        self.assertTrue(self.front_needle.is_front)
        self.assertEqual(self.front_needle.position, self.front_pos)
        self.assertEqual(len(self.front_needle.held_loops), 0)

        # Test back needle
        self.assertFalse(self.back_needle.is_front)
        self.assertEqual(self.back_needle.position, self.back_pos)
        self.assertEqual(len(self.back_needle.held_loops), 0)

        # Test position conversion to int
        float_base = random.randint(0, 540)
        float_pos = float_base + random.uniform(0, 1)
        float_needle = Needle(is_front=True, position=float_pos)
        self.assertEqual(float_needle.position, float_base)

    def test_pull_direction_property(self):
        """Test pull direction property returns correct values."""
        self.assertEqual(self.front_needle.pull_direction, Pull_Direction.BtF)
        self.assertEqual(self.back_needle.pull_direction, Pull_Direction.FtB)

    def test_is_front_property(self):
        """Test is_front property returns correct values."""
        self.assertTrue(self.front_needle.is_front)
        self.assertFalse(self.back_needle.is_front)

    def test_is_back_property(self):
        """Test is_back property returns correct values."""
        self.assertFalse(self.front_needle.is_back)
        self.assertTrue(self.back_needle.is_back)

    def test_position_property(self):
        """Test position property returns correct values."""
        self.assertEqual(self.front_needle.position, self.front_pos)
        self.assertEqual(self.back_needle.position, self.back_pos)

    def test_has_loops_property(self):
        """Test has_loops property reflects loop state correctly."""
        self.assertFalse(self.front_needle.has_loops)

        # Mock loop and add to needle
        mock_loop = Mock(spec=Machine_Knit_Loop)
        mock_loop.yarn = Mock()
        mock_loop.yarn.active_loops = {}
        self.front_needle.held_loops.append(mock_loop)

        self.assertTrue(self.front_needle.has_loops)

    def test_is_slider_property(self):
        """Test is_slider property returns False for regular needles."""
        self.assertFalse(self.front_needle.is_slider)
        self.assertFalse(self.back_needle.is_slider)

    def test_add_loop(self):
        """Test adding a single loop to needle."""
        mock_loop = Mock(spec=Machine_Knit_Loop)
        mock_loop.yarn = Mock()
        mock_loop.yarn.active_loops = {}

        self.front_needle.add_loop(mock_loop)

        self.assertEqual(len(self.front_needle.held_loops), 1)
        self.assertIn(mock_loop, self.front_needle.held_loops)
        self.assertEqual(mock_loop.yarn.active_loops[mock_loop], self.front_needle)

    def test_add_loops_multiple(self):
        """Test adding multiple loops to needle."""
        mock_loops = []
        for i in range(3):
            mock_loop = Mock(spec=Machine_Knit_Loop)
            mock_loop.yarn = Mock()
            mock_loop.yarn.active_loops = {}
            mock_loops.append(mock_loop)

        self.front_needle.add_loops(mock_loops)

        self.assertEqual(len(self.front_needle.held_loops), 3)
        for loop in mock_loops:
            self.assertIn(loop, self.front_needle.held_loops)

    def test_transfer_loops(self):
        """Test transferring loops from one needle to another."""
        # Setup source needle with loops
        mock_loops = []
        for i in range(2):
            mock_loop = Mock(spec=Machine_Knit_Loop)
            mock_loop.yarn = Mock()
            mock_loop.yarn.active_loops = {}
            mock_loops.append(mock_loop)
            self.front_needle.held_loops.append(mock_loop)

        target_needle = Needle(is_front=False, position=3)
        transferred_loops = self.front_needle.transfer_loops(target_needle)

        # Check source needle is empty
        self.assertEqual(len(self.front_needle.held_loops), 0)
        # Check target needle has loops
        self.assertEqual(len(target_needle.held_loops), 2)
        # Check returned loops match
        self.assertEqual(len(transferred_loops), 2)

        # Verify transfer_loop was called on each loop
        for loop in mock_loops:
            loop.transfer_loop.assert_called_once_with(target_needle)

    def test_drop_loops(self):
        """Test dropping all loops from needle."""
        mock_loops = []
        for i in range(2):
            mock_loop = Mock(spec=Machine_Knit_Loop)
            mock_loop.yarn = Mock()
            mock_loop.yarn.active_loops = {mock_loop: self.front_needle}
            mock_loops.append(mock_loop)
            self.front_needle.held_loops.append(mock_loop)

        dropped_loops = self.front_needle.drop()

        # Check needle is empty
        self.assertEqual(len(self.front_needle.held_loops), 0)
        # Check correct loops were returned
        self.assertEqual(len(dropped_loops), 2)

        # Verify drop was called on each loop and removed from active_loops
        for loop in mock_loops:
            loop.drop.assert_called_once()
            self.assertNotIn(loop, loop.yarn.active_loops)

    def test_opposite_needle(self):
        """Test getting needle on opposite bed."""
        front_opposite = self.front_needle.opposite()
        back_opposite = self.back_needle.opposite()

        self.assertFalse(front_opposite.is_front)
        self.assertEqual(front_opposite.position, self.front_pos)

        self.assertTrue(back_opposite.is_front)
        self.assertEqual(back_opposite.position, self.back_pos)

    def test_offset_needle(self):
        """Test getting offset needle on same bed."""
        positive_offset = 3
        offset_positive = self.front_needle.offset(positive_offset)
        negative_offset = -2
        offset_negative = self.front_needle.offset(negative_offset)

        self.assertTrue(offset_positive.is_front)
        self.assertEqual(offset_positive.position, self.front_pos + positive_offset)

        self.assertTrue(offset_negative.is_front)
        self.assertEqual(offset_negative.position, self.front_pos + negative_offset)

    def test_racked_position_on_front(self):
        """Test racked position calculation for front bed alignment."""
        # Front needle position unchanged
        self.assertEqual(self.front_needle.racked_position_on_front(0), self.front_pos)
        self.assertEqual(self.front_needle.racked_position_on_front(2), self.front_pos)

        # Back needle position adjusted by rack
        self.assertEqual(self.back_needle.racked_position_on_front(0), self.back_pos)
        self.assertEqual(self.back_needle.racked_position_on_front(2), self.back_pos + 2)
        self.assertEqual(self.back_needle.racked_position_on_front(-1), self.back_pos - 1)

    def test_main_needle(self):
        """Test getting main needle returns regular needle."""
        main = self.front_needle.main_needle()

        self.assertTrue(main.is_front)
        self.assertEqual(main.position, self.front_pos)
        self.assertFalse(main.is_slider)

    def test_string_representation(self):
        """Test string representations of needles."""
        self.assertEqual(str(self.front_needle), f"f{self.front_pos}")
        self.assertEqual(str(self.back_needle), f"b{self.back_pos}")

    def test_hash_function(self):
        """Test hash function for needles."""
        self.assertEqual(hash(self.front_needle), self.front_pos)
        self.assertEqual(hash(self.back_needle), -1 * self.back_pos)

        # Test hash consistency
        same_needle = Needle(is_front=True, position=self.front_pos)
        self.assertEqual(hash(self.front_needle), hash(same_needle))

    def test_integer_conversion(self):
        """Test integer conversion returns position."""
        self.assertEqual(int(self.front_needle), self.front_pos)
        self.assertEqual(int(self.back_needle), self.back_pos)

    def test_index_conversion(self):
        """Test index conversion returns position."""
        self.assertEqual(self.front_needle.__index__(), self.front_pos)
        self.assertEqual(self.back_needle.__index__(), self.back_pos)

    def test_comparison_with_needles(self):
        """Test comparison operations with other needles."""
        needle1 = Needle(is_front=True, position=3)
        needle2 = Needle(is_front=True, position=7)
        needle3 = Needle(is_front=False, position=3)

        # Position-based comparison
        self.assertTrue(needle1 < needle2)
        self.assertFalse(needle2 < needle1)

        # Same position, front comes before back
        self.assertTrue(needle1 < needle3)
        self.assertFalse(needle3 < needle1)

        # Same needle
        needle4 = Needle(is_front=True, position=3)
        self.assertFalse(needle1 < needle4)
        self.assertFalse(needle4 < needle1)

    def test_comparison_with_numbers(self):
        """Test comparison operations with numbers."""
        needle = Needle(is_front=True, position=10)
        self.assertFalse(needle < 10)  # Equality
        self.assertFalse(needle < 3)
        self.assertFalse(needle < 5.5)
        self.assertTrue(needle < 11)

    def test_comparison_type_error(self):
        """Test comparison with invalid types raises TypeError."""
        with self.assertRaises(TypeError):
            self.front_needle < "invalid"

    def test_at_racking_comparison(self):
        """Test needle comparison at different racking values."""
        front_3 = Needle(is_front=True, position=3)
        back_1 = Needle(is_front=False, position=1)

        # At rack 2: front 3 aligns with back 1 (3 = 1 + 2)
        self.assertEqual(front_3.at_racking_comparison(back_1, rack=2), 0)

        # Front 3 vs front 5
        front_5 = Needle(is_front=True, position=5)
        self.assertEqual(front_3.at_racking_comparison(front_5), -1)
        self.assertEqual(front_5.at_racking_comparison(front_3), 1)

    def test_static_needle_at_racking_cmp(self):
        """Test static method for needle comparison at racking."""
        needle1 = Needle(is_front=True, position=3)
        needle2 = Needle(is_front=True, position=5)

        result = Needle.needle_at_racking_cmp(needle1, needle2)
        self.assertEqual(result, -1)

    def test_arithmetic_operations_with_needles(self):
        """Test arithmetic operations with other needles."""
        needle1 = Needle(is_front=True, position=5)
        needle2 = Needle(is_front=False, position=3)

        # Addition
        result_add = needle1 + needle2
        self.assertTrue(result_add.is_front)
        self.assertEqual(result_add.position, 8)

        # Right addition
        result_radd = needle2 + needle1
        self.assertFalse(result_radd.is_front)
        self.assertEqual(result_radd.position, 8)

        # Subtraction
        result_sub = needle1 - needle2
        self.assertTrue(result_sub.is_front)
        self.assertEqual(result_sub.position, 2)

    def test_arithmetic_operations_with_integers(self):
        """Test arithmetic operations with integers."""
        needle = Needle(is_front=True, position=10)

        # Addition
        self.assertEqual((needle + 5).position, 15)
        self.assertEqual((5 + needle).position, 15)

        # Subtraction
        self.assertEqual((needle - 3).position, 7)
        self.assertEqual((15 - needle).position, 5)

    def test_shift_operations(self):
        """Test left and right shift operations."""
        needle = Needle(is_front=True, position=10)

        # Left shift (subtraction)
        left_shifted = needle << 3
        self.assertEqual(left_shifted.position, 7)

        # Right shift (addition)
        right_shifted = needle >> 3
        self.assertEqual(right_shifted.position, 13)

    def test_equality_comparison(self):
        """Test equality comparison between needles."""
        needle1 = Needle(is_front=True, position=5)
        needle2 = Needle(is_front=True, position=5)
        needle3 = Needle(is_front=False, position=5)
        needle4 = Needle(is_front=True, position=7)

        self.assertTrue(needle1 == needle2)
        self.assertFalse(needle1 == needle3)
        self.assertFalse(needle1 == needle4)

    def test_active_floats(self):
        """Test active floats calculation."""
        # Create mock loops with yarn connections
        loop1 = Mock(spec=Machine_Knit_Loop)
        loop2 = Mock(spec=Machine_Knit_Loop)

        # Setup loop1 connections
        loop1.next_loop_on_yarn.return_value = loop2
        loop1.prior_loop_on_yarn.return_value = None
        loop2.on_needle = True

        # Setup loop2 connections
        loop2.next_loop_on_yarn.return_value = None
        loop2.prior_loop_on_yarn.return_value = loop1
        loop1.on_needle = True

        self.front_needle.held_loops = [loop1, loop2]

        floats = self.front_needle.active_floats()

        # Should have float from loop1 to loop2
        self.assertEqual(len(floats), 1)
        self.assertIn(loop1, floats)
        self.assertEqual(floats[loop1], loop2)

    def test_float_overlaps_needle(self):
        """Test float overlap detection with needle position."""
        # Create mock loops on needles
        loop1 = Mock(spec=Machine_Knit_Loop)
        loop2 = Mock(spec=Machine_Knit_Loop)

        loop1.on_needle = True
        loop2.on_needle = True

        # Setup needles for loops
        left_needle = Mock()
        left_needle.position = 2
        right_needle = Mock()
        right_needle.position = 8

        loop1.holding_needle = left_needle
        loop2.holding_needle = right_needle

        # Test needle in middle of float
        middle_needle = Needle(is_front=True, position=5)
        self.assertTrue(middle_needle.float_overlaps_needle(loop1, loop2))

        # Test needle outside float range
        outside_needle = Needle(is_front=True, position=10)
        self.assertFalse(outside_needle.float_overlaps_needle(loop1, loop2))

        # Test with off-needle loops
        loop1.on_needle = False
        self.assertFalse(middle_needle.float_overlaps_needle(loop1, loop2))
