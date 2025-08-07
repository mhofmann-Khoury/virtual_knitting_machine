"""Module containing the Machine Knit Loop Class"""
from __future__ import annotations
from knit_graphs.Loop import Loop
from knit_graphs.Yarn import Yarn

from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import Slider_Loop_Exception, Xfer_Dropped_Loop_Exception
from virtual_knitting_machine.machine_components.needles.Needle import Needle


class Machine_Knit_Loop(Loop):
    """
    An extension of the loop structure to capture information about the machine knitting process that created it.
    """
    def __init__(self, loop_id: int, yarn: Yarn, source_needle: Needle):
        super().__init__(loop_id, yarn)
        self.needle_history: list[Needle | None] = [source_needle]
        if self.source_needle.is_slider:
            raise Slider_Loop_Exception(self.holding_needle)
        self.source_needle.add_loop(self)

    @property
    def holding_needle(self) -> Needle | None:
        """
        :return: The needle currently holding this loop or None if not on a needle.
        """
        return self.needle_history[-1]

    @property
    def last_needle(self) -> Needle:
        """
        :return: The last needle that held this loop before it was dropped.
        """
        for n in reversed(self.needle_history):
            if n is not None:
                return n
        assert False, f"Machine knit loops must have at least a source needle."

    @property
    def on_needle(self) -> bool:
        """
        :return: True if loop is currently on a holding needle.
        """
        return self.holding_needle is not None

    @property
    def dropped(self) -> bool:
        """
        :return: True if loop is not on a holding needle.
        """
        return not self.on_needle

    @property
    def source_needle(self) -> Needle:
        """
        :return: The needle this loop was created on.
        """
        return self.needle_history[0]

    def transfer_loop(self, target_needle: Needle) -> None:
        """
        Add target needle to the end of needle history for loop
        :param target_needle: the needle the loop is transferred to.
        """
        if self.dropped:
            raise Xfer_Dropped_Loop_Exception(target_needle)
        self.needle_history.append(target_needle)

    def drop(self) -> None:
        """
            Marks the loop as dropped by adding None to end of needle history.
        """
        self.needle_history.append(None)
