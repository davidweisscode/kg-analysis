"""
Project a bipartite graph into its two onemode representations.
"""

#!/usr/bin/python3

import sys
import time
import resource
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

def check_connected(bigraph):
    """ Check whether input graph is connected """
    t_start = time.time()
    connected = True
    if not nx.is_connected(bigraph):
        connected = False
        print("[Info] Input graph is not connected")
    print(f"[Time] check-connected {time.time() - t_start:.3f} sec")
    return connected

def check_bipartite(bigraph):
    """ Check whether input graph is bipartite """
    t_start = time.time()
    bipartite = True
    if not nx.bipartite.is_bipartite(bigraph):
        bipartite = False
        sys.exit("[Error] Input graph is not bipartite")
    print(f"[Time] check-bipartite {time.time() - t_start:.3f} sec")
    return bipartite

def split_edgelist(edges):
    """ Split the input edgelist into top (t) and bottom (b) nodes """
    t_start = time.time()
    nodes_top = []
    nodes_bot = []
    for edge in edges:
        nodes_top.append(edge[0])
        nodes_bot.append(edge[1])
    nodes_top = list(set(nodes_top))
    nodes_bot = list(set(nodes_bot))
    print(f"[Time] split-edgelist {time.time() - t_start:.3f} sec")
    return nodes_top, nodes_bot

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.loc[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

def write_edgelist(classname, edgelist, onemode):
    """ Write edge list to csv file """
    df = pd.DataFrame(edgelist, columns=["node_a", "node_b", "w"])
    df.to_csv(f"out/{classname}.{onemode}.csv", index=False)

def project_graph(superclass, run_name, project_method):
    """ Get the onemode representations of the bipartite subject-predicate graph of a superclass """
    # TODO: Save node ordering for future name lookup
    # TODO: Save diagonal values in .csv for analysis of extensively described entities
    # TODO: Separate onemode nodes to use integers as node labels # nx.convert_node_labels_to_integers(bigraph_labeled, ordering="default")
    bigraph = nx.Graph()
    edgelist = read_edgelist(superclass)
    bigraph.add_edges_from(edgelist)
    is_connected = check_connected(bigraph)
    is_bipartite = check_bipartite(bigraph)
    print("[Info] Number of nodes", bigraph.number_of_nodes())
    print("[Info] Number of edges", bigraph.number_of_edges())
    nodes_top, nodes_bot = split_edgelist(edgelist)
    # In onemode network edgelists, data about disconnected nodes gets lost
    n_t, n_b = len(nodes_top), len(nodes_bot)
    add_results(run_name, superclass, n_t=n_t, n_b=n_b, connected=is_connected, bipartite=is_bipartite)

    if project_method == "dot":
        project_dot(superclass, bigraph, nodes_top, nodes_bot)
    elif project_method == "hop":
        project_hop(superclass, bigraph, nodes_top, nodes_bot)
    elif project_method == "intersect":
        project_intersect(superclass, bigraph, nodes_top, nodes_bot)
    elif project_method == "nx":
        project_nx(superclass, bigraph, nodes_top, nodes_bot)

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

def project_hop(superclass, bigraph, nodes_top, nodes_bot):
    """ Project a bipartite graph to its onemode representations in edgelist format """
    project_hop_onemode(superclass, bigraph, "t", nodes_top)
    project_hop_onemode(superclass, bigraph, "b", nodes_bot)

def project_hop_onemode(superclass, bigraph, onemode, onemode_nodes):
    """ Get a weigthed edgelist of a onemode graph by counting distinct hop-2 paths for each node combination """
    t_start = time.time()
    om_edges = []
    all_simple_paths = nx.all_simple_paths
    print(f"[Info] count distinct hop-2 paths for each node pair in {onemode}")
    for node_a, node_b in tqdm(itertools.combinations(onemode_nodes, 2)):
        weight = len(list(all_simple_paths(bigraph, source=node_a, target=node_b, cutoff=2)))
        if weight > 0:
            om_edges.append((node_a, node_b, weight))
    print(f"[Time] count-hop {onemode} {time.time() - t_start:.3f} sec")
    t_start = time.time()
    write_edgelist(superclass, om_edges, onemode)
    print(f"[Time] write-hop-edgelist {onemode} {time.time() - t_start:.3f} sec")

def project_intersect(superclass, bigraph, nodes_top, nodes_bot):
    """ Project a bipartite graph to its onemode representations in edgelist format """
    project_intersect_onemode(superclass, bigraph, "t", nodes_top)
    project_intersect_onemode(superclass, bigraph, "b", nodes_bot)

def project_intersect_onemode(superclass, bigraph, onemode, onemode_nodes):
    """ Get a weigthed edgelist of a onemode graph by intersecting neighbor sets for each node combination """
    t_start = time.time()
    om_edges = []
    print(f"[Info] intersect neighbor sets for each node pair in {onemode}")
    for node_a, node_b in tqdm(itertools.combinations(onemode_nodes, 2)):
        neighbors_a = set(bigraph.neighbors(node_a))
        neighbors_b = set(bigraph.neighbors(node_b))
        weight = len(set.intersection(neighbors_a, neighbors_b))
        if weight > 0:
            om_edges.append((node_a, node_b, weight))
    print(f"[Time] intersect {onemode} {time.time() - t_start:.3f} sec")
    t_start = time.time()
    write_edgelist(superclass, om_edges, onemode)
    print(f"[Time] write-intersect-edgelist {onemode} {time.time() - t_start:.3f} sec")

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
    write_edgelist(superclass, om_edges, onemode)
    print(f"[Time] convert-write-edgelist {onemode} {time.time() - t_start:.3f} sec")

def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    t_project = time.time()
    for superclass in run.config["classes"]:
        print("\n[Project]", superclass)
        try:
            project_graph(superclass, run_name, run.config["project_method"])
        except KeyError as e:
            sys.exit("[Error] Please specify project_method as 'dot' or 'hop' in run config\n", e)

    print(f"\n[Time] project-graphs {time.time() - t_project:.3f} sec")
    max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
    print(f"[Info] {run.config['project_method']} max RAM in GB {max_ram:.6f}")

main()
