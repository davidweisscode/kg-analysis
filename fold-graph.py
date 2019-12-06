#!/usr/bin/python3

import sys
import csv
import time
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_edgelist(superclass):
    df = pd.read_csv("csv/" + superclass + ".g.csv")
    return list(df.itertuples(index=False, name=None))

def fold_bipartite_graph(bipgraph, U, V):
    # TODO: Save row and column name order, Later name lookup in folded matrix F, Names for e.g. heatmap analysis
    # TODO: fold the onemodes one at a time to reduce RAM
    print("Compute biadjacency matrix A")
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=U, column_order=V)
    print("A shape", A.shape)
    print("Compute G_U")
    G_U = np.dot(A , A.T)
    print("G_U shape", G_U.shape)
    # del G_U # Free up memory
    print("Compute G_V")
    G_V = np.dot(A.T , A)
    print("G_V shape", G_V.shape)
    return G_U, G_V

def append_result_columns(superclass, k_max_U, k_max_V, connected, bipartite):
    df = pd.read_csv("csv/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_U"] = k_max_U
    df.loc[df.index[df["superclass"] == superclass], "k_max_V"] = k_max_V
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("csv/_results.csv", index=False)

# Save onemode graphs in edgelist
def write_edgelist(classname, edgelist, onemode):
    df = pd.DataFrame(edgelist, columns=[onemode + "_node_1", onemode + "_node_2", "weight"])
    df.to_csv("csv/" + classname + "." + onemode + ".csv", index=False)

t_fold = time.time()
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
        print("[Info] Input graph is not connected", superclass)
    if not nx.bipartite.is_bipartite(G):
        is_bipartite = False
        sys.exit("[Error] Input graph is not bipartite", superclass)

    U = []
    V = []
    for edge in edgelist:
        U.append(edge[0])
        V.append(edge[1])
    U = list(set(U))
    V = list(set(V))

    G_U, G_V = fold_bipartite_graph(G, U, V)

    k_max_U = G_V.shape[0]
    k_max_V = G_U.shape[0]
    print("k_max_U", k_max_U)
    print("k_max_V", k_max_V)

    print(G_U)
    #TODO: Build G_U_edgelist [(art1, art2, w), (art1, art3, w), ...] from ndarray G_U
    # Diagonal values of G_U represent to how much V nodes the U node is affiliated with

    G_U_edgelist = list(G_U.edges.data("weight"))
    G_V_edgelist = list(G_V.edges.data("weight"))
    write_edgelist(superclass, G_U_edgelist, "u")
    write_edgelist(superclass, G_V_edgelist, "v")

    # In onemode network edgelists, data about disconnected nodes gets lost
    append_result_columns(superclass, k_max_U, k_max_V, is_connected, is_bipartite)

print("\n[Runtime] fold-graph %.3f sec" % (time.time() - t_fold))
