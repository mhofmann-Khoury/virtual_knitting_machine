"""A Module containing the Needle class and related functions."""
import warnings

from knit_graphs.Pull_Direction import Pull_Direction

from virtual_knitting_machine.knitting_machine_warnings.Needle_Warnings import Needle_Holds_Too_Many_Loops


class Needle:
    """
    A Simple class structure for keeping track of needle locations
    """

    MAX_LOOPS = 4

    def __init__(self, is_front: bool, position: int):
        """
        instantiate a new needle
        :param is_front: True if front bed needle, False otherwise
        :param position: the needle index of this needle
        """
        self._is_front: bool = is_front
        self._position: int = int(position)
        self.held_loops: list = []

    @property
    def pull_direction(self) -> Pull_Direction:
        """
        :return: The direction this needle pulls loops through held loops in a knit operation.
        """
        if self.is_front:
            return Pull_Direction.BtF
        else:
            return Pull_Direction.FtB

    @property
    def is_front(self) -> bool:
        """
        :return: True if needle is on front bed
        """
        return self._is_front

    @property
    def position(self) -> int:
        """
        :return: The index on the machine bed of the needle
        """
        return self._position

    @property
    def has_loops(self) -> bool:
        """
        :return: True if needle is holding loops
        """
        return len(self.held_loops) > 0

    def active_floats(self) -> dict:
        """
        :return: Active floats connecting to loops on this needle.
         Dictionary of loops that are active keyed to active yarn-wise neighbors.
         Each key-value pair represents a directed float where k comes before v on the yarns in the system.
        """
        active_floats = {}
        for loop in self.held_loops:
            next_loop = loop.next_loop_on_yarn()
            if next_loop is not None and next_loop.on_needle:
                active_floats[loop] = next_loop
            prior_loop = loop.prior_loop_on_yarn()
            if prior_loop is not None and prior_loop.on_needle:
                active_floats[prior_loop] = loop
        return active_floats

    def float_overlaps_needle(self, u, v) -> bool:
        """
        :param u: Machine_Knit_Loop at start of float.
        :param v: Machine_Knit_Loop at end of float.
        :return: True if the float between u and v overlaps the position of this needle.
        """
        if not u.on_needle or not v.on_needle:
            return False
        left_position = min(u.holding_needle.position, v.holding_needle.position)
        right_position = max(u.holding_needle.position, v.holding_needle.position)
        return left_position <= self.position <= right_position

    def add_loop(self, loop):
        """
        puts the loop in the set of currently held loops.
        :param loop: loop to add onto needle
        """
        if len(self.held_loops) >= Needle.MAX_LOOPS:
            warnings.warn(Needle_Holds_Too_Many_Loops(self))
        self.held_loops.append(loop)
        loop.yarn.active_loops[loop] = self

    def add_loops(self, loops: list):
        """
        Add loops to the held set
        :param loops: list of loops to place onto needle
        """
        for l in loops:
            self.add_loop(l)

    def transfer_loops(self, target_needle) -> list:
        """
        Transfer loops to target needle.
        :param target_needle: Needle to transfer loops to.
        :return: Loops that were transferred
        """
        xfer_loops = self.held_loops
        for loop in xfer_loops:
            loop.transfer_loop(target_needle)
        self.held_loops = []
        target_needle.add_loops(xfer_loops)
        return xfer_loops

    def drop(self) -> list:
        """
        releases all held loops by resetting the loop-set
        """
        old_loops = self.held_loops
        for loop in old_loops:
            del loop.yarn.active_loops[loop]
            loop.drop()
        self.held_loops = []
        return old_loops

    @property
    def is_back(self) -> bool:
        """
        :return: True if a needle is a back needle
        """
        return not self.is_front

    def opposite(self):
        """
        Return the needle on the opposite bed
        :return: the needle on the opposite bed at the same position
        """
        return Needle(is_front=not self.is_front, position=self.position)

    def offset(self, offset: int):
        """
        Return a needle by the offset value
        :param offset: the amount to offset the needle from
        :return: the needle offset spaces away on the same bed
        """
        return Needle(is_front=self.is_front, position=self.position + offset)

    def racked_position_on_front(self, rack: int) -> int:
        """
        Get the position of the needle on the front bed at a given racking
        :param rack: the racking value
        :return: The front needle position the needle given a racking (no change for front bed needles)
        """
        if self.is_front:
            return self.position
        else:
            return self.position + rack

    def main_needle(self):
        """
        :return: The non-slider needle at this needle positions
        """
        return Needle(is_front=self.is_front, position=self.position)

    def __str__(self):
        if self.is_front:
            return f"f{self.position}"
        else:
            return f"b{self.position}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        if self.is_back:
            return -1 * self.position
        return self.position

    def __lt__(self, other) -> bool:
        if isinstance(other, Needle):
            if self.position < other.position:  # self is left of other
                return True
            elif other.position < self.position:  # other is left of self
                return False
            elif self.is_front and not other.is_front:  # self.position == other.position, front followed by back
                return True
            else:  # same positions, back followed by front or same side
                return False
        elif isinstance(other, int) or isinstance(other, float):
            return self.position < other
        else:
            raise AttributeError

    def __int__(self):
        return self.position

    def __index__(self):
        return int(self)

    def at_racking_comparison(self, other, rack: int = 0, all_needle_racking: bool = False) -> int:
        """
        A comparison value between self and another needle at a given racking.
        :param all_needle_racking: If true, account for front back alignment in all needle knitting.
        :param other: The other needle to compare positions.
        :param rack: Racking value to compare between.
        :return: 1 if self > other, 0 if equal, -1 if self < other.
        """
        assert isinstance(other, Needle)
        self_pos = self.racked_position_on_front(rack)
        other_pos = other.racked_position_on_front(rack)
        if self_pos < other_pos:
            return -1
        elif self_pos > other_pos:
            return 1
        else:  # same position at racking
            if not all_needle_racking or self.is_front == other.is_front:  # same needle
                return 0
            elif self.is_front:  # Self is on the front, implies other is on the back. Front comes before back in all_needle alignment
                return -1
            else:  # implies self is on the back and other is on the front.
                return 1

    @staticmethod
    def needle_at_racking_cmp(n1, n2, racking: int = 0, all_needle_racking: bool = False) -> int:
        """
        A comparison value between self and another needle at a given racking.
        :param all_needle_racking: If true, account for front back alignment in all needle knitting.
        :param n1: First needle in comparison.
        :param n2: Second needle in comparison.
        :param racking: Racking value to compare between.
        :return: 1 if self > other, 0 if equal, -1 if self < other.
        """
        assert isinstance(n1, Needle)
        return n1.at_racking_comparison(n2, racking, all_needle_racking)

    def __add__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position + position)

    def __radd__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position + self.position)

    def __sub__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position - position)

    def __rsub__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position - self.position)

    def __mul__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position * position)

    def __rmul__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position * self.position)

    def __truediv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position / position)

    def __rtruediv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position / self.position)

    def __floordiv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position // position)

    def __rfloordiv__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position // position)

    def __mod__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, self.position % position)

    def __rmod__(self, other):
        position = other
        if isinstance(other, Needle):
            position = other.position
        return Needle(self.is_front, position % self.position)

    def __pow__(self, power, modulo=None):
        position = power
        if isinstance(power, Needle):
            position = power.position
        return Needle(self.is_front, self.position ** position)

    def __rpow__(self, power, modulo=None):
        position = power
        if isinstance(power, Needle):
            position = power.position
        return Needle(self.is_front, position ** self.position)

    def __lshift__(self, other):
        return self - other

    def __rshift__(self, other):
        return self + other

    def __rlshift__(self, other):
        return other - self

    def __rrshift__(self, other):
        return other + self

    def __eq__(self, other):
        assert isinstance(other, Needle), f"Cannot compare needle equality to other types: {type(other)}"
        return self.is_front == other.is_front and self.is_slider == other.is_slider and self.position == other.position

    @property
    def is_slider(self) -> bool:
        """
        :return: True if the needle is a slider
        """
        return False
