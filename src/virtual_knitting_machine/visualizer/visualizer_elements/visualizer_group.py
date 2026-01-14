"""
Module containing the Visualizer_Group class.
"""

from svgwrite.container import Group

from virtual_knitting_machine.visualizer.visualizer_elements.visualizer_element import Visualizer_Element


class Visualizer_Group(Visualizer_Element):
    """
    A wrapper for SVG Groups. The coordinate position of the group is used to set each of its children to a relative position.

    Attributes:
        children (set[Visualizer_Element]): A list of Visualizer_Element objects that are children of the group.
    """

    def __init__(self, x: int, y: int, name: str):
        super().__init__(x, y, name)
        self.children: list[Visualizer_Element] = []

    def _build_svg_element(self) -> Group:
        group = Group(id=self.name)
        for child in self.children:
            child_element = child._build_svg_element()
            group.add(child_element)
        return group

    def add_child(self, child: Visualizer_Element) -> None:
        """
        Add the given child element as a sub element to this element.
        Args:
            child (Visualizer_Element): The child element to add.
        """
        self.children.append(child)
        child.parent = self

    def __getitem__(self, element_id: str) -> Visualizer_Element:
        """
        Args:
            element_id (str): The id of the element to retrieve.

        Returns:
            Visualizer_Element: The retrieved element.

        Raises:
            KeyError: The element does not exist in this group.
        """
        element = next((c for c in self.children if c.name == element_id), None)
        if element is None:
            raise KeyError(f"No element with name {element_id} in {self}")
        return element

    def __contains__(self, element_id: str) -> bool:
        """
        Args:
            element_id (str): The id of a sub-element to this element.

        Returns:
            bool: True if this element contains a sub element with the given id. False otherwise.
        """
        return any(e.name == element_id for e in self.children)
