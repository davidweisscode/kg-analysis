#!/usr/bin/python3

import sys
import csv
import time
import networkx as nx
import pandas as pd
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_edgelist(superclass):
    df = pd.read_csv("csv/" + superclass + ".g.csv")
    return list(df.itertuples(index=False, name=None))

def fold_bipartite_graph(graph):
    #TODO: Save folded graphs in .u.csv and .v.csv
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

def get_k_max(onemode_graph): # TODO: Add error handling
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
        knc_list.append((k, nx.classes.function.density(onemode_graph))) # TODO: Add other connectivity measures
    return knc_list

def write_knc_list(superclass, knc_list_U, knc_list_V):
    df_U = pd.DataFrame(knc_list_U, columns=["k", "density"])
    df_V = pd.DataFrame(knc_list_V, columns=["k", "density"])
    knc = df_U.append(df_V, ignore_index=True)
    knc.to_csv("csv/" + superclass + ".k.csv", index=False)

def append_result_columns(superclass, k_max_U, k_max_V, connected, bipartite):
    df = pd.read_csv("csv/results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_U"] = k_max_U
    df.loc[df.index[df["superclass"] == superclass], "k_max_V"] = k_max_V
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("csv/results.csv", index=False)

start_time = time.time()

config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Compute knc]", superclass)

    G = nx.Graph()
    edgelist = read_edgelist(superclass)
    G.add_edges_from(edgelist)

    is_connected = True
    is_bipartite = True
    if not nx.is_connected(G):
        is_connected = False
        print("Info: Input graph is not connected", superclass)
    if not nx.bipartite.is_bipartite(G):
        is_bipartite = False
        sys.exit("Error: Input graph is not bipartite", superclass)

    G_U, G_V = fold_bipartite_graph(G)

    k_max_U = get_k_max(G_U)
    k_max_V = get_k_max(G_V)

    knc_list_U = compute_knc(G_U)
    knc_list_V = compute_knc(G_V)

    write_knc_list(superclass, knc_list_U, knc_list_V)
    append_result_columns(superclass, k_max_U, k_max_V, is_connected, is_bipartite)

print("\nRuntime: %.3f seconds [Compute knc list]" % (time.time() - start_time))
