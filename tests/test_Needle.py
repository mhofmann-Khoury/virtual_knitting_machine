"""Comprehensive unit tests for the Needle class."""

import random
import unittest
from unittest.mock import Mock

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class TestNeedle(unittest.TestCase):
    """Test cases for the Needle class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.machine = Knitting_Machine()
        self.front_pos = random.randint(0, 540)
        self.back_pos = random.randint(0, 540)
        self.front_needle = self.machine.get_specified_needle(is_front=True, position=self.front_pos)
        self.back_needle = self.machine.get_specified_needle(is_front=False, position=self.back_pos)

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

    def test_slot_number(self):
        """Test racked position calculation for front bed alignment."""
        # Front needle position unchanged
        self.assertEqual(self.front_needle.slot_by_racking(0), self.front_pos)
        self.assertEqual(self.front_needle.slot_by_racking(2), self.front_pos)

        # Back needle position adjusted by rack
        self.assertEqual(self.back_needle.slot_by_racking(0), self.back_pos)
        self.assertEqual(self.back_needle.slot_by_racking(2), self.back_pos + 2)
        self.assertEqual(self.back_needle.slot_by_racking(-1), self.back_pos - 1)

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

    def test_integer_conversion(self):
        """Test integer conversion returns position."""
        self.assertEqual(int(self.front_needle), self.front_pos)
        self.assertEqual(int(self.back_needle), self.back_pos)

    def test_comparison_with_needles(self):
        """Test comparison operations with other needles."""
        needle1 = self.machine.get_specified_needle(is_front=True, position=3)
        needle2 = self.machine.get_specified_needle(is_front=True, position=7)
        needle3 = self.machine.get_specified_needle(is_front=False, position=3)

        # Position-based comparison
        self.assertTrue(needle1 < needle2)
        self.assertFalse(needle2 < needle1)

        # Same position, front comes before back
        self.assertTrue(needle1 < needle3)
        self.assertFalse(needle3 < needle1)

        # Same needle
        needle4 = self.machine.get_specified_needle(is_front=True, position=3)
        self.assertFalse(needle1 < needle4)
        self.assertFalse(needle4 < needle1)

    def test_comparison_with_numbers(self):
        """Test comparison operations with numbers."""
        needle = self.machine.get_specified_needle(is_front=True, position=10)
        self.assertFalse(needle < 10)  # Equality
        self.assertFalse(needle < 3)
        self.assertFalse(needle < 5.5)
        self.assertTrue(needle < 11)

    def test_arithmetic_operations_with_needles(self):
        """Test arithmetic operations with other needles."""
        needle1 = self.machine.get_specified_needle(is_front=True, position=5)
        needle2 = self.machine.get_specified_needle(is_front=False, position=3)

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
        needle = self.machine.get_specified_needle(is_front=True, position=10)

        # Addition
        self.assertEqual((needle + 5).position, 15)
        self.assertEqual((5 + needle).position, 15)

        # Subtraction
        self.assertEqual((needle - 3).position, 7)
        self.assertEqual((15 - needle).position, 5)

    def test_equality_comparison(self):
        """Test equality comparison between needles."""
        needle1 = self.machine.get_specified_needle(is_front=True, position=5)
        needle2 = self.machine.get_specified_needle(is_front=True, position=5)
        needle3 = self.machine.get_specified_needle(is_front=False, position=5)
        needle4 = self.machine.get_specified_needle(is_front=True, position=7)

        self.assertTrue(needle1 == needle2)
        self.assertFalse(needle1 == needle3)
        self.assertFalse(needle1 == needle4)
