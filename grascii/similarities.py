"""Contains methods for determining the similarity of grascii strokes."""

from __future__ import annotations

from typing import Dict, Hashable, Iterable, List, Set, Tuple, cast

_equiv_nodes: Dict[str, Tuple[str, ...]] = {
    "S": ("S", "Z"),
    "Z": ("S", "Z"),
    "TD": ("TD", "DT", "DD"),
    "DT": ("TD", "DT", "DD"),
    "DD": ("TD", "DT", "DD"),
    "MN": ("MN", "MM"),
    "MM": ("MN", "MM"),
    "TN": ("TN", "DN"),
    "DN": ("TN", "DN"),
    "TM": ("TM", "DM"),
    "DM": ("TM", "DM"),
    "NT": ("NT", "ND"),
    "ND": ("NT", "ND"),
    "MT": ("MT", "MD"),
    "MD": ("MT", "MD"),
    "DF": ("DF", "DV", "TV"),
    "DV": ("DF", "DV", "TV"),
    "TV": ("DF", "DV", "TV"),
    "PNT": ("PNT", "PND", "JNT", "JND"),
    "PND": ("PNT", "PND", "JNT", "JND"),
    "JNT": ("PNT", "PND", "JNT", "JND"),
    "JND": ("PNT", "PND", "JNT", "JND"),
}


def get_node(stroke: str) -> Tuple[str, ...]:
    """Get a tuple of all strokes equivalent to the given stroke."""
    return _equiv_nodes.get(stroke, (stroke,))


_disconnected_nodes: List[Hashable] = [("O",), ("U",), get_node("PNT"), get_node("DF")]

_edges: List[Tuple[str, str]] = [
    ("K", "G"),
    ("R", "L"),
    ("L", "LD"),
    ("T", "D"),
    ("D", "DT"),
    ("I", "A"),
    ("I", "A&'"),
    ("I", "A&E"),
    ("A", "E"),
    ("A", "A&'"),
    ("A", "A&E"),
    ("A&'", "A&E"),
    ("NK", "N"),
    ("N", "M"),
    ("M", "MN"),
    ("N", "NG"),
    ("M", "NK"),
    ("NG", "NK"),
    ("M", "NG"),
    ("NK", "MN"),
    ("SH", "S"),
    ("S", "SS"),
    ("S", "XS"),
    ("SS", "XS"),
    ("XS", "X"),
    ("X", "S"),
    ("S", "F"),
    ("F", "V"),
    ("SH", "CH"),
    ("F", "CH"),
    ("V", "J"),
    ("CH", "J"),
    ("CH", "P"),
    ("S", "P"),
    ("P", "B"),
    ("J", "B"),
    ("TH", "TN"),
    ("TN", "TM"),
    ("NT", "MT"),
    ("TH", "NT"),
]

_trans_edges: List[Tuple[Hashable, Hashable]] = [
    (get_node(edge[0]), get_node(edge[1])) for edge in _edges
]


class _SimilarityGraph:
    """Implements a basic graph with the capability of doing an n-layered
    breadth-first search."""

    def __init__(self):
        self.nodes = {}

    def add_node(self, node: Hashable) -> None:
        """Add a node to the graph.

        :param node: An object that can be used as a dict key.
        """

        if node not in self.nodes:
            self.nodes[node] = set()

    def add_edge(self, edge: Tuple[Hashable, Hashable]) -> None:
        """Add an edge to the graph. If either node does not exist
        in the graph, it is added.

        :param edge: Two objects that can be used as a dict key.
        """

        assert len(edge) > 1
        self.add_node(edge[0])
        self.nodes[edge[0]].add(edge[1])
        self.add_node(edge[1])
        self.nodes[edge[1]].add(edge[0])

    def add_nodes(self, nodes: Iterable[Hashable]) -> None:
        """Add a collection of nodes to the graph.

        :param nodes: A collection of objects that can be used as a dict key.
        """

        for node in nodes:
            self.add_node(node)

    def add_edges(self, edges: Iterable[Tuple[Hashable, Hashable]]) -> None:
        """Add a collection of edges to the graph.

        :param nodes: A collection of edges.
        """

        for edge in edges:
            self.add_edge(edge)

    def get_similar(self, node: Hashable, similarity: int) -> Set[Hashable]:
        """Get a set of all nodes within a distance of similarity to the
        given node.

        :param node: The node to get similars for.
        :param similarity: A distance
        :returns: A set of nodes
        """

        similars = set()
        similars.add(node)
        while similarity > 0:
            new = []
            for node in similars:
                new += self.nodes.get(node, list())
            similars |= set(new)
            similarity -= 1

        return similars


_sg = _SimilarityGraph()
_sg.add_edges(_trans_edges)
_sg.add_nodes(_disconnected_nodes)


def get_similar(stroke: str, distance: int) -> Set[Tuple]:
    """Get a set of all strokes within a distance to the
    given node.

    :param stroke: The stroke to get similars for.
    :param distance: The maximum distance of similar strokes.
    :returns: A set of strokes grouped by equivalency.
    """

    return cast(Set[Tuple], _sg.get_similar(get_node(stroke), distance))
