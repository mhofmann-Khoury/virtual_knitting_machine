from unittest import TestCase

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.visualizer.knitting_machine_state_visualizer import Knitting_Machine_State_Visualizer


class TestKnitting_Machine_State_Visualizer(TestCase):

    def setUp(self):
        self.machine = Knitting_Machine()

    def render_and_save(self, save_file: str = "test_diagram.svg"):
        """
        Renders the given visualizer and outputs to a svg file.
        Args:
            save_file (str, optional): A path to a file to save the rendered svg file. Defaults to "test_diagram.svg".
        """
        Knitting_Machine_State_Visualizer(self.machine).save(save_file)

    def tuck_needles(
        self,
        needle_range: slice | int,
        is_front: bool = True,
        carrier_id: int = 1,
        direction: Carriage_Pass_Direction = Carriage_Pass_Direction.Leftward,
    ) -> None:
        """
        Tuck loops on the specified needles with the specified carrier and direction.
        Args:
            needle_range (int | slice): The range of needles to tuck.
            is_front (bool, optional): If True, tucks on front bed, otherwise on back bed. Defaults to True.
            carrier_id (int, optional): The carrier id to tuck with. Defaults to 1.
            direction (Carriage_Pass_Direction, optional): The direction to tuck in. Defaults to Leftward
        """
        if isinstance(needle_range, int):
            self.machine.tuck(Yarn_Carrier_Set(carrier_id), Needle(is_front, needle_range), direction)
        else:
            for n in range(
                needle_range.start, needle_range.stop, needle_range.step if needle_range.step is not None else 1
            ):
                self.machine.tuck(Yarn_Carrier_Set(carrier_id), Needle(is_front, n), direction)

    def xfer_to_sliders(self, start_front: bool = True):
        loops = self.machine.front_loops() if start_front else self.machine.back_loops()
        for n in loops:
            self.machine.xfer(n, to_slider=True)

    def test_render_front_needles(self):
        self.machine.in_hook(1)
        self.tuck_needles(2)
        self.machine.release_hook()
        self.render_and_save()

    def test_render_back_needles(self):
        self.machine.in_hook(2)
        self.tuck_needles(slice(7, 4, -1), is_front=False, carrier_id=2)
        self.machine.release_hook()
        self.render_and_save()

    def test_mix_no_sliders(self):

        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
            is_front=False,
        )
        self.machine.release_hook()

        self.tuck_needles(slice(1, 3), is_front=True, direction=Carriage_Pass_Direction.Rightward)
        self.render_and_save()

    def test_loop_stacks_front(self):
        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
            is_front=True,
        )
        self.machine.release_hook()

        self.tuck_needles(slice(4, 7), is_front=True, direction=Carriage_Pass_Direction.Rightward)
        self.tuck_needles(
            6,
            is_front=True,
        )
        self.render_and_save()

    def test_loop_stacks_back_sliders(self):
        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
        )
        self.machine.release_hook()

        self.tuck_needles(slice(4, 7), direction=Carriage_Pass_Direction.Rightward)
        self.tuck_needles(
            6,
        )
        self.xfer_to_sliders()
        self.render_and_save()

    def test_mix_sliders(self):
        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
        )
        self.tuck_needles(slice(4, 7), is_front=False, direction=Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        self.xfer_to_sliders()
        self.render_and_save()

    #
    def test_just_sliders(self):
        self.machine.in_hook(1)
        self.tuck_needles(slice(7, 4, -1), is_front=False)
        self.machine.release_hook()
        self.xfer_to_sliders(start_front=False)
        self.render_and_save()

    def test_all_needle_rack_left(self):
        self.machine.rack = 0.25
        self.machine.in_hook(1)
        self.tuck_needles(2)
        self.machine.release_hook()
        self.render_and_save()

    def test_all_needle_rack_right(self):
        self.machine.rack = 0.25
        self.machine.in_hook(1)
        self.tuck_needles(2)
        self.tuck_needles(2, is_front=False, direction=Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        self.render_and_save()

    def test_positive_rack(self):
        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
            is_front=False,
        )
        self.machine.release_hook()

        self.tuck_needles(slice(1, 3), is_front=True, direction=Carriage_Pass_Direction.Rightward)
        self.machine.rack = 2
        self.render_and_save()

    def test_negative_rack(self):
        self.machine.in_hook(1)
        self.tuck_needles(
            slice(7, 4, -1),
            is_front=False,
        )
        self.machine.release_hook()

        self.tuck_needles(slice(1, 3), is_front=True, direction=Carriage_Pass_Direction.Rightward)
        self.machine.rack = -1
        self.render_and_save()

    def test_hook_position_no_sliders(self):
        self.machine.in_hook(1)
        self.tuck_needles(slice(10, 1, -1), is_front=True, carrier_id=1)
        self.machine.release_hook()
        self.machine.in_hook(2)
        self.tuck_needles(slice(7, 4, -1), is_front=False, carrier_id=2)
        self.render_and_save()

    def test_complex_floats(self):
        self.machine.in_hook(1)
        self.tuck_needles(slice(10, 1, -2), is_front=True, carrier_id=1)
        self.tuck_needles(slice(1, 10, 2), is_front=False, carrier_id=1, direction=Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        self.machine.in_hook(2)
        self.tuck_needles(slice(5, 1, -2), is_front=True, carrier_id=2)
        self.machine.release_hook()
        self.machine.in_hook(3)
        self.tuck_needles(slice(10, 5, -2), is_front=False, carrier_id=3)
        self.tuck_needles(slice(2, 0, -1), is_front=True, carrier_id=3)
        self.machine.release_hook()
        self.render_and_save()

    def test_complex_floats_snapshot(self):
        self.machine.in_hook(1)
        self.tuck_needles(slice(10, 1, -2), is_front=True, carrier_id=1)
        self.tuck_needles(slice(1, 10, 2), is_front=False, carrier_id=1, direction=Carriage_Pass_Direction.Rightward)
        self.machine.release_hook()
        self.machine.in_hook(2)
        self.tuck_needles(slice(5, 1, -2), is_front=True, carrier_id=2)
        self.machine.release_hook()
        self.machine.in_hook(3)
        self.tuck_needles(slice(8, 5, -2), is_front=False, carrier_id=3)
        self.tuck_needles(slice(2, 0, -1), is_front=True, carrier_id=3)
        snapshot = Knitting_Machine_Snapshot(self.machine)
        visualizer = Knitting_Machine_State_Visualizer(snapshot)
        visualizer.save("test_snapshot.svg")
