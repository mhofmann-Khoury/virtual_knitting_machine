"""Representation of a needle bed on a machine"""
from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import Non_Existent_Needle_Exception
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Sheet_Needle import Sheet_Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop


class Needle_Bed:
    """
    A structure to hold information about loops held on one bed of needles...
    increasing indices indicate needles moving from left to right
        i.e., LEFT -> 0 1 2....N <- RIGHT of Machine
    Attributes
    ----------
    needles: List[Needle]
        The needles on this bed ordered from 0 to max
    sliders: List[Slider_Needle]
        The slider needles on this bed ordered from 0 to max
    """
    MAX_LOOPs = 4

    def __init__(self, is_front: bool, needle_count: int = 250):
        """
        A representation of the state of a bed on the machine.
        :param is_front: True if this is the front bed, false if it is the back bed.
        :param needle_count: The number of needles that are on this bed.
        """
        self._is_front: bool = is_front
        self._needle_count: int = needle_count
        self.needles: list[Needle] = [Needle(self._is_front, i) for i in range(0, self.needle_count)]
        self.sliders: list[Slider_Needle] = [Slider_Needle(self._is_front, i) for i in range(0, self.needle_count)]
        self._active_sliders: set[Slider_Needle] = set()

    def __iter__(self):
        return iter(self.needles)

    def loop_holding_needles(self) -> list[Needle]:
        """
        :return: List of needles on bed that actively hold loops
        """
        return [n for n in self if n.has_loops]

    def loop_holding_sliders(self) -> list[Slider_Needle]:
        """
        :return: List of sliders on bed that actively hold loops
        """
        return [s for s in self.sliders if s.has_loops]

    @property
    def needle_count(self) -> int:
        """
        :return: the number of needles on the bed
        """
        return self._needle_count

    def __len__(self):
        return self.needle_count

    @property
    def is_front(self) -> bool:
        """
        :return: true if this is the front bed
        """
        return self._is_front

    def add_loops(self, needle: Needle, loops: list[Machine_Knit_Loop], drop_prior_loops: bool = True) -> list[Machine_Knit_Loop]:
        """
        Puts the loop_id on given needle, overrides existing loops as if a knit operation took place
        :param loops: the loops to put on the needle if not creating with the yarn carrier
        :param needle: the needle to add the loops on
        :param drop_prior_loops: If true, any loops currently held on this needle are dropped
        :return Returns the list of loops made with the carrier on this needle
        """
        needle = self[needle]  # make sure needle instance is the one in the machine bed state
        if drop_prior_loops:
            self.drop(needle)
        needle.add_loops(loops)
        if isinstance(needle, Slider_Needle):
            self._active_sliders.add(needle)
        for loop in loops:
            assert loop.holding_needle == needle, f"Needle must be recorded in loop history"
        return loops

    def drop(self, needle: Needle) -> list[Machine_Knit_Loop]:
        """
        Clears the loops held at this position as though a drop operation has been done
        :param needle: The position to drop loops from main and slider needles
        :return list of loops that were dropped
        """
        needle = self[needle]  # make sure the correct needle instance in machine bed state is used
        loops = [l for l in needle.held_loops]
        needle.drop()
        return loops

    def __getitem__(self, item: Machine_Knit_Loop | Needle | slice | Sheet_Needle) -> Needle | list[Needle] | None:
        """
        Gets an indexed needle on the bed.
        :param item: The needle position to get a loop from.
        :return: The loop_id held at that position.
        """
        if isinstance(item, slice):
            return self.needles[item]
        elif isinstance(item, Machine_Knit_Loop):
            return self.get_needle_of_loop(item)
        elif isinstance(item, Sheet_Needle) or isinstance(item, Needle):
            if item.position < 0 or item.position >= self.needle_count:
                raise Non_Existent_Needle_Exception(item)
            if item.is_slider:
                return self.sliders[item.position]
            else:
                return self.needles[item.position]

    def get_needle_of_loop(self, loop: Machine_Knit_Loop) -> None | Needle:
        """
        Gets the needle that currently holds the loop.
        :param loop: The loop being searched for.
        :return: None if the bed does not hold the loop, otherwise the needle position that holds it.
        """
        needle = self[loop.holding_needle]
        assert loop in needle.held_loops, f"Loop and needle meta data mismatch"
        return needle

    def sliders_are_clear(self):
        """
        :return: True if no loops are on a slider needle
        """
        return len(self._active_sliders) == 0
