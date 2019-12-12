"""
Fold a bipartite Knowledge Graph into its two onemode representations.
"""

#!/usr/bin/python3

import sys
import time
from importlib import import_module
import numpy as np
import pandas as pd
import networkx as nx

def read_edgelist(superclass):
    """ Read edge list from csv file """
    df = pd.read_csv("csv/" + superclass + ".g.csv")
    return list(df.itertuples(index=False, name=None))

def fold_bipartite_graph(bipgraph, U, V):
    """ Fold a bipartite graph to its onemode representations using its biadjacency matrix """
    # TODO: Save row and column name order for later name lookup in G_U for e.g. heatmap analysis
    # TODO: Fold the onemodes one at a time to reduce RAM
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=U, column_order=V)
    print("[Time] comp-biadj-matrix %.3f sec" % (time.time() - t_start), superclass)
    print("[Info] A shape", A.shape)
    t_start = time.time()
    G_U = np.dot(A, A.T)
    print("[Time] onemode-dot-product U %.3f sec" % (time.time() - t_start), superclass)
    # del G_U # Free up memory, Divide into two method calls?
    t_start = time.time()
    G_V = np.dot(A.T, A)
    print("[Time] onemode-dot-product V %.3f sec" % (time.time() - t_start), superclass)
    return G_U, G_V

def append_result_columns(superclass, k_max_U, k_max_V, connected, bipartite):
    """ Save more properties for each superclass in the result csv file """
    df = pd.read_csv("csv/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_U"] = k_max_U
    df.loc[df.index[df["superclass"] == superclass], "k_max_V"] = k_max_V
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("csv/_results.csv", index=False)

def write_edgelist(classname, edgelist, onemode):
    """ Save onemode edge list in a csv file """
    t_start = time.time()
    # Old solution
    # df = pd.DataFrame(edgelist, columns=[onemode + "_a", onemode + "_b", "weight"])
    # df.to_csv("csv/" + classname + "." + onemode + ".csv", index=False)

    # New solution
    np.savetxt("csv/" + classname + "." + onemode + ".csv", edgelist, fmt="%i,%i,%i")
    print("[Time] write-onemode %.3f sec" % (time.time() - t_start))


def get_onemode_edgelist(weight_matrix):
    """ Build onemode edgelist from non-zero G_U values """
    t_start = time.time()
    # Old solution (for comparing runtime difference)
    # onemode_edgelist = []
    # size = weight_matrix.shape[0]
    # for row in range(1, size):
    #     for col in range(0, row):
    #         weight = weight_matrix[row, col]
    #         if weight > 0:
    #             onemode_edgelist.append((row, col, weight))

    # New solution, Use nonzero elements & indices in triu with k = -1
    #TODO: toarray() only once
    indices = np.nonzero(np.tril(weight_matrix.toarray(), -1))
    elements = weight_matrix.toarray()[indices]
    # Combine indices and corresponding elements # dstack, column_stack, vstack
    onemode_edgelist = np.stack((indices[0], indices[1], elements), axis=-1)
    print("[Time] get-onemode-edgelist %.3f sec" % (time.time() - t_start))
    return onemode_edgelist

t_fold = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Fold]", superclass)

    G = nx.Graph()
    edgelist = read_edgelist(superclass)
    G.add_edges_from(edgelist)

    #TODO: Own method
    t_start = time.time()
    is_connected = True
    is_bipartite = True
    if not nx.is_connected(G):
        is_connected = False
        print("[Info] Input graph is not connected", superclass)
    if not nx.bipartite.is_bipartite(G):
        is_bipartite = False
        sys.exit("[Error] Input graph is not bipartite", superclass)
    print("[Time] check-con-bip %.3f sec" % (time.time() - t_start))

    #TODO: Own method
    t_start = time.time()
    U = []
    V = []
    for edge in edgelist:
        U.append(edge[0])
        V.append(edge[1])
    U = list(set(U))
    V = list(set(V))
    print("[Time] get-onemode-sides %.3f sec" % (time.time() - t_start), superclass)

    # Diagonal values of G_U represent to how much v's the u is affiliated with
    #TODO: Save diagonal values in .u.csv for analysis of extensively described entities
    G_U, G_V = fold_bipartite_graph(G, U, V)

    k_max_U = G_V.shape[0]
    k_max_V = G_U.shape[0]

    G_U_edgelist = get_onemode_edgelist(G_U)
    G_V_edgelist = get_onemode_edgelist(G_V)

    write_edgelist(superclass, G_U_edgelist, "u")
    write_edgelist(superclass, G_V_edgelist, "v")

    # In onemode network edgelists, data about disconnected nodes gets lost
    append_result_columns(superclass, k_max_U, k_max_V, is_connected, is_bipartite)

print("\n[Time] fold-graph %.3f sec" % (time.time() - t_fold))
