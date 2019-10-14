#!/usr/bin/python3

import sys
import networkx as nx
import matplotlib.pyplot as plt
import time

start_time = time.time()

CL_RED = "#e13232"
CL_GREEN = "#32c832"

inputfile = sys.argv[1]
data = open(inputfile, "r")
next(data, None)
G = nx.parse_edgelist(data, delimiter=",")

print("G connected:", nx.is_connected(G))
print("G bipartite:", nx.bipartite.is_bipartite(G))
# print("G nodes:", list(G))
# print("G edges:", list(G.edges()))

if not nx.is_connected(G):
    sys.exit("Error: Input graph is not connected")
if not nx.bipartite.is_bipartite(G):
    sys.exit("Error: Input graph is not bipartite")

coloring = nx.greedy_color(G)
colorList = []
for node in G.nodes():
    if coloring[node] == 0:
        colorList.append(CL_RED)
    else:
        colorList.append(CL_GREEN)

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
nx.draw_networkx(G_U_1, nx.circular_layout(G_U_1), with_labels=True, node_color=CL_RED, edge_color="grey")
nx.draw_networkx_edge_labels(G_U_1, nx.circular_layout(G_U_1))

plt.subplot(224, frameon=False)
nx.draw_networkx(G_V_1, nx.circular_layout(G_V_1), with_labels=False, node_color=CL_GREEN, edge_color="grey")
# nx.draw_networkx_edge_labels(G_V_1, nx.circular_layout(G_V_1))

plt.subplot(222, frameon=False)
# plt.plot(*zip(*knc_list_U), color="#ff0000")
# plt.plot(*zip(*knc_list_V), color="#00ff00")
plt.bar(list(zip(*knc_list_U))[0], list(zip(*knc_list_U))[1], width=-1/k_max_U, align="edge", color=CL_RED+"aa", edgecolor=CL_RED+"55")
plt.bar(list(zip(*knc_list_V))[0], list(zip(*knc_list_V))[1], width=-1/k_max_V, align="edge", color=CL_GREEN+"aa", edgecolor=CL_GREEN+"55")

print("Script execution time: %s seconds" % (time.time() - start_time))

plt.show()
