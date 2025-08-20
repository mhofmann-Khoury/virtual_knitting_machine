"""Comprehensive unit tests for the Carriage_Side enum."""
import unittest

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Side import (
    Carriage_Side,
)


class TestCarriageSide(unittest.TestCase):
    """Test cases for the Carriage_Side enum."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.left_side = Carriage_Side.Left_Side
        self.right_side = Carriage_Side.Right_Side

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        self.assertEqual(self.left_side.value, "Left_Side")
        self.assertEqual(self.right_side.value, "Right_Side")

    def test_string_representation(self):
        """Test string representation of enum values."""
        self.assertEqual(str(self.left_side), "Left_Side")
        self.assertEqual(str(self.right_side), "Right_Side")
        self.assertEqual(repr(self.left_side), "Left_Side")
        self.assertEqual(repr(self.right_side), "Right_Side")

    def test_opposite_method(self):
        """Test opposite method returns correct opposite side."""
        self.assertEqual(self.left_side.opposite(), self.right_side)
        self.assertEqual(self.right_side.opposite(), self.left_side)

    def test_opposite_is_symmetric(self):
        """Test that opposite operation is symmetric."""
        # Applying opposite twice should return original
        self.assertEqual(self.left_side.opposite().opposite(), self.left_side)
        self.assertEqual(self.right_side.opposite().opposite(), self.right_side)

    def test_unary_operators(self):
        """Test unary operators return opposite side."""
        # Test unary minus
        self.assertEqual(-self.left_side, self.right_side)
        self.assertEqual(-self.right_side, self.left_side)

        # Test bitwise invert
        self.assertEqual(~self.left_side, self.right_side)
        self.assertEqual(~self.right_side, self.left_side)

    def test_reverse_direction(self):
        """Test reverse_direction method returns correct direction away from side."""
        # From left side, reverse direction should be rightward (away from left)
        self.assertEqual(self.left_side.reverse_direction(), Carriage_Pass_Direction.Rightward)

        # From right side, reverse direction should be leftward (away from right)
        self.assertEqual(self.right_side.reverse_direction(), Carriage_Pass_Direction.Leftward)

    def test_current_direction(self):
        """Test current_direction method returns correct direction toward side."""
        # To reach left side, direction should be leftward
        self.assertEqual(self.left_side.current_direction(), Carriage_Pass_Direction.Leftward)

        # To reach right side, direction should be rightward
        self.assertEqual(self.right_side.current_direction(), Carriage_Pass_Direction.Rightward)

    def test_direction_methods_are_opposites(self):
        """Test that reverse_direction and current_direction are opposites."""
        # For left side
        left_reverse = self.left_side.reverse_direction()
        left_current = self.left_side.current_direction()
        self.assertEqual(left_reverse, left_current.opposite())
        self.assertEqual(left_current, left_reverse.opposite())

        # For right side
        right_reverse = self.right_side.reverse_direction()
        right_current = self.right_side.current_direction()
        self.assertEqual(right_reverse, right_current.opposite())
        self.assertEqual(right_current, right_reverse.opposite())

    def test_direction_consistency_with_side_semantics(self):
        """Test that direction methods are consistent with side semantics."""
        # Left side current direction should be leftward (toward left)
        self.assertEqual(self.left_side.current_direction(), Carriage_Pass_Direction.Leftward)

        # Left side reverse direction should be rightward (away from left)
        self.assertEqual(self.left_side.reverse_direction(), Carriage_Pass_Direction.Rightward)

        # Right side current direction should be rightward (toward right)
        self.assertEqual(self.right_side.current_direction(), Carriage_Pass_Direction.Rightward)

        # Right side reverse direction should be leftward (away from right)
        self.assertEqual(self.right_side.reverse_direction(), Carriage_Pass_Direction.Leftward)

    def test_enum_identity(self):
        """Test that enum instances maintain identity."""
        # Same enum values should be identical
        self.assertIs(Carriage_Side.Left_Side, self.left_side)
        self.assertIs(Carriage_Side.Right_Side, self.right_side)

        # Different enum values should not be identical
        self.assertIsNot(self.left_side, self.right_side)

    def test_enum_equality(self):
        """Test enum equality comparisons."""
        self.assertEqual(Carriage_Side.Left_Side, self.left_side)
        self.assertEqual(Carriage_Side.Right_Side, self.right_side)
        self.assertNotEqual(self.left_side, self.right_side)

    def test_enum_in_collections(self):
        """Test enum usage in collections."""
        side_list = [self.left_side, self.right_side, self.left_side]
        side_set = {self.left_side, self.right_side, self.left_side}
        side_dict = {self.left_side: "left", self.right_side: "right"}

        self.assertEqual(len(side_list), 3)
        self.assertEqual(len(side_set), 2)  # Set should deduplicate
        self.assertEqual(len(side_dict), 2)

        self.assertIn(self.left_side, side_list)
        self.assertIn(self.right_side, side_set)
        self.assertEqual(side_dict[self.left_side], "left")
        self.assertEqual(side_dict[self.right_side], "right")

    def test_enum_iteration(self):
        """Test iterating over all enum values."""
        all_sides = list(Carriage_Side)
        self.assertEqual(len(all_sides), 2)
        self.assertIn(self.left_side, all_sides)
        self.assertIn(self.right_side, all_sides)

    def test_enum_comparison_with_strings(self):
        """Test that enum values are not equal to their string representations."""
        self.assertNotEqual(self.left_side, "Left_Side")
        self.assertNotEqual(self.right_side, "Right_Side")

        # But string representations should match
        self.assertEqual(str(self.left_side), "Left_Side")
        self.assertEqual(str(self.right_side), "Right_Side")

    def test_enum_hashable(self):
        """Test that enum values are hashable and can be used as dict keys."""
        side_mapping = {
            self.left_side: "port",
            self.right_side: "starboard"
        }

        self.assertEqual(side_mapping[self.left_side], "port")
        self.assertEqual(side_mapping[self.right_side], "starboard")

        # Test that hash is consistent
        self.assertEqual(hash(self.left_side), hash(Carriage_Side.Left_Side))
        self.assertEqual(hash(self.right_side), hash(Carriage_Side.Right_Side))

    def test_enum_boolean_context(self):
        """Test enum values in boolean context."""
        # Enum values should be truthy
        self.assertTrue(self.left_side)
        self.assertTrue(self.right_side)
        self.assertTrue(bool(self.left_side))
        self.assertTrue(bool(self.right_side))

    def test_comprehensive_opposite_behavior(self):
        """Test comprehensive opposite behavior across all methods."""
        # Test that all opposite-related methods are consistent
        sides = [self.left_side, self.right_side]

        for side in sides:
            opposite_side = side.opposite()

            # Double opposite should return original
            self.assertEqual(opposite_side.opposite(), side)

            # Unary operators should match opposite()
            self.assertEqual(-side, opposite_side)
            self.assertEqual(~side, opposite_side)

            # Direction methods should be opposite between sides
            self.assertEqual(side.current_direction(), opposite_side.reverse_direction())
            self.assertEqual(side.reverse_direction(), opposite_side.current_direction())

    def test_side_direction_mapping_completeness(self):
        """Test that all combinations of sides and directions are handled."""
        # Test all possible combinations
        test_cases = [
            (self.left_side, "current", Carriage_Pass_Direction.Leftward),
            (self.left_side, "reverse", Carriage_Pass_Direction.Rightward),
            (self.right_side, "current", Carriage_Pass_Direction.Rightward),
            (self.right_side, "reverse", Carriage_Pass_Direction.Leftward),
        ]

        for side, direction_type, expected_direction in test_cases:
            if direction_type == "current":
                actual_direction = side.current_direction()
            else:  # reverse
                actual_direction = side.reverse_direction()

            self.assertEqual(
                actual_direction,
                expected_direction,
                f"{side} {direction_type} direction should be {expected_direction}"
            )

    def test_enum_member_access(self):
        """Test accessing enum members by name and value."""
        # Access by name
        self.assertEqual(Carriage_Side["Left_Side"], self.left_side)
        self.assertEqual(Carriage_Side["Right_Side"], self.right_side)

        # Access by value
        self.assertEqual(Carriage_Side("Left_Side"), self.left_side)
        self.assertEqual(Carriage_Side("Right_Side"), self.right_side)

    def test_invalid_enum_access(self):
        """Test that invalid enum access raises appropriate errors."""
        with self.assertRaises(KeyError):
            _ = Carriage_Side["Invalid_Side"]

        with self.assertRaises(ValueError):
            _ = Carriage_Side("Invalid_Side")
