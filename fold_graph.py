"""
Fold a bipartite Knowledge Graph into its two onemode representations.
"""

#!/usr/bin/python3

import sys
import time
from scipy import sparse
from importlib import import_module
import numpy as np
import pandas as pd
import networkx as nx

def read_edgelist(superclass):
    """ Read edge list from csv file """
    df = pd.read_csv("out/" + superclass + ".g.csv")
    return list(df.itertuples(index=False, name=None))

def check_connected(bipgraph):
    """ Check whether input graph is connected """
    t_start = time.time()
    connected = True
    if not nx.is_connected(bipgraph):
        connected = False
        print("[Info] Input graph is not connected")
    print("[Time] check-con %.3f sec" % (time.time() - t_start))
    return connected

def check_bipartite(bipgraph):
    """ Check whether input graph is bipartite """
    t_start = time.time()
    bipartite = True
    if not nx.bipartite.is_bipartite(bipgraph):
        bipartite = False
        sys.exit("[Error] Input graph is not bipartite")
    print("[Time] check-bip %.3f sec" % (time.time() - t_start))
    return bipartite

def split_edgelist(edges):
    """ Split the input edgelist into left and right side """
    t_start = time.time()
    side_u = []
    side_v = []
    for edge in edges:
        side_u.append(edge[0])
        side_v.append(edge[1])
    side_u = list(set(side_u))
    side_v = list(set(side_v))
    print("[Time] split-onemode-edges %.3f sec" % (time.time() - t_start))
    return side_u, side_v

def fold_bipgraph(bipgraph, u, v):
    """ Fold a bipartite graph to its onemode representations using its biadjacency matrix """
    # TODO: Save row and column name order for later name lookup in wmatrix_u for e.g. heatmap analysis
    # TODO: Fold the onemodes one at a time to reduce space (increases time)
    # del wmatrix_u # Free up memory, Divide into two method calls?
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=u, column_order=v, dtype="uint16")
    print("[Time] comp-biadj-matrix %.3f sec" % (time.time() - t_start))
    print("[Info] A shape", A.shape)
    print("[Info] A dtype", A.dtype)
    t_start = time.time()
    wmatrix_u = np.dot(A, A.T)
    print("[Time] onemode-dot-product U %.3f sec" % (time.time() - t_start))
    t_start = time.time()
    wmatrix_v = np.dot(A.T, A)
    print("[Time] onemode-dot-product V %.3f sec" % (time.time() - t_start))
    return wmatrix_u, wmatrix_v

def append_result_columns(superclass, k_max_u, k_max_v, connected, bipartite):
    """ Save more properties for each superclass in the result csv file """
    df = pd.read_csv("out/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_u"] = k_max_u
    df.loc[df.index[df["superclass"] == superclass], "k_max_v"] = k_max_v
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("out/_results.csv", index=False)

t_fold = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Fold]", superclass)

    bipgraph = nx.Graph()
    edgelist = read_edgelist(superclass)
    bipgraph.add_edges_from(edgelist)

    is_connected = check_connected(bipgraph)
    is_bipartite = check_bipartite(bipgraph)
    print("[Info] Number of nodes", bipgraph.number_of_nodes())
    print("[Info] Number of edges", bipgraph.number_of_edges())
    side_u, side_v = split_edgelist(edgelist)

    # Diagonal values of wmatrix_u represent to how much v's the u is affiliated with
    #TODO: Save diagonal values in .csv for analysis of extensively described entities
    wmatrix_u, wmatrix_v = fold_bipgraph(bipgraph, side_u, side_v)
    print("[Info] wmatrix_u type", type(wmatrix_u))
    print("[Info] wmatrix_u dtype", wmatrix_u.dtype)
    print("[Info] wmatrix_u nbytes in G", (wmatrix_u.data.nbytes + wmatrix_u.indptr.nbytes + wmatrix_u.indices.nbytes) / (1024 ** 3))

    #TODO: Use dynamic dtypes (int16, uint16, ...) depending on wmatrix max values
    print("[Info] wmatrix_u max", wmatrix_u.max())
    print("[Info] wmatrix_v max", wmatrix_v.max())

    # In onemode network edgelists, data about disconnected nodes gets lost
    k_max_u = wmatrix_v.shape[0]
    k_max_v = wmatrix_u.shape[0]
    append_result_columns(superclass, k_max_u, k_max_v, is_connected, is_bipartite)

    # Fails here for large matrices
    #TODO: Delete objects to free up RAM, Garbage collection
    #TODO: Change overcommit memory https://stackoverflow.com/questions/57507832/unable-to-allocate-array-with-shape-and-data-type
    #TODO: Change datatype of matrix elements from int64 to something else https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.astype.html
    wmatrix_u = sparse.tril(wmatrix_u, k=-1)
    t_start = time.time()
    sparse.save_npz("out/" + superclass + ".u.npz", wmatrix_u)
    print("[Time] save-npz-u %.3f sec" % (time.time() - t_start))

    wmatrix_v = sparse.tril(wmatrix_v, k=-1)
    t_start = time.time()
    sparse.save_npz("out/" + superclass + ".v.npz", wmatrix_v)
    print("[Time] save-npz-v %.3f sec" % (time.time() - t_start))

print("\n[Time] fold-graph %.3f sec" % (time.time() - t_fold))
