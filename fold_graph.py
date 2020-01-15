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
    df = pd.read_csv(f"out/{superclass}.g.csv")
    return list(df.itertuples(index=False, name=None))

def check_connected(bipgraph):
    """ Check whether input graph is connected """
    t_start = time.time()
    connected = True
    if not nx.is_connected(bipgraph):
        connected = False
        print("[Info] Input graph is not connected")
    print(f"[Time] check-connected {time.time() - t_start:.3f} sec")
    return connected

def check_bipartite(bipgraph):
    """ Check whether input graph is bipartite """
    t_start = time.time()
    bipartite = True
    if not nx.bipartite.is_bipartite(bipgraph):
        bipartite = False
        sys.exit("[Error] Input graph is not bipartite")
    print(f"[Time] check-bipartite {time.time() - t_start:.3f} sec")
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
    print(f"[Time] split-edgelist {time.time() - t_start:.3f} sec")
    return side_u, side_v

def append_result_columns(superclass, k_max_u, k_max_v, connected, bipartite):
    """ Save more properties for superclass in the result csv file """
    df = pd.read_csv("out/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_u"] = k_max_u
    df.loc[df.index[df["superclass"] == superclass], "k_max_v"] = k_max_v
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("out/_results.csv", index=False)

def write_edgelist(classname, edgelist, onemode):
    """ Write edge list to csv file """
    df = pd.DataFrame(edgelist, columns=["a", "b", "w"])
    df.to_csv(f"out/{classname}.{onemode}.csv", index=False)

def fold_graph(superclass):
    print("\n[Fold]", superclass)
    bipgraph = nx.Graph()
    edgelist = read_edgelist(superclass)
    bipgraph.add_edges_from(edgelist)
    is_connected = check_connected(bipgraph)
    is_bipartite = check_bipartite(bipgraph)
    print("[Info] Number of nodes", bipgraph.number_of_nodes())
    print("[Info] Number of edges", bipgraph.number_of_edges())
    side_u, side_v = split_edgelist(edgelist)
    # In onemode network edgelists, data about disconnected nodes gets lost
    k_max_u, k_max_v = len(side_v), len(side_u)
    append_result_columns(superclass, k_max_u, k_max_v, is_connected, is_bipartite)
    #TODO: Save diagonal values in .csv for analysis of extensively described entities
    fold_dot(superclass, bipgraph, side_u, side_v)
    #TODO: Add fold_hop() here

def fold_dot(superclass, bipgraph, u, v):
    """ Fold a bipartite graph to its onemode representations using its biadjacency matrix """
    # TODO: Save row and column name order for later name lookup in wmatrix_u for e.g. heatmap analysis
    # TODO: Fold the onemodes one at a time to reduce space (increases time)
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=u, column_order=v, dtype="uint16")
    print(f"[Time] comp-biadj-matrix {time.time() - t_start:.3f} sec")
    print("[Info] A shape", A.shape)
    print("[Info] A dtype", A.dtype)
    fold_dot_onemode(superclass, A, "u")
    fold_dot_onemode(superclass, A, "v")

def fold_dot_onemode(superclass, biadjmatrix, onemode):
    t_start = time.time()
    if onemode == "u":
        wmatrix = np.dot(biadjmatrix, biadjmatrix.T)
    elif onemode == "v":
        wmatrix = np.dot(biadjmatrix.T, biadjmatrix)
    print(f"[Time] onemode-dotproduct {onemode} {time.time() - t_start:.3f} sec")
    print(f"[Info] wmatrix {onemode} type {type(wmatrix)}")
    print(f"[Info] wmatrix {onemode} dtype {wmatrix.dtype}")
    print(f"[Info] wmatrix {onemode} nbytes in GB {(wmatrix.data.nbytes + wmatrix.indptr.nbytes + wmatrix.indices.nbytes) / (1024 ** 3):.6f}")
    print(f"[Info] wmatrix {onemode} nbytes data in GB {(wmatrix.data.nbytes) / (1024 ** 3):.6f}")
    print(f"[Info] wmatrix {onemode} shape {wmatrix.shape}")
    print(f"[Info] wmatrix {onemode} maxelement {wmatrix.max()}")
    count_nonzeroes = wmatrix.nnz
    max_nonzeroes = wmatrix.shape[0] * (wmatrix.shape[0] - 1)
    matrix_density = count_nonzeroes / max_nonzeroes
    print(f"[Info] wmatrix {onemode} nnz {count_nonzeroes}")
    print(f"[Info] wmatrix {onemode} density {matrix_density:.4f}")
    t_start = time.time()
    wmatrix = sparse.tril(wmatrix, k=-1) # Fails here for large matrices with high time, high space
    print(f"[Time] wmatrix {onemode} tril {time.time() - t_start:.3f} sec")
    t_start = time.time()
    wmatrix = wmatrix.tocsr()
    print(f"[Time] wmatrix {onemode} to-csr {time.time() - t_start:.3f} sec")
    count_nonzeroes = wmatrix.nnz
    max_nonzeroes = 0.5 * wmatrix.shape[0] * (wmatrix.shape[0] - 1)
    matrix_density = count_nonzeroes / max_nonzeroes
    print(f"[Info] wmatrix {onemode} tril nnz {count_nonzeroes}")
    print(f"[Info] wmatrix {onemode} tril density {matrix_density:.4f}")
    print(f"[Info] wmatrix {onemode} tril type {type(wmatrix)}")
    print(f"[Info] wmatrix {onemode} tril nbytes data in GB {(wmatrix.data.nbytes) / (1024 ** 3):.6f}")
    print(f"[Info] wmatrix {onemode} tril nnz {wmatrix.nnz}")
    t_start = time.time()
    sparse.save_npz(f"out/{superclass}.{onemode}.npz", wmatrix)
    print(f"[Time] save-npz {onemode} {time.time() - t_start:.3f} sec")

def main():
    config_file = sys.argv[1]
    module = import_module(config_file)

    t_fold = time.time()
    for superclass in module.config["classes"]:
        fold_graph(superclass)

    print(f"\n[Time] fold-graphs {time.time() - t_fold:.3f} sec")

main()
