"""Comprehensive unit tests for the Carriage class."""
import unittest

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)


class TestCarriage(unittest.TestCase):
    """Test cases for the Carriage class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.spec = Knitting_Machine_Specification()
        self.machine = Knitting_Machine(self.spec)

    def test_decrease_rightward(self):
        self.machine.in_hook(1)  # inhook 1
        cs = Yarn_Carrier_Set(1)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)  # tuck - f2 1
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)  # tuck - f1 1
        self.machine.release_hook()  # releasehook
        self.machine.rack = -1  # rack to right # rack -1
        self.machine.xfer(f1)  # xfer f1 b2
        self.assertEqual(self.machine.back_loops()[0].position, 2)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertEqual(self.machine.knit_graph.braid_graph.get_crossing(l, r), Crossing_Direction.Under_Right)
        self.machine.rack = 0  # rack 0
        self.machine.xfer(f2.opposite())  # xfer b2 f2
        self.assertEqual(len(self.machine.back_loops()), 0)

    def test_decrease_leftward(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = 1  # rack to left
        self.machine.xfer(f2)  # xfer f2 b1
        self.assertEqual(self.machine.back_loops()[0].position, 1)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertEqual(self.machine.knit_graph.braid_graph.get_crossing(l, r), Crossing_Direction.Over_Right)
        self.machine.rack = 0
        self.machine.xfer(f1.opposite())  # xfer b1 f1
        self.assertEqual(len(self.machine.back_loops()), 0)

    def test_decrease_long_rightward(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f3 = Needle(True, 3)
        self.machine.tuck(cs, f3, Carriage_Pass_Direction.Leftward)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = -2  # rack to right
        self.machine.xfer(f1)  # xfer f1 b3
        self.assertEqual(self.machine.back_loops()[0].position, 3)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertEqual(self.machine.knit_graph.braid_graph.get_crossing(l, r), Crossing_Direction.Under_Right)
        self.machine.rack = 0
        self.machine.xfer(f3.opposite())
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        self.assertEqual(len(self.machine.back_loops()), 0)

    def test_decrease_long_leftward(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f3 = Needle(True, 3)
        self.machine.tuck(cs, f3, Carriage_Pass_Direction.Leftward)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = 2  # rack to left
        self.machine.xfer(f3)
        self.assertEqual(self.machine.back_loops()[0].position, 1)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertEqual(self.machine.knit_graph.braid_graph.get_crossing(l, r), Crossing_Direction.Over_Right)
        self.machine.rack = 0
        self.machine.xfer(f1.opposite())
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        self.assertEqual(len(self.machine.back_loops()), 0)

    def test_twist_cable_leftward(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = -1  # rack to right
        self.machine.xfer(f1)  # xfer f1 b2
        self.assertEqual(self.machine.back_loops()[0].position, 2)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertEqual(self.machine.knit_graph.braid_graph.get_crossing(l, r), Crossing_Direction.Under_Right)
        self.machine.rack = 1
        self.machine.xfer(f2)  # xfer f2 b1
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Under_Right)
        self.machine.rack = 0
        for n in self.machine.back_loops():
            self.machine.xfer(n)

    def test_twist_cable_rightward(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = 1  # rack to left
        self.machine.xfer(f2)  # xfer f2 b1
        self.assertEqual(self.machine.back_loops()[0].position, 1)
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Over_Right)
        self.machine.rack = -1
        self.machine.xfer(f1)  # xfer f1 b2
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Over_Right)
        self.machine.rack = 0
        for n in self.machine.back_loops():
            self.machine.xfer(n)

    def test_1_over_2_rightward_cable(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f3 = Needle(True, 3)
        self.machine.tuck(cs, f3, Carriage_Pass_Direction.Leftward)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = 1
        self.machine.xfer(f3)  # xfer f3 b2
        self.machine.xfer(f2)  # xfer f2 b1
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Over_Right)
        self.machine.rack = -2  # rack to right
        self.machine.xfer(f1)  # xfer f1 b3
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Over_Right)
        self.machine.rack = 0
        self.machine.xfer(f3.opposite())
        self.machine.xfer(f2.opposite())
        self.machine.xfer(f1.opposite())
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Over_Right)

    def test_1_over_2_leftward_cable(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        f3 = Needle(True, 3)
        self.machine.tuck(cs, f3, Carriage_Pass_Direction.Leftward)
        f2 = Needle(True, 2)
        self.machine.tuck(cs, f2, Carriage_Pass_Direction.Leftward)
        f1 = Needle(True, 1)
        self.machine.tuck(cs, f1, Carriage_Pass_Direction.Leftward)
        self.machine.release_hook()
        self.machine.rack = -1
        self.machine.xfer(f1)  # xfer f1 b2
        self.machine.xfer(f2)  # xfer f2 b3
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 1)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Under_Right)
        self.machine.rack = 2
        self.machine.xfer(f3)  # xfer f3 b1
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Under_Right)
        self.machine.rack = 0
        self.machine.xfer(f3.opposite())
        self.machine.xfer(f2.opposite())
        self.machine.xfer(f1.opposite())
        self.assertEqual(len(self.machine.knit_graph.braid_graph.loop_crossing_graph.edges), 2)
        for l, r in self.machine.knit_graph.braid_graph.loop_crossing_graph.edges:
            self.assertTrue(self.machine.knit_graph.braid_graph.get_crossing(l, r) == Crossing_Direction.Under_Right)
