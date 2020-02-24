"""
Compute points for a KNC plot.
"""

#!/usr/bin/python3

import os
import sys
import time
import json
from scipy import sparse
from importlib import import_module
from logger import get_time, get_ram
import pandas as pd
import networkx as nx
from tqdm import tqdm

def get_result(run_name, superclass, result):
    """ Get the result value of a superclass """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    return df.loc[superclass, result]

def is_buildable(classname, onemode):
    """ Check if onemode edgelist file exists and a networkx graph of it can be loaded into main memory """
    edgelist_file = f"out/{classname}/{classname}.{onemode}.csv"
    nx_max_size = 3
    if os.path.isfile(edgelist_file):
        filesize = os.path.getsize(edgelist_file) / (1000 ** 3)
        if filesize < nx_max_size:
            return True
        else:
            return False
    else:
        return False

def compute_knc(run_name, superclass, project_method):
    """ Compute points for a KNC plot and save them together in .k.csv """
    if is_buildable(superclass, "t"):
        n_b = int(get_result(run_name, superclass, "n_b"))
        omgraph_t = load_onemode_graph(superclass, "t", project_method)
        knc_t = compute_knc_onemode(omgraph_t, n_b)
        write_knc(superclass, knc_t, "t")
    else:
        compute_knc_onemode_weights(run_name, superclass, "t")

    if is_buildable(superclass, "b"):
        n_t = int(get_result(run_name, superclass, "n_t"))
        omgraph_b = load_onemode_graph(superclass, "b", project_method)
        knc_b = compute_knc_onemode(omgraph_b, n_t)
        write_knc(superclass, knc_b, "b")
    else:
        compute_knc_onemode_weights(run_name, superclass, "b")

@get_time
def compute_knc_onemode_weights(run_name, superclass, onemode):
    """ Compute KNC plot based on weight distribution and max edges formula """
    knc = []
    weight_dist = {}
    n_edges = 0
    if onemode == "t":
        n_max = int(get_result(run_name, superclass, f"n_t"))
        k_max = int(get_result(run_name, superclass, f"n_b"))
    elif onemode == "b":
        n_max = int(get_result(run_name, superclass, f"n_b"))
        k_max = int(get_result(run_name, superclass, f"n_t"))
    edges_max = 0.5 * n_max * (n_max - 1)
    with open(f"out/{superclass}/{superclass}.{onemode}.w.json", "r") as input_file:
        weight_dist = json.load(input_file)
    for key, value in weight_dist.items():
        if int(key) > 0:
            n_edges += value
    for k in tqdm(range(1, k_max + 1)):
        edges_miss = 0
        for key, value in weight_dist.items():
            if int(key) > 0 and int(key) < k:
                edges_miss += value
        density = (n_edges - edges_miss) / edges_max
        knc.append((k, density))
    df = pd.DataFrame(knc, columns=["k", "density"])
    df.to_csv(f"out/{superclass}/{superclass}.{onemode}.knc.csv", index=False)

@get_time
def load_onemode_graph(superclass, onemode, project_method):
    """ Load the onemode superclass graph from .onemode.csv """
    if project_method == "dot":
        t_start = time.time()
        wmatrix = sparse.load_npz(f"out/{superclass}.{onemode}.npz")
        print(f"[Time] load-npz {onemode} {time.time() - t_start:.3f} sec")
        print(f"[Info] wmatrix {onemode} type {type(wmatrix)}")
        print(f"[Info] wmatrix {onemode} dtype {wmatrix.dtype}")
        print(f"[Info] wmatrix {onemode} nbytes in GB {(wmatrix.data.nbytes) / (1000 ** 3):.6f}")
        count_nonzeroes = wmatrix.nnz
        max_nonzeroes = 0.5 * wmatrix.shape[0] * (wmatrix.shape[0] - 1)
        matrix_density = count_nonzeroes / max_nonzeroes
        print(f"[Info] wmatrix {onemode} nnz {count_nonzeroes} --> matrix_density {matrix_density:.4f}")
        print(f"[Info] wmatrix {onemode} shape {wmatrix.shape}")
        print(f"[Info] wmatrix {onemode} maxelement {wmatrix.max()}")
        t_start = time.time()
        omgraph = nx.from_scipy_sparse_matrix(wmatrix)
        print(f"[Time] from-sparse {onemode} {time.time() - t_start:.3f} sec")
    else:
        omgraph = nx.Graph()
        df = pd.read_csv(f"out/{superclass}/{superclass}.{onemode}.csv", delim_whitespace=True)
        print("[Info] read edgelist finished")
        omgraph.add_weighted_edges_from([tuple(edge) for edge in df.values])
        print(f"[Info] omgraph number of nodes {onemode} {omgraph.number_of_nodes()}")
    return omgraph

def compute_knc_onemode(onemode_graph, k_max):
    """ Compute points of an KNC plot """
    knc_list = []
    fully_disconnected = False
    get_density = nx.classes.function.density
    get_ncc = nx.algorithms.components.number_connected_components
    get_slcc = nx.algorithms.components.connected_components
    for k in tqdm(range(1, k_max + 1)):
        if not fully_disconnected:
            for edge in list(onemode_graph.edges.data("weight")):
                if int(edge[2]) < k:
                    onemode_graph.remove_edge(edge[0], edge[1])
            density = get_density(onemode_graph)
            ncomponents = get_ncc(onemode_graph)
            slcc = len(max(get_slcc(onemode_graph), key=len))
            if density == 0:
                fully_disconnected = True
        knc_list.append((k, density, ncomponents, slcc))
    return knc_list

@get_time
def write_knc(superclass, knc_list, onemode):
    """ Save KNC plot points to a csv file """
    df = pd.DataFrame(knc_list, columns=["k", "density", "ncomponents", "slcc"])
    df.to_csv(f"out/{superclass}/{superclass}.{onemode}.knc.csv", index=False)

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
            print(f"[Info] file not found {superclass} graph is the null graph\n{e}")

main()
