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

def compute_knc(onemode_graph, k_max):
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
    print("[Time] compute_knc %.3f sec" % (time.time() - t_start))
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
    start_time = time.time()
    config_file = sys.argv[1]
    module = import_module(config_file)

    for superclass in module.config["classes"]:
        print("\n[Compute knc]", superclass)

        k_max_u = int(get_result(superclass, "k_max_u"))
        k_max_v = int(get_result(superclass, "k_max_v"))

        #TODO: Delete objects to free up space?
        t_start = time.time()
        wmatrix_u = sparse.load_npz("out/" + superclass + ".u.npz")
        print("[Time] load_npz u %.3f sec" % (time.time() - t_start))
        print("[Info] wmatrix_u type", type(wmatrix_u))
        print("[Info] wmatrix_u dtype", wmatrix_u.dtype)
        print("[Info] wmatrix_u nbytes in GB", (wmatrix_u.data.nbytes) / (1024 ** 3))
        count_nonzeroes = wmatrix_u.nnz
        max_nonzeroes = 0.5 * wmatrix_u.shape[0] * (wmatrix_u.shape[0] - 1)
        matrix_density = count_nonzeroes / max_nonzeroes
        print(f"[Info] wmatrix_u nnz {count_nonzeroes}", f"matrix_density {matrix_density}")
        print("[Info] wmatrix_u shape", wmatrix_u.shape)
        print("[Info] find nonzeros\n", wmatrix_u[20,:], wmatrix_u[90,:])
        print("[Info] wmatrix_u maxelement", wmatrix_u.max()) # high time, high space in coo; low time, low space in csr
        t_start = time.time()
        #TODO: Use numpy matrix .npz or pairwise edgelist .csv to construct networkx graph?
        # Fails here, ~30gb in RAM when wmatrix 7,8gb, killed, (1000, 500)
        omgraph_u = nx.from_scipy_sparse_matrix(wmatrix_u) # high time, high space in csr
        print("[Time] from_sparse u %.3f sec" % (time.time() - t_start))
        # Fails here, ~6gb in RAM when wmatrix 21mb, shape(4813, 4813)
        knc_u = compute_knc(omgraph_u, k_max_u)

        t_start = time.time()
        wmatrix_v = sparse.load_npz("out/" + superclass + ".v.npz")
        print("[Time] load_npz v %.3f sec" % (time.time() - t_start))
        print("[Info] wmatrix_v type", type(wmatrix_v))
        print("[Info] wmatrix_v dtype", wmatrix_v.dtype)
        t_start = time.time()
        omgraph_v = nx.from_scipy_sparse_matrix(wmatrix_v)
        print("[Time] from_sparse v %.3f sec" % (time.time() - t_start))
        knc_v = compute_knc(omgraph_v, k_max_v)

        write_knc(superclass, knc_u, knc_v)

    print("\n[Time] compute-knc %.3f sec" % (time.time() - start_time))

main()
