"""Comprehensive unit tests for the Sheet_Needle and Slider_Sheet_Needle classes."""

import unittest
from unittest.mock import Mock

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Sheet_Needle import (
    Sheet_Needle,
    Slider_Sheet_Needle,
    get_sheet_needle,
)
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class TestSheetNeedle(unittest.TestCase):
    """Test cases for the Sheet_Needle class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sheet needles with gauge 4
        self.sheet_needle = Sheet_Needle(is_front=True, sheet_pos=5, sheet=2, gauge=4)
        self.back_sheet_needle = Sheet_Needle(is_front=False, sheet_pos=3, sheet=1, gauge=4)
        self.slider_sheet = Slider_Sheet_Needle(is_front=True, sheet_pos=3, sheet=1, gauge=4)

    def test_initialization(self):
        """Test sheet needle initialization."""
        self.assertTrue(self.sheet_needle.is_front)
        self.assertEqual(self.sheet_needle.sheet_pos, 5)
        self.assertEqual(self.sheet_needle.sheet, 2)
        self.assertEqual(self.sheet_needle.gauge, 4)
        self.assertEqual(len(self.sheet_needle.recorded_loops), 0)

        # Test actual position calculation: sheet + sheet_pos * gauge = 2 + 5 * 4 = 22
        self.assertEqual(self.sheet_needle.position, 22)

    def test_properties(self):
        """Test sheet needle specific properties."""
        self.assertEqual(self.sheet_needle.gauge, 4)
        self.assertEqual(self.sheet_needle.sheet_pos, 5)
        self.assertEqual(self.sheet_needle.sheet, 2)

    def test_static_get_sheet_pos(self):
        """Test static method get_sheet_pos."""
        # actual_pos = 23, gauge = 4 -> sheet_pos = 23 // 4 = 5
        self.assertEqual(Sheet_Needle.get_sheet_pos(23, 4), 5)
        self.assertEqual(Sheet_Needle.get_sheet_pos(20, 4), 5)
        self.assertEqual(Sheet_Needle.get_sheet_pos(0, 4), 0)
        self.assertEqual(Sheet_Needle.get_sheet_pos(3, 4), 0)
        self.assertEqual(Sheet_Needle.get_sheet_pos(4, 4), 1)

    def test_static_get_sheet(self):
        """Test static method get_sheet."""
        # actual_pos = 23, sheet_pos = 5, gauge = 4 -> sheet = 23 - (5 * 4) = 3
        self.assertEqual(Sheet_Needle.get_sheet(23, 5, 4), 3)
        self.assertEqual(Sheet_Needle.get_sheet(20, 5, 4), 0)
        self.assertEqual(Sheet_Needle.get_sheet(21, 5, 4), 1)
        self.assertEqual(Sheet_Needle.get_sheet(22, 5, 4), 2)

    def test_static_get_actual_pos(self):
        """Test static method get_actual_pos."""
        # sheet_pos = 5, sheet = 2, gauge = 4 -> actual_pos = 2 + 5 * 4 = 22
        self.assertEqual(Sheet_Needle.get_actual_pos(5, 2, 4), 22)
        self.assertEqual(Sheet_Needle.get_actual_pos(0, 0, 4), 0)
        self.assertEqual(Sheet_Needle.get_actual_pos(3, 1, 4), 13)
        self.assertEqual(Sheet_Needle.get_actual_pos(2, 3, 5), 13)

    def test_offset_in_sheet(self):
        """Test offset_in_sheet method."""
        # Test regular offset
        offset_needle = self.sheet_needle.offset_in_sheet(3)
        self.assertIsInstance(offset_needle, Sheet_Needle)
        self.assertFalse(offset_needle.is_slider)
        self.assertTrue(offset_needle.is_front)
        self.assertEqual(offset_needle.sheet_pos, 8)  # 5 + 3
        self.assertEqual(offset_needle.sheet, 2)
        self.assertEqual(offset_needle.gauge, 4)

    def test_main_needle(self):
        """Test main_needle method returns non-slider sheet needle."""
        main = self.sheet_needle.main_needle()
        self.assertIsInstance(main, Sheet_Needle)
        self.assertFalse(main.is_slider)
        self.assertEqual(main.sheet_pos, 5)
        self.assertEqual(main.sheet, 2)
        self.assertEqual(main.gauge, 4)
        self.assertTrue(main.is_front)

    def test_gauge_neighbors(self):
        """Test gauge_neighbors method."""
        neighbors = self.sheet_needle.gauge_neighbors()

        # Should return 3 neighbors (gauge 4 - 1 for current sheet)
        self.assertEqual(len(neighbors), 3)

        # All should be Sheet_Needles with same sheet_pos and gauge, different sheets
        expected_sheets = {0, 1, 3}  # All sheets except current (2)
        actual_sheets = {n.sheet for n in neighbors}
        self.assertEqual(actual_sheets, expected_sheets)

        for neighbor in neighbors:
            self.assertIsInstance(neighbor, Sheet_Needle)
            self.assertEqual(neighbor.sheet_pos, 5)
            self.assertEqual(neighbor.gauge, 4)
            self.assertTrue(neighbor.is_front)
            self.assertNotEqual(neighbor.sheet, 2)  # Should not include current sheet

    def test_arithmetic_operations(self):
        """Test arithmetic operations with sheet needles."""
        sheet2 = Sheet_Needle(is_front=False, sheet_pos=2, sheet=1, gauge=4)

        # Addition with Sheet_Needle (uses sheet_pos)
        result = self.sheet_needle + sheet2
        self.assertIsInstance(result, Sheet_Needle)
        self.assertEqual(result.sheet_pos, 7)  # 5 + 2
        self.assertEqual(result.sheet, 2)  # Keeps original sheet
        self.assertEqual(result.gauge, 4)
        self.assertTrue(result.is_front)

        # Addition with regular Needle (uses position)
        regular_needle = Needle(is_front=True, position=3)
        result2 = self.sheet_needle + regular_needle
        self.assertEqual(result2.sheet_pos, 8)  # 5 + 3

        # Addition with integer
        result3 = self.sheet_needle + 4
        self.assertEqual(result3.sheet_pos, 9)  # 5 + 4

    def test_subtraction_operations(self):
        """Test subtraction operations with sheet needles."""
        # Subtraction
        result = self.sheet_needle - 2
        self.assertEqual(result.sheet_pos, 3)  # 5 - 2

        # Right subtraction
        result2 = 10 - self.sheet_needle
        self.assertEqual(result2.sheet_pos, 5)  # 10 - 5

    def test_inherited_functionality(self):
        """Test that inherited Needle functionality works correctly."""
        from knit_graphs.Pull_Direction import Pull_Direction

        # Test pull direction
        self.assertEqual(self.sheet_needle.pull_direction, Pull_Direction.BtF)
        self.assertEqual(self.back_sheet_needle.pull_direction, Pull_Direction.FtB)

        # Test bed properties
        self.assertTrue(self.sheet_needle.is_front)
        self.assertFalse(self.sheet_needle.is_back)
        self.assertFalse(self.back_sheet_needle.is_front)
        self.assertTrue(self.back_sheet_needle.is_back)

        # Test is_slider (should be False for regular Sheet_Needle)
        self.assertFalse(self.sheet_needle.is_slider)

    def test_loop_operations(self):
        """Test loop operations work correctly with sheet needles."""
        # Test has_loops
        self.assertFalse(self.sheet_needle.has_loops)

        # Test adding loops
        mock_loop = Mock(spec=Machine_Knit_Loop)
        mock_loop.yarn = Mock()
        mock_loop.yarn.active_loops = {}

        self.sheet_needle.add_loop(mock_loop)
        self.assertTrue(self.sheet_needle.has_loops)
        self.assertEqual(len(self.sheet_needle.held_loops), 1)

    def test_string_representation(self):
        """Test string representation uses inherited Needle format."""
        # Should use actual position, not sheet position
        self.assertEqual(str(self.sheet_needle), "f22")  # actual position 22
        self.assertEqual(str(self.back_sheet_needle), "b13")  # actual position 13

    def test_slider_initialization(self):
        """Test slider sheet needle initialization."""
        self.assertTrue(self.slider_sheet.is_front)
        self.assertEqual(self.slider_sheet.sheet_pos, 3)
        self.assertEqual(self.slider_sheet.sheet, 1)
        self.assertEqual(self.slider_sheet.gauge, 4)
        self.assertEqual(self.slider_sheet.position, 13)  # 1 + 3 * 4

    def test_inheritance(self):
        """Test multiple inheritance from both Sheet_Needle and Slider_Needle."""
        self.assertIsInstance(self.slider_sheet, Sheet_Needle)
        self.assertIsInstance(self.slider_sheet, Slider_Needle)
        self.assertIsInstance(self.slider_sheet, Needle)

    def test_is_slider_property(self):
        """Test is_slider property returns True."""
        self.assertTrue(self.slider_sheet.is_slider)

    def test_slider_string_representation(self):
        """Test string representation shows slider format."""
        # Should use slider format with actual position
        self.assertEqual(str(self.slider_sheet), "fs13")

    def test_sheet_operations_work(self):
        """Test that sheet-specific operations work correctly."""
        # Test offset in sheet
        offset = self.slider_sheet.offset_in_sheet(2)
        self.assertIsInstance(offset, Slider_Sheet_Needle)  # Returns Slider_Sheet_Needle
        self.assertTrue(offset.is_slider)
        self.assertEqual(offset.sheet_pos, 5)

    def test_slider_gauge_neighbors(self):
        """Test gauge_neighbors returns regular Sheet_Needles."""
        neighbors = self.slider_sheet.gauge_neighbors()

        self.assertEqual(len(neighbors), 3)  # gauge 4 - 1
        for neighbor in neighbors:
            self.assertIsInstance(neighbor, Sheet_Needle)
            self.assertTrue(neighbor.is_slider)
            self.assertEqual(neighbor.sheet_pos, 3)
            self.assertNotEqual(neighbor.sheet, 1)

    def test_get_regular_sheet_needle(self):
        """Test getting regular sheet needle from regular needle."""
        needle = Needle(is_front=True, position=14)  # position 14
        gauge = 4

        sheet_needle = get_sheet_needle(needle, gauge, slider=False)

        self.assertIsInstance(sheet_needle, Sheet_Needle)
        self.assertFalse(sheet_needle.is_slider)
        self.assertTrue(sheet_needle.is_front)
        self.assertEqual(sheet_needle.position, 14)
        self.assertEqual(sheet_needle.gauge, 4)

        # Calculate expected sheet_pos and sheet
        expected_sheet_pos = 14 // 4  # 3
        expected_sheet = 14 % 4  # 2
        self.assertEqual(sheet_needle.sheet_pos, expected_sheet_pos)
        self.assertEqual(sheet_needle.sheet, expected_sheet)

    def test_get_slider_sheet_needle(self):
        """Test getting slider sheet needle from regular needle."""
        needle = Needle(is_front=False, position=17)
        gauge = 5

        slider_sheet = get_sheet_needle(needle, gauge, slider=True)

        self.assertIsInstance(slider_sheet, Slider_Sheet_Needle)
        self.assertTrue(slider_sheet.is_slider)
        self.assertFalse(slider_sheet.is_front)
        self.assertEqual(slider_sheet.position, 17)
        self.assertEqual(slider_sheet.gauge, 5)

        # Calculate expected values
        expected_sheet_pos = 17 // 5  # 3
        expected_sheet = 17 % 5  # 2
        self.assertEqual(slider_sheet.sheet_pos, expected_sheet_pos)
        self.assertEqual(slider_sheet.sheet, expected_sheet)

    def test_get_sheet_needle_from_slider(self):
        """Test getting sheet needle from slider needle."""
        slider = Slider_Needle(is_front=True, position=12)
        gauge = 3

        sheet_needle = get_sheet_needle(slider, gauge, slider=False)

        self.assertIsInstance(sheet_needle, Sheet_Needle)
        self.assertFalse(sheet_needle.is_slider)
        self.assertEqual(sheet_needle.position, 12)
        self.assertEqual(sheet_needle.gauge, 3)

        expected_sheet_pos = 12 // 3  # 4
        expected_sheet = 12 % 3  # 0
        self.assertEqual(sheet_needle.sheet_pos, expected_sheet_pos)
        self.assertEqual(sheet_needle.sheet, expected_sheet)

    def test_various_gauge_values(self):
        """Test function with various gauge values."""
        needle = Needle(is_front=True, position=20)

        gauges = [1, 2, 4, 5, 10]
        for gauge in gauges:
            sheet_needle = get_sheet_needle(needle, gauge)

            self.assertEqual(sheet_needle.gauge, gauge)
            self.assertEqual(sheet_needle.position, 20)
            self.assertEqual(sheet_needle.sheet_pos, 20 // gauge)
            self.assertEqual(sheet_needle.sheet, 20 % gauge)

    def test_edge_case_positions(self):
        """Test function with edge case positions."""
        # Position 0
        needle0 = Needle(is_front=True, position=0)
        sheet0 = get_sheet_needle(needle0, 4)
        self.assertEqual(sheet0.sheet_pos, 0)
        self.assertEqual(sheet0.sheet, 0)
        self.assertEqual(sheet0.position, 0)

        # Large position
        needle_large = Needle(is_front=False, position=1000)
        sheet_large = get_sheet_needle(needle_large, 7)
        self.assertEqual(sheet_large.sheet_pos, 1000 // 7)
        self.assertEqual(sheet_large.sheet, 1000 % 7)
        self.assertEqual(sheet_large.position, 1000)
