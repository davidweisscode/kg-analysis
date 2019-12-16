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
    # TODO: Fold the onemodes one at a time to reduce RAM
    # del wmatrix_u # Free up memory, Divide into two method calls?
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bipgraph, row_order=u, column_order=v)
    print("[Time] comp-biadj-matrix %.3f sec" % (time.time() - t_start))
    print("[Info] A shape", A.shape)
    t_start = time.time()
    wmatrix_u = np.dot(A, A.T)
    print("[Time] onemode-dot-product U %.3f sec" % (time.time() - t_start))
    t_start = time.time()
    wmatrix_v = np.dot(A.T, A)
    print("[Time] onemode-dot-product V %.3f sec" % (time.time() - t_start))
    return wmatrix_u, wmatrix_v

def append_result_columns(superclass, k_max_u, k_max_v, connected, bipartite):
    """ Save more properties for each superclass in the result csv file """
    df = pd.read_csv("csv/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "k_max_u"] = k_max_u
    df.loc[df.index[df["superclass"] == superclass], "k_max_v"] = k_max_v
    df.loc[df.index[df["superclass"] == superclass], "connected"] = connected
    df.loc[df.index[df["superclass"] == superclass], "bipartite"] = bipartite
    df.to_csv("csv/_results.csv", index=False)

def write_edgelist(classname, edgelist, onemode):
    """ Save onemode edge list in a csv file """
    #TODO: Most time intensive, Improve
    t_start = time.time()
    # Old solution
    # df = pd.DataFrame(edgelist, columns=[onemode + "_a", onemode + "_b", "weight"])
    # df.to_csv("csv/" + classname + "." + onemode + ".csv", index=False)

    # New solution
    np.savetxt("csv/" + classname + "." + onemode + ".csv", edgelist, fmt="%i,%i,%i")
    print("[Time] write-onemode %.3f sec" % (time.time() - t_start))

def get_tril_start(indexarray):
    # indexarray pairs not ordered
    tril_start = 0#indexarray[0].shape[0] / 2
    for i in range(0, indexarray[0].shape[0]):
        rowindex = indexarray[0][i]
        colindex = indexarray[1][i]
        print(rowindex, colindex)

def get_onemode_edgelist(wmatrix):
    """ Build onemode edgelist [(n1, n2, w), ...] from non-zero onemode weight matrix values """
    t_start = time.time()

    print("wmatrix type", type(wmatrix)) # scipy.sparse.csr.csr_matrix
    print("wmatrix shape", wmatrix.shape) # (700, 700) --> 487204 elements

    nonzero_indices = np.nonzero(wmatrix) # Has nonzero() an effect when dealing with sparse matrices?
    #TODO: Get tril indices (rowindex > colindex)

    elements = wmatrix[nonzero_indices][0,:]# https://stackoverflow.com/questions/4455076/how-to-access-the-ith-column-of-a-numpy-multidimensional-array

    print("elements", elements)
    print("elements type", type(elements)) # numpy matrix
    print("elements shape", elements.shape) # (1, 283368)
    print("elements [0]", elements[0]) # same as elements
    print("elements [0] shape", elements[0].shape) # (1, 283368)

    # Convert numpy.matrix to ndarray
    print("squeeze", np.squeeze(np.asarray(elements)))
    print("squeeze shape", np.squeeze(np.asarray(elements)).shape)

    print("nzi", nonzero_indices)
    print("nzi type", type(nonzero_indices)) # tuple
    print("nzi [0]", nonzero_indices[0])
    print("nzi [0] type", type(nonzero_indices[0])) # ndarray
    print("nzi [0] shape", nonzero_indices[0].shape) # (283368,)

    # print(len(nonzero_indices[0]), len(nonzero_indices[1]), len(list(elements)))
    print(nonzero_indices[0].shape, nonzero_indices[1].shape, np.squeeze(np.asarray(elements)).shape)
    onemode_edgelist = np.stack((nonzero_indices[0], nonzero_indices[1], np.squeeze(np.asarray(elements))), axis=-1)
    print(onemode_edgelist)

    sys.exit()

    # toarray() only once, time vs space, to transform sparse matrix to ndarray
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

    bipgraph = nx.Graph()
    edgelist = read_edgelist(superclass)
    bipgraph.add_edges_from(edgelist)

    is_connected = check_connected(bipgraph)
    is_bipartite = check_bipartite(bipgraph)
    print("[Info] Number of nodes", bipgraph.number_of_nodes())
    print("[Info] Number of edges", bipgraph.number_of_edges())
    side_u, side_v = split_edgelist(edgelist)

    # Diagonal values of G_U represent to how much v's the u is affiliated with
    #TODO: Save diagonal values in .csv for analysis of extensively described entities
    wmatrix_u, wmatrix_v = fold_bipgraph(bipgraph, side_u, side_v)

    k_max_u = wmatrix_u.shape[0]
    k_max_v = wmatrix_v.shape[0]

    edgelist_u = get_onemode_edgelist(wmatrix_u)
    edgelist_v = get_onemode_edgelist(wmatrix_v)

    write_edgelist(superclass, edgelist_u, "u")
    write_edgelist(superclass, edgelist_v, "v")

    # In onemode network edgelists, data about disconnected nodes gets lost
    append_result_columns(superclass, k_max_u, k_max_v, is_connected, is_bipartite)

    # TODO: Delete objects (G, edgelist, U, V, ...) to free up RAM?

print("\n[Time] fold-graph %.3f sec" % (time.time() - t_fold))
