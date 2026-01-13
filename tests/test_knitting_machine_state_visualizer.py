from typing import Iterable
from unittest import TestCase

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.visualizer.knitting_machine_state_visualizer import Knitting_Machine_State_Visualizer
from virtual_knitting_machine.visualizer.machine_state_protocol import Mock_Machine_State


class TestKnitting_Machine_State_Visualizer(TestCase):

    @staticmethod
    def get_mock_state(
        front_needles: Iterable[int] | None = None,
        back_needles: Iterable[int] | None = None,
        front_sliders: Iterable[int] | None = None,
        back_sliders: Iterable[int] | None = None,
        rack: int = 0,
        all_needle_rack: bool = False,
    ) -> Mock_Machine_State:
        """
        Args:
            front_needles (Iterable[int], optional): An iterable over the slot numbers of active front needles. Defaults to having no active front needles.
            back_needles (Iterable[int], optional): An iterable over the slot numbers of active back needles. Defaults to having no active back needles.
            front_sliders (Iterable[int], optional): An iterable over the slot numbers of active front sliders. Defaults to having no active front sliders.
            back_sliders (Iterable[int], optional): An iterable over the slot numbers of active back sliders. Defaults to having no active back sliders.
            rack (int, optional): A racking offset. Defaults to 0.
            all_needle_rack (bool, optional): A boolean to indicate if all needle racking. Defaults to False.

        Returns:
            Mock_Machine_State: A Mock machine state based on the given values.
        """
        all_needles = [Needle(is_front=True, position=n) for n in front_needles] if front_needles is not None else []
        all_needles.extend(
            [Slider_Needle(is_front=True, position=n) for n in front_sliders] if front_sliders is not None else []
        )
        all_needles.extend(
            [Needle(is_front=False, position=n) for n in back_needles] if back_needles is not None else []
        )
        all_needles.extend(
            [Slider_Needle(is_front=False, position=n) for n in back_sliders] if back_sliders is not None else []
        )
        return Mock_Machine_State(all_needles, rack, all_needle_rack)

    @staticmethod
    def render_and_save(
        visualizer: Knitting_Machine_State_Visualizer, save_file: str = "test_diagram.svg", print_svg: bool = True
    ):
        """
        Renders the given visualizer and outputs to a svg file.
        Args:
            visualizer (Knitting_Machine_State_Visualizer): The visualizer to render.
            save_file (str, optional): A path to a file to save the rendered svg file. Defaults to "test_diagram.svg".
            print_svg (bool, optional): If True, prints the svg to console. Defaults to True.
        """
        visualizer.render()
        visualizer.save(save_file)
        if print_svg:
            print(visualizer.get_svg_string())

    def test_render_front_needles(self):
        state = self.get_mock_state(front_needles=range(1, 3))
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_render_back_needles(self):
        state = self.get_mock_state(back_needles=range(4, 6))
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_no_sliders(self):
        state = self.get_mock_state(front_needles=range(3, 4), back_needles=range(7, 10))
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_sliders(self):
        state = self.get_mock_state(front_needles=range(3, 4), back_sliders=range(7, 10))
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_all_needle_rack(self):
        state = self.get_mock_state(front_needles=range(1, 3), all_needle_rack=True)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_sliders_all_needle(self):
        state = self.get_mock_state(front_needles=range(3, 4), back_sliders=range(7, 10), all_needle_rack=True)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_positive_rack(self):
        state = self.get_mock_state(front_needles=range(1, 3), rack=2)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_negative_rack(self):
        state = self.get_mock_state(front_needles=range(1, 3), rack=-1)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_positive_rack_all_needle(self):
        state = self.get_mock_state(front_needles=range(1, 3), rack=2, all_needle_rack=True)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_negative_rack_all_needle(self):
        state = self.get_mock_state(front_needles=range(1, 3), rack=-1, all_needle_rack=True)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)
