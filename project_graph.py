"""
Project a bipartite graph into its two onemode representations.
"""

#!/usr/bin/python3

import os
import sys
import time
import resource
from math import ceil
from tqdm import tqdm
from scipy import sparse
from logger import get_time, get_ram
from itertools import combinations, islice, chain
from importlib import import_module
from multiprocessing import Pool, current_process
import numpy as np
import pandas as pd
import networkx as nx

def read_edgelist(superclass, label):
    """ Read edgelist from csv file """
    df = pd.read_csv(f"out/{superclass}.{label}.csv")
    return list(df.itertuples(index=False, name=None))

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.loc[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

@get_time
def write_edgelist(classname, onemode, edgelist):
    """ Write edge list to csv file """
    df = pd.DataFrame(edgelist, columns=["node_a", "node_b", "w"])
    df.to_csv(f"out/{classname}.{onemode}.csv", index=False)

def project_graph(run_name, superclass, project_method):
    """ Get the onemode representations of the bipartite subject-predicate graph of a superclass """
    edgelist = read_edgelist(superclass, "i") # Are integer node labels better?
    if project_method == "hyper":
        project_hyper(superclass, edgelist)
    elif project_method == "intersect_al":
        project_intersect_al(superclass, edgelist)
    # elif project_method == "intersect":
    #     project_intersect(superclass, bigraph, nodes_top, nodes_bot)
    # elif project_method == "dot":
    #     project_dot(superclass, bigraph, nodes_top, nodes_bot)
    # elif project_method == "hop":
    #     project_hop(superclass, bigraph, nodes_top, nodes_bot)
    # elif project_method == "nx":
    #     project_nx(superclass, bigraph, nodes_top, nodes_bot)

@get_time
@get_ram
def project_hyper(superclass, edgelist):
    al_top = get_adjacencylist(edgelist, "t")
    project_hyper_onemode(superclass, "t", al_top)

    al_bot = get_adjacencylist(edgelist, "b")
    project_hyper_onemode(superclass, "b", al_bot)

@get_time
@get_ram
def project_hyper_onemode(superclass, onemode, adj_list):
    gen_pairs = combinations(adj_list, 2)
    n = len(adj_list)
    pairs_len = n * (n - 1) * 0.5
    ncores = os.cpu_count()
    size = ceil(pairs_len / ncores)
    print(f"[Info] Start {ncores} processes with input length {size}")
    with Pool() as pool:
        gen_slices = [(superclass, onemode, islice(gen_pairs, size * i, size * (i + 1))) for i in range(0, ncores)]
        pool.map(project_gen, gen_slices)
    # TODO: Combine k process files to one single .t.csv

@get_time
@get_ram
def project_gen(al_gen):
    """ Get a weigthed edgelist by intersecting pairs from adjacency list generator slices """
    pid = current_process()._identity[0]
    print(f"[Info] PID {pid:02}")
    with open(f"./out/{al_gen[0]}.{pid:02}.{al_gen[1]}.csv", "a") as output_file:
        for node_a, node_b in al_gen[2]:
            neighbors_a = node_a[1]
            neighbors_b = node_b[1]
            weight = len(set.intersection(neighbors_a, neighbors_b))
            if weight > 0:
                output_file.write(f"{int(node_a[0])}, {int(node_b[0])}, {weight}\n")

@get_ram
def project_intersect_al(superclass, edgelist):
    """ Project a bipartite graph to its onemode representations in edgelist format """
    al_top = get_adjacencylist(edgelist, "t")
    om_edges_top = project_intersect_al_onemode(al_top)
    write_edgelist(superclass, "t", om_edges_top)
    al_bot = get_adjacencylist(edgelist, "b")
    om_edges_bot = project_intersect_al_onemode(al_bot)
    write_edgelist(superclass, "b", om_edges_bot)

@get_time
def project_intersect_al_onemode(onemode_al):
    """ Get a weigthed edgelist of a onemode graph by intersecting neighbor sets for each node combination """
    # TODO: Multiprocessing, divide combinations into k parts
    om_edges = []
    n = len(onemode_al)
    n_iterations = int(n * (n - 1) * 0.5)
    for node_a, node_b in tqdm(combinations(onemode_al, 2), total=n_iterations):
        neighbors_a = node_a[1]
        neighbors_b = node_b[1]
        weight = len(set.intersection(neighbors_a, neighbors_b))
        if weight > 0:
            om_edges.append((int(node_a[0]), int(node_b[0]), weight))
    return om_edges

@get_time
def get_adjacencylist(edgelist, onemode):
    """ Build onemode adjacency list from edgelist """
    al = {}
    if onemode == "t":
        base_node_index = 0
        neighbor_index = 1
    elif onemode == "b":
        base_node_index = 1
        neighbor_index = 0
    for edge in edgelist:
        base_node = str(edge[base_node_index]) # Use integers as dict keys?
        neighbor = edge[neighbor_index]
        if base_node in al:
            al[base_node].add(neighbor)
        else:
            al[base_node] = {neighbor}
    al = list(al.items())
    return al

@get_ram
def project_intersect(superclass, bigraph, nodes_top, nodes_bot):
    """ Project a bipartite graph to its onemode representations in edgelist format """
    om_edges_top = project_intersect_onemode(superclass, bigraph, "t", nodes_top)
    write_edgelist(superclass, "t", om_edges_top)
    om_edges_bot = project_intersect_onemode(superclass, bigraph, "b", nodes_bot)
    write_edgelist(superclass, "b", om_edges_bot)

@get_time
def project_intersect_onemode(superclass, bigraph, onemode, onemode_nodes):
    """ Get a weigthed edgelist of a onemode graph by intersecting neighbor sets for each node combination """
    om_edges = []
    n = len(onemode_nodes)
    n_iterations = int(n * (n - 1) * 0.5)
    print(f"[Info] project_intersect {onemode}")
    for node_a, node_b in tqdm(combinations(onemode_nodes, 2), total=n_iterations):
        neighbors_a = set(bigraph.neighbors(node_a))
        neighbors_b = set(bigraph.neighbors(node_b))
        weight = len(set.intersection(neighbors_a, neighbors_b))
        if weight > 0:
            om_edges.append((node_a, node_b, weight))
    return om_edges

def project_dot(superclass, bigraph, nodes_top, nodes_bot):
    """ project a bipartite graph to its onemode representations in sparse matrix format """
    t_start = time.time()
    A = nx.bipartite.biadjacency_matrix(bigraph, row_order=nodes_top, column_order=nodes_bot, dtype="uint16")
    print(f"[Time] comp-biadj-matrix {time.time() - t_start:.3f} sec")
    print("[Info] A shape", A.shape)
    print("[Info] A dtype", A.dtype)
    project_dot_onemode(superclass, A, "t")
    project_dot_onemode(superclass, A, "b")

def project_dot_onemode(superclass, biadjmatrix, onemode):
    """ Get the weigthed adjacency matrix of the onemode graph by matrix multiplication """
    t_start = time.time()
    if onemode == "t":
        wmatrix = np.dot(biadjmatrix, biadjmatrix.T)
    elif onemode == "b":
        wmatrix = np.dot(biadjmatrix.T, biadjmatrix)
    print(f"[Time] onemode-dotproduct {onemode} {time.time() - t_start:.3f} sec")
    print(f"[Info] wmatrix {onemode} type {type(wmatrix)}")
    print(f"[Info] wmatrix {onemode} dtype {wmatrix.dtype}")
    print(f"[Info] wmatrix {onemode} nbytes in GB {(wmatrix.data.nbytes + wmatrix.indptr.nbytes + wmatrix.indices.nbytes) / (1024 ** 3):.6f}")
    print(f"[Info] wmatrix {onemode} shape {wmatrix.shape}")
    print(f"[Info] wmatrix {onemode} maxelement {wmatrix.max()}")
    count_nonzeroes = wmatrix.nnz
    max_nonzeroes = wmatrix.shape[0] * (wmatrix.shape[0] - 1)
    matrix_density = count_nonzeroes / max_nonzeroes
    print(f"[Info] wmatrix {onemode} density {matrix_density:.4f}")
    t_start = time.time()
    wmatrix = sparse.tril(wmatrix, k=-1) # Fails here for large matrices with high time, high space
    print(f"[Time] wmatrix {onemode} tril {time.time() - t_start:.3f} sec")
    wmatrix = wmatrix.tocsr()
    print(f"[Info] wmatrix {onemode} tril type {type(wmatrix)}")
    print(f"[Info] wmatrix {onemode} tril nbytes data in GB {(wmatrix.data.nbytes) / (1024 ** 3):.6f}")
    t_start = time.time()
    sparse.save_npz(f"out/{superclass}.{onemode}.npz", wmatrix)
    print(f"[Time] save-npz {onemode} {time.time() - t_start:.3f} sec")

def project_hop(superclass, bigraph, nodes_top, nodes_bot):
    """ Project a bipartite graph to its onemode representations in edgelist format """
    project_hop_onemode(superclass, bigraph, "t", nodes_top)
    project_hop_onemode(superclass, bigraph, "b", nodes_bot)

@get_time
def project_hop_onemode(superclass, bigraph, onemode, onemode_nodes):
    """ Get a weigthed edgelist of a onemode graph by counting distinct hop-2 paths for each node combination """
    om_edges = []
    all_simple_paths = nx.all_simple_paths
    print(f"[Info] count distinct hop-2 paths for each node pair in {onemode}")
    for node_a, node_b in tqdm(combinations(onemode_nodes, 2)):
        weight = len(list(all_simple_paths(bigraph, source=node_a, target=node_b, cutoff=2)))
        if weight > 0:
            om_edges.append((node_a, node_b, weight))
    write_edgelist(superclass, onemode, om_edges)

def project_nx(superclass, bigraph, nodes_top, nodes_bot):
    """ Project a bipartite graph to its onemode representations """
    project_nx_onemode(superclass, bigraph, "u", nodes_top)
    project_nx_onemode(superclass, bigraph, "v", nodes_bot)

def project_nx_onemode(superclass, bigraph, onemode, onemode_nodes):
    """ Get a weigthed edgelist of a onemode graph """
    t_start = time.time()
    print(f"[Info] nx weighted projection {onemode}")
    omgraph = nx.algorithms.bipartite.weighted_projected_graph(bigraph, onemode_nodes)
    print(f"[Time] nx {onemode} {time.time() - t_start:.3f} sec")
    t_start = time.time()
    om_edges = []
    for edge in omgraph.edges(data=True):
        om_edges.append((edge[0], edge[1], edge[2]["weight"]))
    write_edgelist(superclass, onemode, om_edges)
    print(f"[Time] convert-write-edgelist {onemode} {time.time() - t_start:.3f} sec")

@get_time
@get_ram
def main():
    if __name__ == "__main__":
        run_name = sys.argv[1][:-3]
        run = import_module(run_name)
        
        for superclass in run.config["classes"]:
            print("\n[Project]", superclass)
            try:
                project_graph(run_name, superclass, run.config["project_method"])
            except KeyError as e:
                sys.exit("[Error] Please specify project_method as 'dot' or 'hop' in run config\n", e)

main()
