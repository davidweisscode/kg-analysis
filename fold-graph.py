#!/usr/bin/python3

import sys
import csv
import time
import pandas as pd
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_edgelist(superclass):
    df = pd.read_csv("csv/" + superclass + ".g.csv")
    return list(df.itertuples(index=False, name=None))

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

def get_k_max(onemode_graph): # TODO: Add error handling
    if onemode_graph == G_U:
        return int(G_V.number_of_nodes())
    if onemode_graph == G_V:
        return int(G_U.number_of_nodes())

def append_result_columns(superclass, k_max_U, k_max_V, connected, bipartite):
    df = pd.read_csv("csv/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_U"] = k_max_U
    df.loc[df.index[df["superclass"] == superclass], "k_max_V"] = k_max_V
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("csv/_results.csv", index=False)

# Save onemode graphs in edgelist
def write_edgelist(classname, edgelist, onemode):
    df = pd.DataFrame(edgelist, columns=["node_1", "node_2", "weight"])
    df.to_csv("csv/" + classname + "." + onemode + ".csv", index=False)

start_time = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Fold graph]", superclass)

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

    G_U_edgelist = list(G_U.edges.data("weight"))
    G_V_edgelist = list(G_V.edges.data("weight"))
    write_edgelist(superclass, G_U_edgelist, "u")
    write_edgelist(superclass, G_V_edgelist, "v")

    append_result_columns(superclass, k_max_U, k_max_V, is_connected, is_bipartite)

print("\n[Runtime] %.3f seconds [Compute knc list]" % (time.time() - start_time))
