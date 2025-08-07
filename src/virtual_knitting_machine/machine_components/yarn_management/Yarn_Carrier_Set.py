"""
    Representation of a Yarn Carrier on the machine
"""
from __future__ import annotations
import warnings
from typing import Iterator

from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import Duplicate_Carriers_In_Set
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Insertion_System import Yarn_Insertion_System


class Yarn_Carrier_Set:
    """
    A structure to represent the location of a Yarn_carrier
    ...

    Attributes
    ----------
    """

    def __init__(self, carrier_ids: list[int | Yarn_Carrier] | int | Yarn_Carrier):
        """
        Represents the state of the yarn_carriage
        :param carrier_ids: The carrier_id for this yarn
        """
        if isinstance(carrier_ids, list):
            duplicates = set()
            self._carrier_ids: list[int] = []
            for c in carrier_ids:
                if int(c) in duplicates:
                    warnings.warn(Duplicate_Carriers_In_Set(c, carrier_ids))
                else:
                    duplicates.add(int(c))
                    self._carrier_ids.append(int(c))
        else:
            self._carrier_ids: list[int] = [int(carrier_ids)]

    def positions(self, carrier_system: Yarn_Insertion_System) -> list[None | int]:
        """
        :param carrier_system: The carrier system to reference position data from.
        :return: The list of positions of each carrier in the carrier set.
        """
        return [c.position for c in self.get_carriers(carrier_system)]

    def get_carriers(self, carrier_system: Yarn_Insertion_System) -> list[Yarn_Carrier]:
        """
        :param carrier_system: carrier system referenced by set.
        :return: carriers that correspond to the ids in the carrier set.
        """
        carriers = carrier_system[self]
        if not isinstance(carriers, list):
            carriers = [carriers]
        return carriers

    def position_carriers(self, carrier_system: Yarn_Insertion_System, position: Needle | int | None) -> None:
        """
        Set the position of involved carriers to the given position.
        :param carrier_system: Carrier system referenced by set.
        :param position: The position to move the carrier set to. If None, this means the carrier is not active.
        """
        for carrier in self.get_carriers(carrier_system):
            carrier.position = position

    @property
    def carrier_ids(self) -> list[int]:
        """
        :return: the id of this carrier
        """
        return self._carrier_ids

    @property
    def many_carriers(self) -> bool:
        """
        :return: True if this carrier set involves multiple carriers
        """
        return len(self.carrier_ids) > 1

    def __str__(self) -> str:
        carriers = str(self.carrier_ids[0])
        for cid in self.carrier_ids[1:]:
            carriers += f" {cid}"
        return carriers

    def __hash__(self) -> int:
        if len(self.carrier_ids) == 1:
            return self.carrier_ids[0]
        else:
            return hash(str(self))

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: None | Yarn_Carrier | int | list[Yarn_Carrier | int] | Yarn_Carrier_Set) -> bool:
        if other is None:
            return False
        elif isinstance(other, Yarn_Carrier) or isinstance(other, int):
            if len(self.carrier_ids) != 1:
                return False
            return self.carrier_ids[0] == int(other)
        elif len(self) != len(other):
            return False
        return any(c != int(other_c) for c, other_c in zip(self, other))

    def __iter__(self) -> Iterator[int]:
        return iter(self.carrier_ids)

    def __getitem__(self, item: int | slice | Yarn_Carrier) -> int | list[int]:
        if isinstance(item, Yarn_Carrier):
            item = int(item)
        return self.carrier_ids[item]

    def __len__(self) -> int:
        return len(self.carrier_ids)

    def __contains__(self, carrier_id: int | Yarn_Carrier) -> bool:
        return int(carrier_id) in self.carrier_ids

    def carrier_DAT_ID(self) -> int:
        """
        :return: Number used in DAT files to represent the carrier set
        """
        carrier_id = 0
        for place, carrier in enumerate(reversed(self.carrier_ids)):
            multiplier = 10 ** place
            carrier_val = multiplier * carrier
            carrier_id += carrier_val
        return carrier_id
