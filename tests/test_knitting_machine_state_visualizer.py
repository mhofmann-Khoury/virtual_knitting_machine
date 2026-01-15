from unittest import TestCase

from resources.mock_machine_state import Mock_Machine_State

from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.visualizer.knitting_machine_state_visualizer import Knitting_Machine_State_Visualizer


class TestKnitting_Machine_State_Visualizer(TestCase):

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
        state = Mock_Machine_State({1: [Needle(is_front=True, position=n) for n in range(2, 3)]})
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_render_back_needles(self):
        state = Mock_Machine_State({1: [Needle(is_front=False, position=n) for n in range(4, 6)]})
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_no_sliders(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=True, position=n) for n in range(3, 4)],
                2: [Needle(is_front=False, position=n) for n in range(7, 10)],
            }
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_sliders(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=True, position=n) for n in range(3, 4)],
                2: [Slider_Needle(is_front=False, position=n) for n in range(7, 10)],
            }
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_just_sliders(self):
        state = Mock_Machine_State({1: [Slider_Needle(is_front=True, position=n) for n in range(7, 10)]})
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_all_needle_rack(self):
        state = Mock_Machine_State({1: [Needle(is_front=True, position=n) for n in range(2, 3)]}, all_needle_rack=True)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_mix_sliders_all_needle(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=True, position=n) for n in range(3, 4)],
                2: [Slider_Needle(is_front=False, position=n) for n in range(7, 10)],
            },
            all_needle_rack=True,
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_positive_rack(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=False, position=n) for n in range(2, 3)],
                2: [Needle(is_front=True, position=n) for n in range(2, 3)],
            },
            rack=2,
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_negative_rack(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=False, position=n) for n in range(2, 3)],
                2: [Needle(is_front=True, position=n) for n in range(2, 3)],
            },
            rack=-1,
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_positive_rack_all_needle(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=False, position=n) for n in range(2, 3)],
                2: [Needle(is_front=True, position=n) for n in range(2, 3)],
            },
            rack=2,
            all_needle_rack=True,
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_negative_rack_all_needle(self):
        state = Mock_Machine_State(
            {
                1: [Needle(is_front=False, position=n) for n in range(2, 3)],
                2: [Needle(is_front=True, position=n) for n in range(2, 3)],
            },
            rack=-1,
            all_needle_rack=True,
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_cross_bed(self):
        state = Mock_Machine_State(
            {1: [Needle(is_front=False, position=2), Needle(is_front=True, position=3)]},
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_hook_position_no_sliders(self):
        state = Mock_Machine_State({1: [Needle(is_front=True, position=n) for n in range(2, 6)]}, hook_position=3)
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)

    def test_hook_position_sliders(self):
        state = Mock_Machine_State(
            {1: [Slider_Needle(is_front=True, position=n) for n in range(2, 6)]}, hook_position=4
        )
        visualizer = Knitting_Machine_State_Visualizer(state)
        self.render_and_save(visualizer)
