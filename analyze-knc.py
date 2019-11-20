#!/usr/bin/python3

import sys
import csv
import time
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_knc(superclass):
    with open("csv/" + superclass + ".k.csv", "r") as file_in:
        reader = csv.reader(file_in)
        knc_U_V = list(map(tuple, reader))
        return knc_U_V

def get_k_max(knc_U_V):
    k_max_U = 
    k_max_V = knc_U_V

# G = nx.Graph()
# G.add_edges_from(edge_list)

# # Check G for bipartite and connected properties
# if not nx.is_connected(G):
#     print("Info: Input graph is not connected")
# if not nx.bipartite.is_bipartite(G):
#     sys.exit("Error: Input graph is not bipartite")

# # Create one mode graphs
# U = []
# V = []
# print("Sort nodes into U and V")
# for edge in tqdm(edge_list):
#     U.append(edge[0])
#     V.append(edge[1])

# U = list(set(U))
# V = list(set(V))

# print("Compute one mode graph U")
# G_U = nx.algorithms.bipartite.projection.weighted_projected_graph(G, U)
# print("Compute one mode graph V")
# G_V = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)

# k_max_U = G_V.number_of_nodes()
# k_max_V = G_U.number_of_nodes()
# print("k_max_U =", k_max_U)
# print("k_max_V =", k_max_V)

# G_U_1 = G_U.copy()
# G_V_1 = G_V.copy()

# # TODO: Refactor into method
# # Calculate connectivity measures
# densitySum = 0
# for k in tqdm(range(1, k_max_U + 1)):
#     densitySum += nx.classes.function.density(G_U)#TODO: Calculate density only one time and save it to variable?
# RC_U = (1 / k_max_U) * densitySum
# print("RC_U = %.4f" % RC_U)

# # Get strongest pairs
# pairs = []
# G_V_adj = nx.to_numpy_matrix(G_V_1)
# for row in range(0, k_max_U):
#     for col in range(0, row):
#         pairs.append((row, col, G_V_adj.item(row, col)))

# sorted_pairs = sorted(pairs, key=lambda x: x[2], reverse=True) # Use edge weight as sorting criterion

# for i in range(0, 10):
#     pair = sorted_pairs[i]
#     print(pair[2], list(G_V_1.nodes)[pair[0]], list(G_V_1.nodes)[pair[1]])

# with open(module.config["classes"][0] + ".k.csv", "w", newline="") as file_out:
#     wr = csv.writer(file_out)
#     wr.writerows(knc_list_U)
#     wr.writerows(knc_list_V)

start_time = time.time()

config_file = sys.argv[1]
module = import_module(config_file)

classlist = module.config["classes"]

#TODO: Main loop
for superclass in classlist:
    # Artist, subclasses, k_max_U, k_max_V, #edges, connected, bipartite, RC_U_c1, RC_V_c1, RC_U_c2, RC_V_c2, lower_quartile, median, upper_quartile, slope
    print("\n[Analyze knc]", superclass)
    knc_U_V = read_knc(superclass) # [(k, c1, c2, ...), (), ...]
    
    k_max_U, k_max_V = get_k_max(knc_U_V)



print("\nRuntime: %.3f seconds [Compute knc list]" % (time.time() - start_time))
