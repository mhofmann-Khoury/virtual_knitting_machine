"""Comprehensive unit tests for the Carriage_Pass_Direction enum."""
import unittest

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class TestCarriagePassDirection(unittest.TestCase):
    """Test cases for the Carriage_Pass_Direction enum."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.leftward = Carriage_Pass_Direction.Leftward
        self.rightward = Carriage_Pass_Direction.Rightward

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        self.assertEqual(self.leftward.value, "-")
        self.assertEqual(self.rightward.value, "+")

    def test_string_representation(self):
        """Test string representation of enum values."""
        self.assertEqual(str(self.leftward), "-")
        self.assertEqual(str(self.rightward), "+")
        self.assertEqual(repr(self.leftward), "-")
        self.assertEqual(repr(self.rightward), "+")

    def test_opposite_method(self):
        """Test opposite method returns correct opposite direction."""
        self.assertEqual(self.leftward.opposite(), self.rightward)
        self.assertEqual(self.rightward.opposite(), self.leftward)

    def test_unary_operators(self):
        """Test unary operators return opposite direction."""
        # Test unary minus
        self.assertEqual(-self.leftward, self.rightward)
        self.assertEqual(-self.rightward, self.leftward)

        # Test bitwise invert
        self.assertEqual(~self.leftward, self.rightward)
        self.assertEqual(~self.rightward, self.leftward)

    def test_next_needle_position(self):
        """Test next needle position calculation in each direction."""
        # Leftward decreases position
        self.assertEqual(self.leftward.next_needle_position(5), 4)
        self.assertEqual(self.leftward.next_needle_position(0), -1)
        self.assertEqual(self.leftward.next_needle_position(10), 9)

        # Rightward increases position
        self.assertEqual(self.rightward.next_needle_position(5), 6)
        self.assertEqual(self.rightward.next_needle_position(0), 1)
        self.assertEqual(self.rightward.next_needle_position(10), 11)

    def test_prior_needle_position(self):
        """Test prior needle position calculation in each direction."""
        # Leftward increases position (opposite of next)
        self.assertEqual(self.leftward.prior_needle_position(5), 6)
        self.assertEqual(self.leftward.prior_needle_position(0), 1)
        self.assertEqual(self.leftward.prior_needle_position(10), 11)

        # Rightward decreases position (opposite of next)
        self.assertEqual(self.rightward.prior_needle_position(5), 4)
        self.assertEqual(self.rightward.prior_needle_position(0), -1)
        self.assertEqual(self.rightward.prior_needle_position(10), 9)

    def test_next_prior_consistency(self):
        """Test that next and prior are consistent opposites."""
        positions = [0, 5, 10, -3, 100]

        for pos in positions:
            # next followed by prior should return original position
            next_pos = self.leftward.next_needle_position(pos)
            back_to_original = self.leftward.prior_needle_position(next_pos)
            self.assertEqual(back_to_original, pos)

            # Same for rightward
            next_pos_r = self.rightward.next_needle_position(pos)
            back_to_original_r = self.rightward.prior_needle_position(next_pos_r)
            self.assertEqual(back_to_original_r, pos)

    def test_rightward_needles_comparison(self):
        """Test static method for rightward needle comparison."""
        needle_left = Needle(is_front=True, position=3)
        needle_right = Needle(is_front=True, position=7)
        needle_same = Needle(is_front=True, position=3)

        # Left needle should come before right needle in rightward order
        result = Carriage_Pass_Direction.rightward_needles_comparison(needle_left, needle_right)
        self.assertEqual(result, 1)  # left comes first in rightward

        # Right needle should come after left needle
        result = Carriage_Pass_Direction.rightward_needles_comparison(needle_right, needle_left)
        self.assertEqual(result, -1)  # right comes second in rightward

        # Same needles should be equal
        result = Carriage_Pass_Direction.rightward_needles_comparison(needle_left, needle_same)
        self.assertEqual(result, 0)

    def test_leftward_needles_comparison(self):
        """Test static method for leftward needle comparison."""
        needle_left = Needle(is_front=True, position=3)
        needle_right = Needle(is_front=True, position=7)
        needle_same = Needle(is_front=True, position=3)

        # Left needle should come after right needle in leftward order
        result = Carriage_Pass_Direction.leftward_needles_comparison(needle_left, needle_right)
        self.assertEqual(result, -1)  # left comes second in leftward

        # Right needle should come before left needle
        result = Carriage_Pass_Direction.leftward_needles_comparison(needle_right, needle_left)
        self.assertEqual(result, 1)  # right comes first in leftward

        # Same needles should be equal
        result = Carriage_Pass_Direction.leftward_needles_comparison(needle_left, needle_same)
        self.assertEqual(result, 0)

    def test_needle_direction_comparison_rightward(self):
        """Test needle direction comparison for rightward direction."""
        needle_left = Needle(is_front=True, position=3)
        needle_right = Needle(is_front=True, position=7)

        # For rightward, left needle comes first
        result = self.rightward.needle_direction_comparison(needle_left, needle_right)
        self.assertEqual(result, 1)

        result = self.rightward.needle_direction_comparison(needle_right, needle_left)
        self.assertEqual(result, -1)

    def test_all_needle_direction_comparison_rightward(self):
        needle_left = Needle(is_front=False, position=0)
        needle_right = Needle(is_front=True, position=0)
        result = self.rightward.needle_direction_comparison(needle_left, needle_right, rack=-1, all_needle_rack=True)
        self.assertEqual(result, 1)

        needle_left = needle_right
        needle_right = Needle(is_front=False, position=1)
        result = self.rightward.needle_direction_comparison(needle_left, needle_right, rack=-1, all_needle_rack=True)
        self.assertEqual(result, 1)

    def test_needle_direction_comparison_leftward(self):
        """Test needle direction comparison for leftward direction."""
        needle_left = Needle(is_front=True, position=3)
        needle_right = Needle(is_front=True, position=7)

        # For leftward, right needle comes first
        result = self.leftward.needle_direction_comparison(needle_left, needle_right)
        self.assertEqual(result, -1)

        result = self.leftward.needle_direction_comparison(needle_right, needle_left)
        self.assertEqual(result, 1)

    def test_needles_are_in_pass_direction(self):
        """Test checking if needles are in correct pass direction order."""
        needle_left = Needle(is_front=True, position=3)
        needle_right = Needle(is_front=True, position=7)

        # Rightward: left before right
        self.assertTrue(self.rightward.needles_are_in_pass_direction(needle_left, needle_right))
        self.assertFalse(self.rightward.needles_are_in_pass_direction(needle_right, needle_left))

        # Leftward: right before left
        self.assertTrue(self.leftward.needles_are_in_pass_direction(needle_right, needle_left))
        self.assertFalse(self.leftward.needles_are_in_pass_direction(needle_left, needle_right))

    def test_comparison_with_racking(self):
        """Test needle comparisons with different racking values."""
        front_needle = Needle(is_front=True, position=5)
        back_needle = Needle(is_front=False, position=3)

        # At rack 2: front 5 aligns with back 3 (5 = 3 + 2)
        result = self.rightward.needle_direction_comparison(front_needle, back_needle, rack=2)
        self.assertEqual(result, 0)  # Should be equal at this racking

    def test_comparison_with_all_needle_racking(self):
        """Test needle comparisons with all needle racking enabled."""
        front_needle = Needle(is_front=True, position=5)
        back_needle = Needle(is_front=False, position=5)

        # With all needle racking, front should come before back at same position
        result = self.rightward.needle_direction_comparison(front_needle, back_needle, all_needle_rack=True)
        self.assertEqual(result, 1)  # Front comes first
        result = self.leftward.needle_direction_comparison(front_needle, back_needle, all_needle_rack=True)
        self.assertEqual(result, -1)  # Front comes first

    def test_get_direction_from_string(self):
        """Test static method to get direction from string."""
        self.assertEqual(Carriage_Pass_Direction.get_direction("-"), self.leftward)
        self.assertEqual(Carriage_Pass_Direction.get_direction("+"), self.rightward)
        self.assertEqual(Carriage_Pass_Direction.get_direction("anything"), self.rightward)
        self.assertEqual(Carriage_Pass_Direction.get_direction(""), self.rightward)

    def test_sort_needles_rightward(self):
        """Test sorting needles in rightward direction."""
        needles = [
            Needle(is_front=True, position=7),
            Needle(is_front=True, position=2),
            Needle(is_front=True, position=5),
            Needle(is_front=False, position=3)
        ]

        sorted_needles = self.rightward.sort_needles(needles)

        # Should be sorted by position ascending (left to right)
        positions = [n.position for n in sorted_needles]
        self.assertEqual(positions, sorted(positions))

        # First needle should be leftmost
        self.assertEqual(sorted_needles[0].position, 2)
        # Last needle should be rightmost
        self.assertEqual(sorted_needles[-1].position, 7)

    def test_sort_needles_leftward(self):
        """Test sorting needles in leftward direction."""
        needles = [
            Needle(is_front=True, position=7),
            Needle(is_front=True, position=2),
            Needle(is_front=True, position=5),
            Needle(is_front=False, position=3)
        ]

        sorted_needles = self.leftward.sort_needles(needles)

        # Should be sorted by position descending (right to left)
        positions = [n.position for n in sorted_needles]
        self.assertEqual(positions, sorted(positions, reverse=True))

        # First needle should be rightmost
        self.assertEqual(sorted_needles[0].position, 7)
        # Last needle should be leftmost
        self.assertEqual(sorted_needles[-1].position, 2)

    def test_sort_needles_with_racking(self):
        """Test sorting needles with specific racking value."""
        front_needle = Needle(is_front=True, position=5)
        back_needle = Needle(is_front=False, position=3)

        needles = [back_needle, front_needle]

        # At rack 2, these needles should be at same effective position
        sorted_needles = self.rightward.sort_needles(needles, racking=2)

        # Should have both needles, order may depend on tie-breaking rules
        self.assertEqual(len(sorted_needles), 2)
        self.assertIn(front_needle, sorted_needles)
        self.assertIn(back_needle, sorted_needles)

    def test_sort_needles_empty_list(self):
        """Test sorting empty list of needles."""
        empty_needles = []

        result_rightward = self.rightward.sort_needles(empty_needles)
        result_leftward = self.leftward.sort_needles(empty_needles)

        self.assertEqual(result_rightward, [])
        self.assertEqual(result_leftward, [])

    def test_sort_needles_single_needle(self):
        """Test sorting single needle."""
        single_needle = [Needle(is_front=True, position=5)]

        result_rightward = self.rightward.sort_needles(single_needle)
        result_leftward = self.leftward.sort_needles(single_needle)

        self.assertEqual(len(result_rightward), 1)
        self.assertEqual(len(result_leftward), 1)
        self.assertEqual(result_rightward[0].position, 5)
        self.assertEqual(result_leftward[0].position, 5)

    def test_sort_needles_with_mixed_beds(self):
        """Test sorting needles from both front and back beds."""
        needles = [
            Needle(is_front=True, position=3),
            Needle(is_front=False, position=3),
            Needle(is_front=True, position=5),
            Needle(is_front=False, position=1)
        ]

        sorted_rightward = self.rightward.sort_needles(needles)
        sorted_leftward = self.leftward.sort_needles(needles)

        # Check that all needles are included
        self.assertEqual(len(sorted_rightward), 4)
        self.assertEqual(len(sorted_leftward), 4)

        # Check rightward order (ascending positions)
        rightward_positions = [n.position for n in sorted_rightward]
        self.assertTrue(all(rightward_positions[i] <= rightward_positions[i + 1]
                            for i in range(len(rightward_positions) - 1)))

        # Check leftward order (descending positions)
        leftward_positions = [n.position for n in sorted_leftward]
        self.assertTrue(all(leftward_positions[i] >= leftward_positions[i + 1]
                            for i in range(len(leftward_positions) - 1)))

    def test_enum_identity(self):
        """Test that enum instances maintain identity."""
        # Same enum values should be identical
        self.assertIs(Carriage_Pass_Direction.Leftward, self.leftward)
        self.assertIs(Carriage_Pass_Direction.Rightward, self.rightward)

        # Different enum values should not be identical
        self.assertIsNot(self.leftward, self.rightward)

    def test_enum_equality(self):
        """Test enum equality comparisons."""
        self.assertEqual(Carriage_Pass_Direction.Leftward, self.leftward)
        self.assertEqual(Carriage_Pass_Direction.Rightward, self.rightward)
        self.assertNotEqual(self.leftward, self.rightward)

    def test_enum_in_collections(self):
        """Test enum usage in collections."""
        direction_list = [self.leftward, self.rightward, self.leftward]
        direction_set = {self.leftward, self.rightward, self.leftward}

        self.assertEqual(len(direction_list), 3)
        self.assertEqual(len(direction_set), 2)  # Set should deduplicate

        self.assertIn(self.leftward, direction_list)
        self.assertIn(self.rightward, direction_set)
