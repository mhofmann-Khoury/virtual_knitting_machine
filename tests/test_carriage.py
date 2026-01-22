"""Comprehensive unit tests for the Carriage class."""

import unittest

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.Carriage_Warning import Carriage_Off_Edge_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage import Carriage
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction


class TestCarriage(unittest.TestCase):
    """Test cases for the Carriage class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the knitting machine
        # self.mock_machine = Mock()
        self.mock_machine = Knitting_Machine()

        # Create carriage with typical parameters
        self.carriage = Carriage(knitting_machine=self.mock_machine)

    def test_initialization_valid_parameters(self):
        """Test carriage initialization with valid parameters."""
        self.assertEqual(
            self.carriage.last_direction, Carriage_Pass_Direction.Leftward
        )  # Defaults to assuming a leftward motion parked the carriage on the left side.
        self.assertEqual(self.carriage.current_needle_slot, 0)  # Should start at left for Rightward movement
        self.assertFalse(self.carriage.transferring)

    def test_transferring_property_setter_start_transfers(self):
        """Test transferring property setter when starting transfers."""
        initial_position = self.carriage.current_needle_slot
        initial_direction = self.carriage.last_direction

        self.carriage.transferring = True

        self.assertTrue(self.carriage.transferring)
        # Position and direction should remain unchanged when starting transfers
        self.assertEqual(self.carriage.current_needle_slot, initial_position)
        self.assertEqual(self.carriage.last_direction, initial_direction)

    def test_transferring_property_setter_end_transfers(self):
        """Test transferring property setter when ending transfers."""
        # Start transfers and move carriage
        self.carriage.transferring = True
        self.carriage.current_needle_slot = 10
        self.carriage.last_direction = Carriage_Pass_Direction.Rightward

        # End transfers should restore previous position and direction
        self.carriage.transferring = False

        self.assertFalse(self.carriage.transferring)
        self.assertEqual(self.carriage.current_needle_slot, 0)  # Restored
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)  # Restored

    def test_current_needle_position_property(self):
        """Test current needle position property getter and setter."""
        self.assertEqual(self.carriage.current_needle_slot, 0)

        self.carriage.current_needle_slot = 15
        self.assertEqual(self.carriage.current_needle_slot, 15)
        self.assertEqual(self.carriage._slot_prior_to_transfers, 15)  # Should update when not transferring

    def test_current_needle_position_during_transfers(self):
        """Test current needle position behavior during transfers."""
        self.carriage.transferring = True
        initial_prior_position = self.carriage._slot_prior_to_transfers

        self.carriage.current_needle_slot = 15

        self.assertEqual(self.carriage.current_needle_slot, 15)
        # Should NOT update prior position during transfers
        self.assertEqual(self.carriage._slot_prior_to_transfers, initial_prior_position)

    def test_reverse_of_last_direction_property(self):
        """Test reverse of last direction property."""
        self.carriage.last_direction = Carriage_Pass_Direction.Leftward
        self.assertEqual(self.carriage.reverse_of_last_direction, Carriage_Pass_Direction.Rightward)

        self.carriage.last_direction = Carriage_Pass_Direction.Rightward
        self.assertEqual(self.carriage.reverse_of_last_direction, Carriage_Pass_Direction.Leftward)

    def test_last_direction_property_setter(self):
        """Test last direction property setter."""
        self.carriage.last_direction = Carriage_Pass_Direction.Rightward
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        self.assertEqual(self.carriage._direction_prior_to_transfers, Carriage_Pass_Direction.Rightward)

    def test_last_direction_setter_during_transfers(self):
        """Test last direction setter behavior during transfers."""
        self.carriage.transferring = True
        initial_prior_direction = self.carriage._direction_prior_to_transfers

        self.carriage.last_direction = Carriage_Pass_Direction.Rightward

        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        # Should NOT update prior direction during transfers
        self.assertEqual(self.carriage._direction_prior_to_transfers, initial_prior_direction)

    def test_on_left_side_property(self):
        """Test on_left_side property."""
        self.carriage.current_needle_slot = 0
        self.assertTrue(self.carriage.on_left_side)

        self.carriage.current_needle_slot = 5
        self.assertFalse(self.carriage.on_left_side)

    def test_on_right_side_property(self):
        """Test on_right_side property."""
        self.carriage.current_needle_slot = self.carriage.rightmost_needle_slot
        self.assertTrue(self.carriage.on_right_side)

        self.carriage.current_needle_slot = 15
        self.assertFalse(self.carriage.on_right_side)

    def test_possible_directions_middle_position(self):
        """Test possible directions from middle position."""
        self.carriage.current_needle_slot = 10  # Middle position

        directions = self.carriage.possible_directions()

        self.assertEqual(len(directions), 2)
        self.assertIn(Carriage_Pass_Direction.Leftward, directions)
        self.assertIn(Carriage_Pass_Direction.Rightward, directions)

    def test_possible_directions_left_side(self):
        """Test possible directions from left side."""
        self.carriage.current_needle_slot = 0  # Left side

        directions = self.carriage.possible_directions()

        self.assertEqual(len(directions), 1)
        self.assertIn(Carriage_Pass_Direction.Rightward, directions)
        self.assertNotIn(Carriage_Pass_Direction.Leftward, directions)

    def test_possible_directions_right_side(self):
        """Test possible directions from right side."""
        self.carriage.current_needle_slot = self.carriage.rightmost_needle_slot  # Right side

        directions = self.carriage.possible_directions()

        self.assertEqual(len(directions), 1)
        self.assertIn(Carriage_Pass_Direction.Leftward, directions)
        self.assertNotIn(Carriage_Pass_Direction.Rightward, directions)

    def test_position_comparison_methods(self):
        """Test left_of, right_of, and on_position methods."""
        self.carriage.current_needle_slot = 10

        # left_of tests
        self.assertTrue(self.carriage.left_of(15))
        self.assertFalse(self.carriage.left_of(5))
        self.assertFalse(self.carriage.left_of(10))

        # right_of tests
        self.assertTrue(self.carriage.right_of(5))
        self.assertFalse(self.carriage.right_of(15))
        self.assertFalse(self.carriage.right_of(10))

        # on_position tests
        self.assertTrue(self.carriage.on_slot(10))
        self.assertFalse(self.carriage.on_slot(5))
        self.assertFalse(self.carriage.on_slot(15))

    def test_direction_to_method(self):
        """Test direction_to method."""
        self.carriage.current_needle_slot = 10

        # Target to the right
        self.assertEqual(self.carriage.direction_to(15), Carriage_Pass_Direction.Rightward)

        # Target to the left
        self.assertEqual(self.carriage.direction_to(5), Carriage_Pass_Direction.Leftward)

        # Target at current position
        self.assertIsNone(self.carriage.direction_to(10))

    def test_move_method_valid_movement(self):
        """Test move method with valid movement."""
        self.carriage.current_needle_slot = 5

        self.carriage.move(Carriage_Pass_Direction.Rightward, 10)

        self.assertEqual(self.carriage.current_needle_slot, 10)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)

    def test_move_method_off_left_edge(self):
        """Test move method with target off left edge triggers warning."""
        self.carriage.current_needle_slot = 5

        with self.assertWarns(Carriage_Off_Edge_Warning):
            self.carriage.move(Carriage_Pass_Direction.Leftward, -5)

        # Should be clamped to left edge
        self.assertEqual(self.carriage.current_needle_slot, 0)

    def test_move_method_off_right_edge(self):
        """Test move method with target off right edge triggers warning."""
        self.carriage.current_needle_slot = 15

        with self.assertWarns(Carriage_Off_Edge_Warning):
            self.carriage.move(Carriage_Pass_Direction.Rightward, self.carriage.rightmost_needle_slot + 25)

        # Should be clamped to right edge
        self.assertEqual(self.carriage.current_needle_slot, self.carriage.rightmost_needle_slot)

    def test_move_to_method(self):
        """Test move_to method."""
        self.carriage.current_needle_slot = 5

        # Move to right
        self.carriage.move_to(15)
        self.assertEqual(self.carriage.current_needle_slot, 15)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)

        # Move to left
        self.carriage.move_to(3)
        self.assertEqual(self.carriage.current_needle_slot, 3)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)

    def test_move_to_same_position(self):
        """Test move_to method when target is current position."""
        self.carriage.current_needle_slot = 10
        initial_direction = self.carriage.last_direction

        self.carriage.move_to(10)

        # Position should remain same, direction should be unchanged
        self.assertEqual(self.carriage.current_needle_slot, 10)
        self.assertEqual(self.carriage.last_direction, initial_direction)

    def test_move_in_reverse_direction(self):
        """Test move_in_reverse_direction method."""
        self.carriage.current_needle_slot = 10
        self.carriage.last_direction = Carriage_Pass_Direction.Rightward

        self.carriage.move_in_reverse_direction(5)

        self.assertEqual(self.carriage.current_needle_slot, 5)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)

    def test_move_in_current_direction(self):
        """Test move_in_current_direction method."""
        self.carriage.current_needle_slot = 10
        self.carriage.last_direction = Carriage_Pass_Direction.Rightward

        self.carriage.move_in_current_direction(15)

        self.assertEqual(self.carriage.current_needle_slot, 15)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)

    def test_transfer_state_management_complex_scenario(self):
        """Test complex transfer state management scenario."""
        # Initial state
        self.carriage.current_needle_slot = 5
        self.carriage.last_direction = Carriage_Pass_Direction.Leftward

        # Start transfers
        self.carriage.transferring = True

        # Move during transfers
        self.carriage.current_needle_slot = 15
        self.carriage.last_direction = Carriage_Pass_Direction.Rightward

        # Verify state during transfers
        self.assertTrue(self.carriage.transferring)
        self.assertEqual(self.carriage.current_needle_slot, 15)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)

        # End transfers - should restore pre-transfer state
        self.carriage.transferring = False

        self.assertFalse(self.carriage.transferring)
        self.assertEqual(self.carriage.current_needle_slot, 5)
        self.assertEqual(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)

    def test_edge_positions_boundary_cases(self):
        """Test behavior at exact boundary positions."""
        # Test exact left boundary
        self.carriage.current_needle_slot = 0
        self.assertTrue(self.carriage.on_left_side)
        self.assertFalse(self.carriage.on_right_side)

        # Test exact right boundary
        self.carriage.current_needle_slot = self.carriage.rightmost_needle_slot
        self.assertFalse(self.carriage.on_left_side)
        self.assertTrue(self.carriage.on_right_side)

        # Test one position inside boundaries
        self.carriage.current_needle_slot = 1
        self.assertFalse(self.carriage.on_left_side)
        self.assertFalse(self.carriage.on_right_side)

        self.carriage.current_needle_slot = 19
        self.assertFalse(self.carriage.on_left_side)
        self.assertFalse(self.carriage.on_right_side)

    def test_multiple_consecutive_moves(self):
        """Test multiple consecutive moves maintain correct state."""
        moves = [
            (Carriage_Pass_Direction.Rightward, 5),
            (Carriage_Pass_Direction.Rightward, 10),
            (Carriage_Pass_Direction.Leftward, 3),
            (Carriage_Pass_Direction.Rightward, 15),
        ]

        for direction, target in moves:
            self.carriage.move(direction, target)
            self.assertEqual(self.carriage.current_needle_slot, target)
            self.assertEqual(self.carriage.last_direction, direction)

    def test_state_consistency_after_operations(self):
        """Test that carriage maintains consistent state after various operations."""
        # Perform various operations
        self.carriage.move_to(10)
        self.carriage.transferring = True
        self.carriage.move_in_reverse_direction(15)
        self.carriage.transferring = False

        # Verify final state consistency
        self.assertEqual(self.carriage.current_needle_slot, 10)  # Restored
        self.assertFalse(self.carriage.transferring)
        # Direction and position should be consistent
        self.assertTrue(0 <= self.carriage.current_needle_slot <= 20)
