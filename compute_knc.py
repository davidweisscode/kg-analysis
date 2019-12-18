"""
Compute points for a KNC plot.
"""

#!/usr/bin/python3

import sys
import time
from scipy import sparse
from importlib import import_module
import pandas as pd
import networkx as nx
from tqdm import tqdm

def read_edgelist(superclass, onemode):
    """ Read edge list from csv file """
    df = pd.read_csv("csv/" + superclass + "." + onemode + ".csv")
    return list(df.itertuples(index=False, name=None))

def get_k_max(onemode_graph): # TODO: Add error handling
    """ Compute the maximum k value for a given onemode graph """
    if onemode_graph == G_U:
        return int(G_V.number_of_nodes())
    if onemode_graph == G_V:
        return int(G_U.number_of_nodes())

def get_result(superclass, feature):
    """ Get the superclasses value in a feature column """
    df = pd.read_csv("csv/_results.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

def compute_knc(onemode_graph, k_max):
    """ Compute points of an KNC plot """
    # TODO: Build a graph here? Density can be computed manually

    # TODO: Add other connectivity measures
    # TODO: Break if connectivity measure reached zero
    knc_list = []
    for k in tqdm(range(1, k_max + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, nx.classes.function.density(onemode_graph)))
    return knc_list

def write_knc(superclass, knc_U, knc_V):
    """ Save KNC plot points to a csv file """
    df_U = pd.DataFrame(knc_U, columns=["k", "density"])
    df_V = pd.DataFrame(knc_V, columns=["k", "density"])
    knc = df_U.append(df_V, ignore_index=True)
    knc.to_csv("csv/" + superclass + ".k.csv", index=False)

start_time = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Compute knc]", superclass)

    #TODO: Delete objects to free up space?
    wmatrix_u = sparse.load_npz("out/" + superclass + ".u.npz")
    omgraph_u = nx.from_scipy_sparse_matrix(wmatrix_u)
    wmatrix_v = sparse.load_npz("out/" + superclass + ".v.npz")
    omgraph_v = nx.from_scipy_sparse_matrix(wmatrix_v)

    k_max_u = int(get_result(superclass, "k_max_u"))
    k_max_v = int(get_result(superclass, "k_max_v"))

    knc_u = compute_knc(omgraph_u, k_max_u)
    knc_v = compute_knc(omgraph_v, k_max_v)

    write_knc(superclass, knc_u, knc_v)

print("\n[Time] compute-knc %.3f sec" % (time.time() - start_time))
