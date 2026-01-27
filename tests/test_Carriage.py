from unittest import TestCase

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.Side_of_Needle_Bed import Side_of_Needle_Bed


class TestCarriage(TestCase):

    def setUp(self):
        machine = Knitting_Machine()
        self.carriage = machine.carriage

    def test_initialization(self):
        self.assertIsNotNone(self.carriage.knitting_machine)
        self.assertFalse(self.carriage.position_on_bed.on_bed)
        self.assertIs(self.carriage.position_on_bed.position_on_bed, Side_of_Needle_Bed.Left_Side)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

    def test_move_to_needle(self):
        self.carriage.move_to_needle(Needle(True, 10))
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 10)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

        self.carriage.move_to_needle(Needle(True, 20))
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 20)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

        self.carriage.move_to_needle(Needle(True, 15))
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 15)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

    def test_move_in_direction(self):
        self.carriage.move_in_direction(Needle(True, 10), Carriage_Pass_Direction.Leftward)
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 10)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

        self.carriage.move_in_direction(Needle(True, 10), Carriage_Pass_Direction.Rightward)
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 10)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Rightward)

        self.carriage.move_in_direction(Needle(True, 20), Carriage_Pass_Direction.Leftward)
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 20)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Leftward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Leftward)

        self.carriage.move_in_direction(Needle(True, 15), Carriage_Pass_Direction.Rightward)
        self.assertTrue(self.carriage.position_on_bed.on_bed)
        self.assertEqual(self.carriage.slot_number, 15)
        self.assertIs(self.carriage.last_direction, Carriage_Pass_Direction.Rightward)
        self.assertIs(self.carriage.last_set_direction, Carriage_Pass_Direction.Rightward)
