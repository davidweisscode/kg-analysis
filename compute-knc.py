#!/usr/bin/python3

import sys
import csv
import time
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

start_time = time.time()

# Read config
config_file = sys.argv[1]
module = import_module(config_file)

G = nx.Graph()

with open(module.config["classes"][0]+ ".g.csv", "r") as file_in:
    reader = csv.reader(file_in)
    edge_list = list(map(tuple, reader))

G.add_edges_from(edge_list)

# Analyze dataset
if not nx.is_connected(G):
    print("Info: Input graph is not connected")
if not nx.bipartite.is_bipartite(G):
    sys.exit("Error: Input graph is not bipartite")

# Create one mode graphs
U = []
V = []
for edge in edge_list:
    U.append(edge[0])
    V.append(edge[1])

U = list(set(U))
V = list(set(V))

G_U = nx.algorithms.bipartite.projection.weighted_projected_graph(G, U)
G_V = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)

k_max_U = G_V.number_of_nodes()
k_max_V = G_U.number_of_nodes()
print("k_max_U =", k_max_U)
print("k_max_V =", k_max_V)

G_U_1 = G_U.copy()
G_V_1 = G_V.copy()

# Calculate connectivity measures # TODO: Use also other connectivity measures
densitySum = 0
knc_list_U = []
for k in range(1, k_max_U + 1):
    for edge in list(G_U.edges.data("weight")):
        if edge[2] < k:
            G_U.remove_edge(edge[0], edge[1])
    knc_list_U.append((k, nx.classes.function.density(G_U)))
    densitySum += nx.classes.function.density(G_U)
RC_U = (1 / k_max_U) * densitySum
print("RC_U = %.4f" % RC_U)

densitySum = 0
knc_list_V = []
for k in range(1, k_max_V + 1):
    for edge in list(G_V.edges.data("weight")):
        if edge[2] < k:
            G_V.remove_edge(edge[0], edge[1])
    knc_list_V.append((k, nx.classes.function.density(G_V)))
    densitySum += nx.classes.function.density(G_V)
RC_V = (1 / k_max_V) * densitySum
print("RC_V = %.4f" % RC_V, "\n")

# Get strongest pairs
pairs = []
G_V_adj = nx.to_numpy_matrix(G_V_1)
for row in range(0, k_max_U):
    for col in range(0, row):
        pairs.append((row, col, G_V_adj.item(row, col)))

sorted_pairs = sorted(pairs, key=lambda x: x[2], reverse=True) # Use edge weight as sorting criterion

for i in range(0, 10):
    pair = sorted_pairs[i]
    print(pair[2], list(G_V_1.nodes)[pair[0]], list(G_V_1.nodes)[pair[1]])

with open(module.config["classes"][0] + ".k.csv", "w", newline="") as file_out:
    wr = csv.writer(file_out)
    wr.writerows(knc_list_U)
    wr.writerows(knc_list_V)

print("\nScript execution time: %.3f seconds" % (time.time() - start_time))
