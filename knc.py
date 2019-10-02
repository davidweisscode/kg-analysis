import networkx as nx
import matplotlib.pyplot as plt

data = open("simple-query.csv", "r")
next(data, None) # Skip csv header
G = nx.parse_edgelist(data, delimiter=",")

# G = nx.Graph()
# edgeList = [(1, 6), (1, 7), (1, 8),
#             (2, 6), (2, 7), (2, 8),
#             (3, 6), (3, 7), (3, 8), (3, 9),
#             (4, 7), (4, 8),
#             (5, 9)]
# G.add_edges_from(edgeList)

coloring = nx.greedy_color(G)
colorList = []
for node in G.nodes():
    if coloring[node] == 0:
        colorList.append("red")
    else:
        colorList.append("green")

bipartition_1, bipartition_2 = nx.bipartite.sets(G)
if len(bipartition_1) > len(bipartition_2):
    U, V = bipartition_2, bipartition_1
else:
    U, V = bipartition_1, bipartition_2

G_U = nx.algorithms.bipartite.projection.weighted_projected_graph(G, U)
G_V = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)

# Max k value of the graph to have at least one edge
k_max_U = G_V.number_of_nodes()
k_max_V = G_U.number_of_nodes()

print("k_max_U =", k_max_U)
print("k_max_V =", k_max_V)

G_U_1 = G_U.copy()
G_V_1 = G_V.copy()

print("\nKNC for U")
densitySum = 0
knc_list_U = []
for k in range(1, k_max_U + 1):
    for edge in list(G_U.edges.data("weight")):
        if edge[2] < k:
            G_U.remove_edge(edge[0], edge[1])
    # print("Density @ k:", k, "=", nx.classes.function.density(G_U))
    knc_list_U.append((k/k_max_U, nx.classes.function.density(G_U)))
    densitySum += nx.classes.function.density(G_U)
print(knc_list_U)

RC_U = (1 / k_max_U) * densitySum
print("RC_U =", RC_U)

print("\nKNC for V")
densitySum = 0
knc_list_V = []
for k in range(1, k_max_V + 1):
    for edge in list(G_V.edges.data("weight")):
        if edge[2] < k:
            G_V.remove_edge(edge[0], edge[1])
    # print("Density @ k:", k, "=", nx.classes.function.density(G_V))
    knc_list_V.append((k/k_max_V, nx.classes.function.density(G_V)))
    densitySum += nx.classes.function.density(G_V)
print(knc_list_V)

RC_V = (1 / k_max_V) * densitySum
print("RC_V =", RC_V)

plt.subplot(221, frameon=False)
bipartiteLayout = nx.bipartite_layout(G, U, aspect_ratio=0.5, scale=0.2)
nx.draw_networkx(G, bipartiteLayout, with_labels=True, font_size=10, node_color=colorList, edge_color="grey")

plt.subplot(223, frameon=False)
nx.draw_networkx(G_U_1, nx.circular_layout(G_U_1), with_labels=True, node_color="red", edge_color="grey")
nx.draw_networkx_edge_labels(G_U_1, nx.circular_layout(G_U_1))

plt.subplot(224, frameon=False)
nx.draw_networkx(G_V_1, nx.circular_layout(G_V_1), with_labels=False, node_color="green", edge_color="grey")
# nx.draw_networkx_edge_labels(G_V_1, nx.circular_layout(G_V_1))

plt.subplot(222, frameon=False)
plt.plot(*zip(*knc_list_U), color="red")
plt.plot(*zip(*knc_list_V), color="green")

plt.show()
