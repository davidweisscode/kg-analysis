"""
Compute points for a KNC plot.
"""

#!/usr/bin/python3

import sys
import time
from scipy import sparse
from importlib import import_module
from logger import get_time, get_ram
import pandas as pd
import networkx as nx
from tqdm import tqdm

def read_om_edgelist(superclass, onemode):
    """ Read onemode edgelist from csv file """
    df = pd.read_csv(f"out/{superclass}.{onemode}.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(run_name, superclass, result):
    """ Get the result value of a superclass """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    return df.loc[superclass, result]

def compute_knc(run_name, superclass, project_method):
    """ Compute points for a KNC plot and save them together in .k.csv """
    n_b = int(get_result(run_name, superclass, "n_b"))
    omgraph_t = load_onemode_graph(superclass, "t", project_method)
    knc_t = compute_knc_onemode(omgraph_t, n_b)
    n_t = int(get_result(run_name, superclass, "n_t"))
    omgraph_b = load_onemode_graph(superclass, "b", project_method)
    knc_b = compute_knc_onemode(omgraph_b, n_t)
    write_knc(superclass, knc_t, knc_b)

def load_onemode_graph(superclass, onemode, project_method):
    """ Load the onemode superclass graph from .onemode.csv """
    if project_method == "dot":
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
        print(f"[Info] wmatrix {onemode} maxelement {wmatrix.max()}")
        t_start = time.time()
        omgraph = nx.from_scipy_sparse_matrix(wmatrix)
        print(f"[Time] from-sparse {onemode} {time.time() - t_start:.3f} sec")
    elif project_method == "hop" or project_method == "intersect" or project_method == "nx":
        t_start = time.time()
        omgraph = nx.Graph()
        omedges = read_om_edgelist(superclass, onemode)
        omgraph.add_weighted_edges_from(omedges)
        print(f"[Time] from-weighted-edgelist {onemode} {time.time() - t_start:.3f} sec")
    return omgraph

@get_time
def compute_knc_onemode(onemode_graph, k_max):
    """ Compute points of an KNC plot """
    # TODO: Break if connectivity measure reached zero
    # TODO: Add other connectivity measures
    # TODO: Build a graph here? Density can be computed manually
    knc_list = []
    graph_density = nx.classes.function.density
    print("[Info] compute connectivity measures")
    for k in tqdm(range(1, k_max + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, graph_density(onemode_graph)))
    return knc_list

@get_time
def write_knc(superclass, knc_t, knc_b):
    """ Save KNC plot points to a csv file """
    df_t = pd.DataFrame(knc_t, columns=["k", "density"])
    df_b = pd.DataFrame(knc_b, columns=["k", "density"])
    knc = df_t.append(df_b, ignore_index=True)
    knc.to_csv(f"out/{superclass}.k.csv", index=False)

@get_time
@get_ram
def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    for superclass in run.config["classes"]:
        print("\n[Compute knc]", superclass)
        try:
            compute_knc(run_name, superclass, run.config["project_method"])
        except KeyError as e:
            sys.exit("[Error] Please specify project_method as 'dot' or 'hop' in run config\n", e)

main()
