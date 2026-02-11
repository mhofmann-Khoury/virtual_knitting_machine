from unittest import TestCase

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set


class TestKnitting_Machine_Snapshot(TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.spec = Knitting_Machine_Specification()
        self.machine = Knitting_Machine(self.spec)

    @property
    def _snapshot(self) -> Knitting_Machine_Snapshot:
        return Knitting_Machine_Snapshot(self.machine)

    def test_tucks(self):
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.carrier_system.active_carriers), 0)
        self.assertIsNone(snapshot.carrier_system.hooked_carrier)
        self.machine.in_hook(1)
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.carrier_system.active_carriers), 1)
        self.assertEqual(snapshot.carrier_system.hooked_carrier, 1)
        cs = Yarn_Carrier_Set(1)
        for i in range(9, -1, -2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Leftward)
        snapshot = self._snapshot
        self.assertEqual(snapshot.carrier_system[1].slot_number, 1)
        self.assertEqual(len(snapshot.front_loops()), 5)
        for i in range(0, 10, 2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Rightward)
        snapshot = self._snapshot
        self.assertEqual(snapshot.carrier_system[1].slot_number, 8)
        self.assertEqual(len(snapshot.front_loops()), 10)
        self.machine.release_hook()
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.carrier_system.active_carriers), 1)
        self.assertIsNone(snapshot.carrier_system.hooked_carrier)

    def test_stst(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        for i in range(9, -1, -2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Leftward)
        for i in range(0, 10, 2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        for _ in range(0, 4):
            for n in Carriage_Pass_Direction.Leftward.sort_needles(self.machine.front_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Leftward)
            for n in Carriage_Pass_Direction.Rightward.sort_needles(self.machine.front_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Rightward)
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.front_loops()), 10)
        self.assertIn(cs, snapshot)

    def test_rib(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        for i in range(9, -1, -2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Leftward)
        for i in range(0, 10, 2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        for n in self.machine.front_loops()[1::2]:
            self.machine.xfer(n)
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.front_loops()), 5)
        self.assertEqual(len(snapshot.back_loops()), 5)
        for _ in range(0, 4):
            for n in Carriage_Pass_Direction.Leftward.sort_needles(self.machine.all_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Leftward)
            for n in Carriage_Pass_Direction.Rightward.sort_needles(self.machine.all_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Rightward)
        self.assertEqual(len(self._snapshot.all_loops()), 10)

    def test_seed(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        for i in range(9, -1, -2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Leftward)
        for i in range(0, 10, 2):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        for n in self.machine.front_loops()[1::2]:
            self.machine.xfer(n)
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.front_loops()), 5)
        self.assertEqual(len(snapshot.back_loops()), 5)
        for _ in range(0, 4):
            for n in Carriage_Pass_Direction.Leftward.sort_needles(self.machine.all_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Leftward)
            for n in self.machine.all_loops():
                self.machine.xfer(n)
            for n in Carriage_Pass_Direction.Rightward.sort_needles(self.machine.all_loops()):
                self.machine.knit(cs, n, Carriage_Pass_Direction.Rightward)
            for n in self.machine.all_loops():
                self.machine.xfer(n)
        self.assertEqual(len(self._snapshot.all_loops()), 10)

    def test_cable(self):
        self.machine.in_hook(1)
        cs = Yarn_Carrier_Set(1)
        for i in range(4, -1, -1):
            self.machine.tuck(cs, self.machine.get_specified_needle(True, i), Carriage_Pass_Direction.Leftward)
        for n in self.machine.front_loops():
            self.machine.knit(cs, n, Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        self.machine.update_rack(1, 2)
        self.machine.xfer(self.machine.get_specified_needle(True, 1))
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.back_loops()), 1)
        self.assertEqual(snapshot.back_loops()[0].position, 2)
        self.machine.update_rack(2, 1)
        self.machine.xfer(self.machine.get_specified_needle(True, 2))
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.back_loops()), 2)
        self.assertEqual(snapshot.back_loops()[0].position, 1)
        self.assertEqual(snapshot.back_loops()[1].position, 2)
        self.rack = 0
        for n in self.machine.back_loops():
            self.machine.xfer(n)
        snapshot = self._snapshot
        self.assertEqual(len(snapshot.back_loops()), 0)
        self.assertEqual(len(snapshot.front_loops()), 4)
