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

def get_result(superclass, feature):
    """ Get the superclasses value in a feature column """
    df = pd.read_csv("out/_results.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

def compute_knc(superclass):
    """ Compute points for a KNC plot and save them together in .k.csv """
    k_max_u = int(get_result(superclass, "k_max_u"))
    omgraph_u = load_onemode_graph(superclass, "u")
    knc_u = compute_knc_onemode(omgraph_u, k_max_u)
    k_max_v = int(get_result(superclass, "k_max_v"))
    omgraph_v = load_onemode_graph(superclass, "v")
    knc_v = compute_knc_onemode(omgraph_v, k_max_v)
    write_knc(superclass, knc_u, knc_v)

def load_onemode_graph(superclass, onemode):
    """ Load the onemode superclass graph from .onemode.csv """
    t_start = time.time()
    wmatrix = sparse.load_npz("out/" + superclass + "." + onemode + ".npz")
    print("[Time] load_npz u %.3f sec" % (time.time() - t_start))
    print("[Info] wmatrix type", type(wmatrix))
    print("[Info] wmatrix dtype", wmatrix.dtype)
    print("[Info] wmatrix nbytes in GB", (wmatrix.data.nbytes) / (1024 ** 3))
    count_nonzeroes = wmatrix.nnz
    max_nonzeroes = 0.5 * wmatrix.shape[0] * (wmatrix.shape[0] - 1)
    matrix_density = count_nonzeroes / max_nonzeroes
    print(f"[Info] wmatrix nnz {count_nonzeroes}", f"matrix_density {matrix_density}")
    print("[Info] wmatrix shape", wmatrix.shape)
    # print("[Info] find nonzeros\n", wmatrix[2,:], wmatrix[4,:], wmatrix[6,:])
    print("[Info] wmatrix maxelement", wmatrix.max()) # high time, high space in coo; low time, low space in csr
    t_start = time.time()
    # Fails here, ~30gb in RAM when wmatrix 7,8gb, killed, (1000, 500)
    omgraph = nx.from_scipy_sparse_matrix(wmatrix) # high time, high space in csr
    print("[Time] from_sparse u %.3f sec" % (time.time() - t_start))
    return omgraph

def compute_knc_onemode(onemode_graph, k_max):
    """ Compute points of an KNC plot """
    # TODO: Break if connectivity measure reached zero
    # TODO: Add other connectivity measures
    # TODO: Build a graph here? Density can be computed manually
    t_start = time.time()
    knc_list = []
    for k in tqdm(range(1, k_max + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, nx.classes.function.density(onemode_graph)))
    print("[Time] compute_knc_onemode %.3f sec" % (time.time() - t_start))
    return knc_list

def write_knc(superclass, knc_u, knc_v):
    """ Save KNC plot points to a csv file """
    t_start = time.time()
    df_u = pd.DataFrame(knc_u, columns=["k", "density"])
    df_v = pd.DataFrame(knc_v, columns=["k", "density"])
    knc = df_u.append(df_v, ignore_index=True)
    knc.to_csv("out/" + superclass + ".k.csv", index=False)
    print("[Time] write knc %.3f sec" % (time.time() - t_start))

def main():
    config_file = sys.argv[1]
    module = import_module(config_file)

    t_compute = time.time()
    for superclass in module.config["classes"]:
        print("\n[Compute knc]", superclass)
        compute_knc(superclass)
    print("\n[Time] compute-knc %.3f sec" % (time.time() - t_compute))

main()
