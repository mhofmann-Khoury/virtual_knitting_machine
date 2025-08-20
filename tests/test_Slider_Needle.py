"""Comprehensive unit tests for the Slider_Needle class."""
import unittest

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import (
    Slider_Needle,
)


class TestSliderNeedle(unittest.TestCase):
    """Test cases for the Slider_Needle class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.front_slider = Slider_Needle(is_front=True, position=5)
        self.back_slider = Slider_Needle(is_front=False, position=10)

    def test_initialization(self):
        """Test slider needle initialization."""
        # Test front slider
        self.assertTrue(self.front_slider.is_front)
        self.assertEqual(self.front_slider.position, 5)
        self.assertTrue(self.front_slider.is_slider)

        # Test back slider
        self.assertFalse(self.back_slider.is_front)
        self.assertEqual(self.back_slider.position, 10)
        self.assertTrue(self.back_slider.is_slider)

    def test_is_slider_property(self):
        """Test is_slider property returns True for slider needles."""
        self.assertTrue(self.front_slider.is_slider)
        self.assertTrue(self.back_slider.is_slider)

    def test_string_representation(self):
        """Test string representations of slider needles."""
        # Front slider
        self.assertEqual(str(self.front_slider), "fs5")
        self.assertEqual(repr(self.front_slider), "fs5")

        # Back slider
        self.assertEqual(str(self.back_slider), "bs10")
        self.assertEqual(repr(self.back_slider), "bs10")

    def test_string_representation_different_from_regular_needle(self):
        """Test slider needle string representation differs from regular needle."""
        regular_front = Needle(is_front=True, position=5)
        regular_back = Needle(is_front=False, position=10)

        # Should be different from regular needles
        self.assertNotEqual(str(self.front_slider), str(regular_front))
        self.assertNotEqual(str(self.back_slider), str(regular_back))

    def test_inherited_methods(self):
        """Test that inherited methods work correctly."""
        # Test opposite needle
        front_opposite = self.front_slider.opposite()
        self.assertFalse(front_opposite.is_front)
        self.assertEqual(front_opposite.position, 5)
        self.assertTrue(front_opposite.is_slider)  # opposite() returns same type

        # Test offset needle
        offset_slider = self.front_slider.offset(3)
        self.assertTrue(offset_slider.is_front)
        self.assertEqual(offset_slider.position, 8)
        self.assertTrue(offset_slider.is_slider)  # offset() returns same type

        # Test main needle
        main_needle = self.front_slider.main_needle()
        self.assertTrue(main_needle.is_front)
        self.assertEqual(main_needle.position, 5)
        self.assertFalse(main_needle.is_slider)

    def test_arithmetic_operations_return_type(self):
        """Test that arithmetic operations return correct types."""
        # Addition should return Slider_Needle (due to __class__ usage)
        result_add = self.front_slider + 3
        self.assertIsInstance(result_add, Slider_Needle)
        self.assertEqual(result_add.position, 8)
        self.assertTrue(result_add.is_slider)

        # Subtraction should return Slider_Needle
        result_sub = self.front_slider - 2
        self.assertIsInstance(result_sub, Slider_Needle)
        self.assertEqual(result_sub.position, 3)
        self.assertTrue(result_sub.is_slider)

    def test_comparison_operations(self):
        """Test comparison operations work correctly for slider needles."""
        slider1 = Slider_Needle(is_front=True, position=3)
        slider2 = Slider_Needle(is_front=True, position=7)
        slider3 = Slider_Needle(is_front=False, position=3)

        # Position-based comparison
        self.assertTrue(slider1 < slider2)
        self.assertFalse(slider2 < slider1)

        # Same position, front comes before back
        self.assertTrue(slider1 < slider3)
        self.assertFalse(slider3 < slider1)

    def test_equality_with_regular_needles(self):
        """Test equality comparison between slider needles and regular needles."""
        regular_needle = Needle(is_front=True, position=5)

        # Slider needle should NOT equal regular needle even with same position/bed
        self.assertFalse(self.front_slider == regular_needle)
        self.assertFalse(regular_needle == self.front_slider)

        # But slider should equal another slider with same properties
        another_slider = Slider_Needle(is_front=True, position=5)
        self.assertTrue(self.front_slider == another_slider)

    def test_hash_consistency(self):
        """Test hash function works consistently for slider needles."""
        # Hash should be same as regular needle (based on position only)
        regular_needle = Needle(is_front=True, position=5)
        self.assertEqual(hash(self.front_slider), hash(regular_needle))

        # But equality should still be False
        self.assertFalse(self.front_slider == regular_needle)

    def test_integer_conversion(self):
        """Test integer conversion works for slider needles."""
        self.assertEqual(int(self.front_slider), 5)
        self.assertEqual(int(self.back_slider), 10)

    def test_racked_position_calculation(self):
        """Test racked position calculation works for slider needles."""
        # Front slider position unchanged at any rack
        self.assertEqual(self.front_slider.racked_position_on_front(0), 5)
        self.assertEqual(self.front_slider.racked_position_on_front(2), 5)

        # Back slider position adjusted by rack
        self.assertEqual(self.back_slider.racked_position_on_front(0), 10)
        self.assertEqual(self.back_slider.racked_position_on_front(2), 12)
        self.assertEqual(self.back_slider.racked_position_on_front(-1), 9)

    def test_at_racking_comparison(self):
        """Test racking comparison works for slider needles."""
        front_slider = Slider_Needle(is_front=True, position=3)
        back_slider = Slider_Needle(is_front=False, position=1)

        # At rack 2: front 3 aligns with back 1 (3 = 1 + 2)
        self.assertEqual(front_slider.at_racking_comparison(back_slider, rack=2), 0)

    def test_multiple_slider_positions(self):
        """Test slider needles at various positions."""
        positions = [0, 1, 50, 100, 500]

        for pos in positions:
            front_slider = Slider_Needle(is_front=True, position=pos)
            back_slider = Slider_Needle(is_front=False, position=pos)

            self.assertEqual(front_slider.position, pos)
            self.assertEqual(back_slider.position, pos)
            self.assertTrue(front_slider.is_slider)
            self.assertTrue(back_slider.is_slider)
            self.assertEqual(str(front_slider), f"fs{pos}")
            self.assertEqual(str(back_slider), f"bs{pos}")

    def test_edge_case_positions(self):
        """Test slider needles with edge case positions."""
        # Test negative position (if allowed)
        negative_slider = Slider_Needle(is_front=True, position=-5)
        self.assertEqual(negative_slider.position, -5)
        self.assertEqual(str(negative_slider), "fs-5")

        # Test zero position
        zero_slider = Slider_Needle(is_front=False, position=0)
        self.assertEqual(zero_slider.position, 0)
        self.assertEqual(str(zero_slider), "bs0")

    def test_slider_specific_functionality(self):
        """Test functionality that is specific to slider needles."""
        regular_needle = Needle(is_front=True, position=5)

        # The main difference should be the is_slider property
        self.assertTrue(self.front_slider.is_slider)
        self.assertFalse(regular_needle.is_slider)

        # And the string representation
        self.assertEqual(str(self.front_slider), "fs5")
        self.assertEqual(str(regular_needle), "f5")

        # All other functionality should be inherited and work the same way
        # This includes loop holding, transfer operations, arithmetic, etc.
