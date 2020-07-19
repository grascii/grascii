
equiv_nodes = {
    "S" : ("S", "Z"),
    "Z" : ("S", "Z"),
    "TD" : ("TD", "DT", "DD"),
    "DT" : ("TD", "DT", "DD"),
    "DD" : ("TD", "DT", "DD"),
    "MN" : ("MN", "MM"),
    "MM" : ("MN", "MM"),
    "TN" : ("TN", "DN"),
    "DN" : ("TN", "DN"),
    "TM" : ("TM", "DM"),
    "DM" : ("TM", "DM"),
    "NT" : ("NT", "ND"),
    "ND" : ("NT", "ND"),
    "MT" : ("MT", "MD"),
    "MD" : ("MT", "MD"),
    "DF" : ("DF", "DV", "TV"),
    "DV" : ("DF", "DV", "TV"),
    "TV" : ("DF", "DV", "TV"),
    "PNT" : ("PNT", "PND", "JNT", "JND"),
    "PND" : ("PNT", "PND", "JNT", "JND"),
    "JNT" : ("PNT", "PND", "JNT", "JND"),
    "JND" : ("PNT", "PND", "JNT", "JND"),
    }

def get_node(stroke):
    return equiv_nodes.get(stroke, (stroke,))

disconnected_nodes = [
    ("O",),
    ("U",),
    get_node("PNT"),
    get_node("DF")
    ]

edges = [
    ("K", "G"),
    ("R", "L"),
    ("L", "LD"),
    ("T", "D"),
    ("D", "DT"),
    ("I", "A"),
    ("A", "E"),
    ("NK", "N"),
    ("N", "M"),
    ("M", "MN"),
    ("N", "NG"),
    ("M", "NK"),
    ("NG", "NK"),
    ("M", "NG"), # add to graph
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

trans_edges = [(get_node(edge[0]), get_node(edge[1])) for edge in edges]

class SimilarityGraph():

    def __init__(self):
        self.nodes = dict()

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = set()

    def add_edge(self, edge):
        assert len(edge) > 1
        self.add_node(edge[0])
        self.nodes[edge[0]].add(edge[1])
        self.add_node(edge[1])
        self.nodes[edge[1]].add(edge[0])

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge)

    def get_similar(self, node, similarity):
        similars = set()
        similars.add(node)
        while similarity > 0:
            new = list()
            for node in similars:
                new += self.nodes[node]
            similars |= set(new)
            similarity -= 1

        return similars

sg = SimilarityGraph()
sg.add_edges(trans_edges)
sg.add_nodes(disconnected_nodes)

def get_similar(stroke, distance):
    return sg.get_similar(get_node(stroke), distance)

