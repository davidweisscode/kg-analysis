"""
Fold a bipartite Knowledge Graph into its two onemode representations.
"""

#!/usr/bin/python3

import sys
import time
import itertools
from tqdm import tqdm
from scipy import sparse
from importlib import import_module
import numpy as np
import pandas as pd
import networkx as nx

def read_edgelist(superclass):
    """ Read edgelist from csv file """
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

def append_result_columns(superclass, k_max_u, k_max_v, connected, bipartite):
    """ Save more properties for each superclass in the result csv file """
    df = pd.read_csv("out/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_u"] = k_max_u
    df.loc[df.index[df["superclass"] == superclass], "k_max_v"] = k_max_v
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("out/_results.csv", index=False)

def write_edgelist(classname, edgelist, onemode):
    """ Write edge list to csv file """
    df = pd.DataFrame(edgelist, columns=["a", "b", "w"])
    df.to_csv("out/" + classname + "." + onemode + ".csv", index=False)

def fold_bipgraph(bipgraph, u, v):
    """ Fold a bipartite graph to its onemode representations using its biadjacency matrix """
    # TODO: Save row and column name order for later name lookup in wmatrix_u for e.g. heatmap analysis
    # TODO: Fold the onemodes one at a time to reduce space (increases time)
    # TODO: Delete objects to free up RAM, Garbage collection
    # del wmatrix_u # Free up memory, Divide into two method calls?
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=u, column_order=v, dtype="uint16")
    print("[Time] comp-biadj-matrix %.3f sec" % (time.time() - t_start))
    print("[Info] A shape", A.shape)
    print("[Info] A dtype", A.dtype)
    t_start = time.time()
    wmatrix_u = np.dot(A, A.T)
    print("[Time] onemode-dot-product u %.3f sec" % (time.time() - t_start))
    t_start = time.time()
    wmatrix_v = np.dot(A.T, A)
    print("[Time] onemode-dot-product v %.3f sec\n" % (time.time() - t_start))
    return wmatrix_u, wmatrix_v

def main():
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
        print("[Info] wmatrix_u nbytes in GB", (wmatrix_u.data.nbytes + wmatrix_u.indptr.nbytes + wmatrix_u.indices.nbytes) / (1024 ** 3))
        print("[Info] wmatrix_u nbytes data in GB", (wmatrix_u.data.nbytes) / (1024 ** 3))
        print("[Info] wmatrix_u shape", wmatrix_u.shape)
        print("[Info] wmatrix_u maxelement", wmatrix_u.max())
        print("[Info] wmatrix_v shape", wmatrix_v.shape)
        print("[Info] wmatrix_v maxelement", wmatrix_v.max())
        count_nonzeroes = wmatrix_u.nnz
        max_nonzeroes = wmatrix_u.shape[0] * (wmatrix_u.shape[0] - 1)
        matrix_density = count_nonzeroes / max_nonzeroes
        print(f"[Info] wmatrix_u nnz {count_nonzeroes}")
        print(f"[Info] wmatrix_u density {matrix_density}")

        # In onemode network edgelists, data about disconnected nodes gets lost
        k_max_u = wmatrix_v.shape[0]
        k_max_v = wmatrix_u.shape[0]
        append_result_columns(superclass, k_max_u, k_max_v, is_connected, is_bipartite)

        # Fails here for large matrices
        t_start = time.time()
        wmatrix_u = sparse.tril(wmatrix_u, k=-1) # high time, high space
        print("[Time] wmatrix_u tril %.3f sec" % (time.time() - t_start))

        t_start = time.time()
        wmatrix_u = wmatrix_u.tocsr()
        print("[Time] tocsr %.3f sec" % (time.time() - t_start))

        count_nonzeroes = wmatrix_u.nnz
        max_nonzeroes = 0.5 * wmatrix_u.shape[0] * (wmatrix_u.shape[0] - 1)
        matrix_density = count_nonzeroes / max_nonzeroes
        print(f"[Info] wmatrix_u tril nnz {count_nonzeroes}")
        print(f"[Info] wmatrix_u tril density {matrix_density}")
        print("[Info] wmatrix_u tril type", type(wmatrix_u))
        print("[Info] wmatrix_u tril nbytes data in GB", (wmatrix_u.data.nbytes) / (1024 ** 3))
        print("[Info] wmatrix_u tril nnz", wmatrix_u.nnz)

        t_start = time.time()
        sparse.save_npz("out/" + superclass + ".u.npz", wmatrix_u) # high time, low space
        print("[Time] savenpz u %.3f sec" % (time.time() - t_start))

        t_start = time.time()
        wmatrix_v = sparse.tril(wmatrix_v, k=-1)
        print("[Time] wmatrix_v tril %.3f sec" % (time.time() - t_start))
        t_start = time.time()
        sparse.save_npz("out/" + superclass + ".v.npz", wmatrix_v)
        print("[Time] savenpz v %.3f sec" % (time.time() - t_start))

    print("\n[Time] fold-graph %.3f sec" % (time.time() - t_fold))

main()
