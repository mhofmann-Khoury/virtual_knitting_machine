"""Comprehensive unit tests for the Carriage_Pass_Direction enum."""

import unittest

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class TestCarriagePassDirection(unittest.TestCase):
    """Test cases for the Carriage_Pass_Direction enum."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.machine = Knitting_Machine()
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

    def test_get_direction_from_string(self):
        """Test static method to get direction from string."""
        self.assertEqual(Carriage_Pass_Direction.get_direction("-"), self.leftward)
        self.assertEqual(Carriage_Pass_Direction.get_direction("+"), self.rightward)
        self.assertEqual(Carriage_Pass_Direction.get_direction("anything"), self.rightward)
        self.assertEqual(Carriage_Pass_Direction.get_direction(""), self.rightward)

    def test_sort_needles_rightward(self):
        """Test sorting needles in rightward direction."""
        needles = [
            self.machine.get_specified_needle(is_front=True, position=7),
            self.machine.get_specified_needle(is_front=True, position=2),
            self.machine.get_specified_needle(is_front=True, position=5),
            self.machine.get_specified_needle(is_front=False, position=3),
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
            self.machine.get_specified_needle(is_front=True, position=7),
            self.machine.get_specified_needle(is_front=True, position=2),
            self.machine.get_specified_needle(is_front=True, position=5),
            self.machine.get_specified_needle(is_front=False, position=3),
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
        front_needle = self.machine.get_specified_needle(is_front=True, position=5)
        back_needle = self.machine.get_specified_needle(is_front=False, position=3)

        needles = [back_needle, front_needle]

        # At rack 2, these needles should be at same effective position
        sorted_needles = self.rightward.sort_needles(needles, racking=2)

        # Should have both needles, order may depend on tie-breaking rules
        self.assertEqual(len(sorted_needles), 2)
        self.assertIn(front_needle, sorted_needles)
        self.assertIn(back_needle, sorted_needles)

    def test_sort_needles_with_mixed_beds(self):
        """Test sorting needles from both front and back beds."""
        needles = [
            self.machine.get_specified_needle(is_front=True, position=3),
            self.machine.get_specified_needle(is_front=False, position=3),
            self.machine.get_specified_needle(is_front=True, position=5),
            self.machine.get_specified_needle(is_front=False, position=1),
        ]

        sorted_rightward = self.rightward.sort_needles(needles)
        sorted_leftward = self.leftward.sort_needles(needles)

        # Check that all needles are included
        self.assertEqual(len(sorted_rightward), 4)
        self.assertEqual(len(sorted_leftward), 4)

        # Check rightward order (ascending positions)
        rightward_positions = [n.position for n in sorted_rightward]
        self.assertTrue(
            all(rightward_positions[i] <= rightward_positions[i + 1] for i in range(len(rightward_positions) - 1))
        )

        # Check leftward order (descending positions)
        leftward_positions = [n.position for n in sorted_leftward]
        self.assertTrue(
            all(leftward_positions[i] >= leftward_positions[i + 1] for i in range(len(leftward_positions) - 1))
        )
