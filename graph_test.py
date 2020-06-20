
import networkx as nx

equiv_nodes = {
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

def getNode(stroke):
    try:
        return equiv_nodes[stroke]
    except KeyError:
        return (stroke)

disconnected_nodes = [
        ("O"),
        ("U"),
        getNode("PNT"),
        getNode("DF")
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
        ("M", "NG"),
        ("NK", "MN"),
        ("SH", "S"),
        ("S", "SS"),
        ("S", "XS"),
        ("SS", "XS"),
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

trans_edges = [(getNode(edge[0]), getNode(edge[1])) for edge in edges]

g = nx.Graph()
g.add_edges_from(trans_edges)
g.add_nodes_from(disconnected_nodes)


# print(g.nodes)
# print(g.edges)
# print([a for a in nx.neighbors(g, getNode("S"))])


def getNeighbors(stroke, distance):
    neighbors = set()
    start = getNode(stroke)
    neighbors.add(start)
    while distance > 0:
        new = list()
        for node in neighbors:
            new += nx.neighbors(g, node)
        neighbors |= set([item for item in new])
        distance -= 1

    return neighbors

print(getNeighbors("DN", 2))
print("|".join(getNeighbors("S", 2)))



