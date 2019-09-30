import networkx as nx
import matplotlib.pyplot as plt

# data = open("simple-query.csv", "r")
# next(data, None) # Skip csv header

# G = nx.parse_edgelist(data, delimiter=",")

G = nx.Graph()
edgeList = [(1, 6), (1, 7), (1, 8),
            (2, 6), (2, 7), (2, 8),
            (3, 6), (3, 7), (3, 8), (3, 9),
            (4, 7), (4, 8),
            (5, 9)]
G.add_edges_from(edgeList)

bipartition_1 = nx.bipartite.sets(G)[0]
bipartition_2 = nx.bipartite.sets(G)[1]

if len(bipartition_1) < len(bipartition_2):
    V = bipartition_1
    U = bipartition_2
else:
    V = bipartition_2
    U = bipartition_1

G_S = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)

N = G_S.number_of_nodes()
E = G_S.number_of_edges()

k_max = 0 # Max k value of the graph to have at least one edge
for edge in list(G_S.edges.data("weight")):
        if edge[2] > k_max:
            k_max = edge[2]
print("k_max =", k_max)

densitySum = 0

for k in range(1, k_max + 2):
    for edge in list(G_S.edges.data("weight")):
        if edge[2] < k:
            G_S.remove_edge(edge[0], edge[1])
    print("Density @", k, "=", nx.classes.function.density(G_S))
    densitySum += nx.classes.function.density(G_S)

RC = (1 / k_max) * densitySum
print("RC", RC)

# bipartiteLayout = nx.bipartite_layout(G, U, aspect_ratio=0.5, scale=0.2)
# nx.draw_networkx(G, bipartiteLayout, with_labels=True, font_size=10, edge_color="grey")

nx.draw_networkx(G_S, nx.circular_layout(G_S))
nx.draw_networkx_edge_labels(G_S, nx.circular_layout(G_S))

plt.show()
