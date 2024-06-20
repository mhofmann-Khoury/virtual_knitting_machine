"""Yarn_Carrier representation"""
import warnings

from knit_graphs.Yarn import Yarn_Properties

from virtual_knitting_machine.knitting_machine_exceptions.Yarn_Carrier_Error_State import Change_Active_Yarn_Exception, Hooked_Carrier_Exception
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import In_Active_Carrier_Warning, Out_Inactive_Carrier_Warning
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn


class Yarn_Carrier:
    """
        Carrier on a knitting machine
    """

    def __init__(self, carrier_id: int, yarn: None | Machine_Knit_Yarn = None, yarn_properties: Yarn_Properties | None = None):
        self._carrier_id: int = carrier_id
        self._is_active: bool = False
        self._is_hooked: bool = False
        self._position: None | int = None
        if yarn is not None:
            self._yarn = yarn
        elif yarn_properties is None:
            self.yarn = Yarn_Properties.default_yarn()
        else:
            self.yarn = yarn_properties

    @property
    def yarn(self) -> Machine_Knit_Yarn:
        """
        :return: The Yarn held on this carrier
        """
        return self._yarn

    @yarn.setter
    def yarn(self, yarn_properties: Yarn_Properties):
        if self.is_active:
            raise Change_Active_Yarn_Exception(self.carrier_id)
        self._yarn: Machine_Knit_Yarn = Machine_Knit_Yarn(self, yarn_properties)

    @property
    def position(self) -> None | int:
        """
        :return: The needle position that the carrier sits at or None if the carrier is not active
        """
        return self._position

    @position.setter
    def position(self, new_position: None | Needle | int):
        if new_position is None:
            self._position = None
        else:
            self._position = int(new_position)

    @property
    def is_active(self) -> bool:
        """
        :return: True if active
        """
        return self._is_active

    @is_active.setter
    def is_active(self, active_state: bool):
        if active_state is True:
            self._is_active = True
        else:
            self._is_active = False
            self.is_hooked = False
            self.position = None

    @property
    def is_hooked(self) -> bool:
        """
        :return: True if connected to inserting hook
        """
        return self._is_hooked

    @is_hooked.setter
    def is_hooked(self, hook_state: bool):
        self._is_hooked = hook_state

    def bring_in(self):
        """
            Record in operation
        """
        if self.is_active:
            warnings.warn(In_Active_Carrier_Warning(self.carrier_id))  # Warn user but do no in action
        self.is_active = True

    def inhook(self):
        """
            Record inhook operation
        """
        self.bring_in()
        self.is_hooked = True

    def releasehook(self):
        """
            Record release hook operation
        """
        self.is_hooked = False

    def out(self):
        """
            Record out operation
        """
        if not self.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(self.carrier_id))  # Warn use but do not do out action
        self.is_active = False

    def outhook(self):
        """
        Record outhook operation. Raise exception if already on yarn inserting hook
        """
        if self.is_hooked:
            raise Hooked_Carrier_Exception(self.carrier_id)
        else:
            self.out()

    @property
    def carrier_id(self) -> int:
        """
        :return: id of carrier, corresponds to order in machine
        """
        return self._carrier_id

    def __lt__(self, other):
        return self.carrier_id < other.carrier_id

    def __hash__(self):
        return self.carrier_id

    def __str__(self):
        if self.yarn.yarn_id == str(self._carrier_id):
            return str(self.carrier_id)
        else:
            return f"{self.carrier_id}:{self.yarn}"

    def __repr__(self):
        return str(self)

    def __int__(self):
        return self.carrier_id
