#!/usr/bin/python3

import sys
import csv
import time
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_edgelist(superclass):
    with open("csv/" + superclass + ".g.csv", "r") as file_in:
        reader = csv.reader(file_in)
        edgelist = list(map(tuple, reader))
        return edgelist

def fold_bipartite_graph(graph):
    U = []
    V = []
    for edge in edgelist:
        U.append(edge[0])
        V.append(edge[1])
    U = list(set(U))
    V = list(set(V))
    print("Compute one mode graph U")
    G_U = nx.algorithms.bipartite.projection.weighted_projected_graph(G, U)
    print("Compute one mode graph V")
    G_V = nx.algorithms.bipartite.projection.weighted_projected_graph(G, V)
    return G_U, G_V

def get_k_max(onemode_graph): # TODO
    if onemode_graph == G_U:
        return G_V.number_of_nodes()
    if onemode_graph == G_V:
        return G_U.number_of_nodes()

def compute_knc(onemode_graph):
    knc_list = []
    for k in tqdm(range(1, get_k_max(onemode_graph) + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, nx.classes.function.density(onemode_graph))) # TODO: Other connectivity measures
    return knc_list

def write_knc_list(superclass, knc_list_U, knc_list_V):
    with open("csv/" + superclass + ".k.csv", "w", newline="") as file_out:
        wr = csv.writer(file_out)
        wr.writerows(knc_list_U)
        wr.writerows(knc_list_V)

start_time = time.time()

config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Compute knc]", superclass)

    G = nx.Graph()
    edgelist = read_edgelist(superclass)
    G.add_edges_from(edgelist)

    if not nx.is_connected(G):
        print("Info: Input graph is not connected", superclass)
    if not nx.bipartite.is_bipartite(G):
        sys.exit("Error: Input graph is not bipartite", superclass)

    G_U, G_V = fold_bipartite_graph(G)

    knc_list_U = compute_knc(G_U)
    knc_list_V = compute_knc(G_V)

    write_knc_list(superclass, knc_list_U, knc_list_V)

print("\nRuntime: %.3f seconds [Compute knc list]" % (time.time() - start_time))
