#!/usr/bin/python3

import sys
import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np
from hdt import HDTDocument

start_time = time.time()

# Constants
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DBO = "http://dbpedia.org/ontology/"
DBR = "http://dbpedia.org/resource/"
RED = "#e13232"
GREEN = "#32c832"

# Query dataset
inputfile = sys.argv[1]
dataset = HDTDocument(inputfile)
G = nx.Graph()

musicians = []
ka_musicians = []
edge_list = []

(triples, card) = dataset.search_triples("", RDF + "type", DBO + "MusicalArtist")
for triple in triples:
    musicians.append(triple[0])

for musician in musicians:
    (triples, card) = dataset.search_triples(musician, DBO + "birthPlace", DBR + "Karlsruhe")
    for triple in triples:
        ka_musicians.append(triple[0])

for ka_musician in ka_musicians:
    (triples, card) = dataset.search_triples(ka_musician, "", "")
    for triple in triples:
        edge_list.append((triple[0], triple[1]))

G.add_edges_from(edge_list)

# Analyze dataset
print("G connected:", nx.is_connected(G))
print("G bipartite:", nx.bipartite.is_bipartite(G))

if not nx.is_connected(G):
    sys.exit("Error: Input graph is not connected")
if not nx.bipartite.is_bipartite(G):
    sys.exit("Error: Input graph is not bipartite")

coloring = nx.greedy_color(G)
colorList = []
for node in G.nodes():
    if coloring[node] == 0:
        colorList.append(RED)
    else:
        colorList.append(GREEN)

bipartition_1, bipartition_2 = nx.bipartite.sets(G)
if len(bipartition_1) > len(bipartition_2):
    U, V = bipartition_2, bipartition_1
else:
    U, V = bipartition_1, bipartition_2

G_U = nx.algorithms.bipartite.projection.weighted_projected_graph(G, U)
G_V = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)

# TODO: Set up a blacklist to ignore generic properties which are not class specific

# Max k value of the one mode graph to have edges
k_max_U = G_V.number_of_nodes()
k_max_V = G_U.number_of_nodes()
print("k_max_U =", k_max_U)
print("k_max_V =", k_max_V)

G_U_1 = G_U.copy()
G_V_1 = G_V.copy()

# TODO: Use also other connectivity measures
densitySum = 0
knc_list_U = []
for k in range(1, k_max_U + 1):
    for edge in list(G_U.edges.data("weight")):
        if edge[2] < k:
            G_U.remove_edge(edge[0], edge[1])
    knc_list_U.append((k/k_max_U, nx.classes.function.density(G_U)))
    densitySum += nx.classes.function.density(G_U)
RC_U = (1 / k_max_U) * densitySum
print("RC_U =", RC_U)

densitySum = 0
knc_list_V = []
for k in range(1, k_max_V + 1):
    for edge in list(G_V.edges.data("weight")):
        if edge[2] < k:
            G_V.remove_edge(edge[0], edge[1])
    knc_list_V.append((k/k_max_V, nx.classes.function.density(G_V)))
    densitySum += nx.classes.function.density(G_V)
RC_V = (1 / k_max_V) * densitySum
print("RC_V =", RC_V, "\n")

plt.subplot(321, frameon=False) # Bipartite graph G
bipartiteLayout = nx.bipartite_layout(G, U, aspect_ratio=0.5, scale=0.2)
nx.draw_networkx(G, bipartiteLayout, with_labels=True, font_size=6, node_color=colorList, edge_color="grey")

plt.subplot(323, frameon=False) # One mode network G_U
nx.draw_networkx(G_U_1, nx.circular_layout(G_U_1), with_labels=True, font_size=6, node_color=RED, edge_color="grey")
nx.draw_networkx_edge_labels(G_U_1, nx.circular_layout(G_U_1), font_size=6)

plt.subplot(324, frameon=False) # One mode network G_V
nx.draw_networkx(G_V_1, nx.circular_layout(G_V_1), with_labels=False, node_color=GREEN, edge_color="grey")

plt.subplot(322, frameon=False) # KNC plot
# plt.plot(*zip(*knc_list_U), color="#ff0000")
# plt.plot(*zip(*knc_list_V), color="#00ff00")
plt.bar(list(zip(*knc_list_U))[0], list(zip(*knc_list_U))[1], width=-1/k_max_U, align="edge", color=RED+"aa", edgecolor=RED+"55")
plt.bar(list(zip(*knc_list_V))[0], list(zip(*knc_list_V))[1], width=-1/k_max_V, align="edge", color=GREEN+"aa", edgecolor=GREEN+"55")

G_U_adj = nx.to_numpy_matrix(G_U_1)
G_U_adj[np.triu_indices_from(G_U_adj, 0)] = 0 # Set upper triangle to zeros
ax_U = plt.subplot(325, frameon=False) # Adjacency matrix G_U as heatmap
ax_U.set_xticks(np.arange(len(G_U_1.nodes())))
ax_U.set_yticks(np.arange(len(G_U_1.nodes())))
ax_U.set_xticklabels(G_U_1.nodes()) # TODO: Shorten node names?
ax_U.set_yticklabels(G_U_1.nodes())
plt.setp(ax_U.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
plt.imshow(G_U_adj, interpolation='nearest', cmap=plt.cm.Reds)
plt.colorbar()

G_V_adj = nx.to_numpy_matrix(G_V_1)
G_V_adj[np.triu_indices_from(G_V_adj, 0)] = 0
ax_V = plt.subplot(326, frameon=False) # Adjacency matrix G_V as heatmap
ax_V.set_xticks(np.arange(len(G_V_1.nodes())))
ax_V.set_yticks(np.arange(len(G_V_1.nodes())))
ax_V.set_xticklabels(G_V_1.nodes(), {"fontsize": 6})
ax_V.set_yticklabels(G_V_1.nodes(), {"fontsize": 6})
plt.setp(ax_V.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
plt.imshow(G_V_adj, interpolation='nearest', cmap=plt.cm.Greens)
plt.colorbar()

pairs = []
for row in range(0, k_max_U):
    for col in range(row + 1, k_max_U):
        pairs.append((G_V_adj.item(row, col), row, col))

sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=True) # Use pairs[0] as sort criterion

for i in range(0, 10): # Print strongest pairs
    pair = sorted_pairs[i]
    print(i + 1, pair[0], list(G_V_1.nodes)[pair[1]], list(G_V_1.nodes)[pair[2]])

# G_U_adj[np.tril_indices_from(G_U_adj, -1)] = 0 # Set lower triangle to zeros
# top_pairs = np.unravel_index(np.argsort(G_U_adj.ravel())[-2:], G_U_adj.shape) # TODO: What is -2: ?

print("\nScript execution time: %s seconds" % (time.time() - start_time))

plt.show()
