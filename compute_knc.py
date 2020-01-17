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

def read_om_edgelist(superclass, onemode):
    """ Read onemode edgelist from csv file """
    df = pd.read_csv(f"out/{superclass}.{onemode}.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(superclass, feature, run_name):
    """ Get the superclasses value in a feature column """
    df = pd.read_csv(f"out/_results_{run_name}.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

def compute_knc(superclass, run_name, fold_method):
    """ Compute points for a KNC plot and save them together in .k.csv """
    k_max_u = int(get_result(superclass, "k_max_u", run_name))
    omgraph_u = load_onemode_graph(superclass, "u", fold_method)
    knc_u = compute_knc_onemode(omgraph_u, k_max_u)
    k_max_v = int(get_result(superclass, "k_max_v", run_name))
    omgraph_v = load_onemode_graph(superclass, "v", fold_method)
    knc_v = compute_knc_onemode(omgraph_v, k_max_v)
    write_knc(superclass, knc_u, knc_v)

def load_onemode_graph(superclass, onemode, fold_method):
    """ Load the onemode superclass graph from .onemode.csv """
    if fold_method == "dot":
        t_start = time.time()
        wmatrix = sparse.load_npz(f"out/{superclass}.{onemode}.npz")
        print(f"[Time] load-npz {onemode} {time.time() - t_start:.3f} sec")
        print(f"[Info] wmatrix {onemode} type {type(wmatrix)}")
        print(f"[Info] wmatrix {onemode} dtype {wmatrix.dtype}")
        print(f"[Info] wmatrix {onemode} nbytes in GB {(wmatrix.data.nbytes) / (1024 ** 3):.6f}")
        count_nonzeroes = wmatrix.nnz
        max_nonzeroes = 0.5 * wmatrix.shape[0] * (wmatrix.shape[0] - 1)
        matrix_density = count_nonzeroes / max_nonzeroes
        print(f"[Info] wmatrix {onemode} nnz {count_nonzeroes} --> matrix_density {matrix_density:.4f}")
        print(f"[Info] wmatrix {onemode} shape {wmatrix.shape}")
        # print(f"[Info] wmatrix {onemode} find-nonzero-examples\n", wmatrix[2,:], wmatrix[4,:], wmatrix[6,:])
        print(f"[Info] wmatrix {onemode} maxelement {wmatrix.max()}") # high time, high space in coo; low time, low space in csr
        t_start = time.time()
        # Fails here, ~30gb in RAM when wmatrix 7,8gb, killed, (1000, 500)
        omgraph = nx.from_scipy_sparse_matrix(wmatrix) # high time, high space in csr
        print(f"[Time] from-sparse {onemode} {time.time() - t_start:.3f} sec")
    elif fold_method == "hop" or fold_method == "intersect":
        t_start = time.time()
        omgraph = nx.Graph()
        omedges = read_om_edgelist(superclass, onemode)
        omgraph.add_weighted_edges_from(omedges)
        print(f"[Time] from-weighted-edgelist {onemode} {time.time() - t_start:.3f} sec")
    return omgraph

def compute_knc_onemode(onemode_graph, k_max):
    """ Compute points of an KNC plot """
    # TODO: Break if connectivity measure reached zero
    # TODO: Add other connectivity measures
    # TODO: Build a graph here? Density can be computed manually
    t_start = time.time()
    knc_list = []
    graph_density = nx.classes.function.density
    print("[Info] compute connectivity measures")
    for k in tqdm(range(1, k_max + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, graph_density(onemode_graph)))
    print(f"[Time] compute-knc {time.time() - t_start:.3f} sec")
    return knc_list

def write_knc(superclass, knc_u, knc_v):
    """ Save KNC plot points to a csv file """
    t_start = time.time()
    df_u = pd.DataFrame(knc_u, columns=["k", "density"])
    df_v = pd.DataFrame(knc_v, columns=["k", "density"])
    knc = df_u.append(df_v, ignore_index=True)
    knc.to_csv(f"out/{superclass}.k.csv", index=False)
    print(f"[Time] write-knc {time.time() - t_start:.3f} sec")

def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    t_compute = time.time()
    for superclass in run.config["classes"]:
        print("\n[Compute knc]", superclass)
        try:
            compute_knc(superclass, run_name, run.config["fold_method"])
        except KeyError as e:
            sys.exit("[Error] Please specify fold_method as 'dot' or 'hop' in run config\n", e)
    print(f"\n[Time] compute-kncs {time.time() - t_compute:.3f} sec")

main()
