#!/usr/bin/python3

import sys
import csv
import time
import pandas as pd
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

def read_edgelist(superclass, onemode):
    df = pd.read_csv("csv/" + superclass + "." + onemode + ".csv")
    return list(df.itertuples(index=False, name=None))

def get_k_max(onemode_graph): # TODO: Add error handling
    if onemode_graph == G_U:
        return int(G_V.number_of_nodes())
    if onemode_graph == G_V:
        return int(G_U.number_of_nodes())

def compute_knc(onemode_graph):
    knc_list = []
    for k in tqdm(range(1, get_k_max(onemode_graph) + 1)):
        for edge in list(onemode_graph.edges.data("weight")):
            if edge[2] < k:
                onemode_graph.remove_edge(edge[0], edge[1])
        knc_list.append((k, nx.classes.function.density(onemode_graph))) # TODO: Add other connectivity measures
    return knc_list

def write_knc(superclass, knc_U, knc_V):
    df_U = pd.DataFrame(knc_U, columns=["k", "density"])
    df_V = pd.DataFrame(knc_V, columns=["k", "density"])
    knc = df_U.append(df_V, ignore_index=True)
    knc.to_csv("csv/" + superclass + ".k.csv", index=False)

start_time = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Compute knc]", superclass)

    G_U = nx.Graph()
    G_U_edges = read_edgelist(superclass, "u")
    G_U.add_weighted_edges_from(G_U_edges)

    G_V = nx.Graph()
    G_V_edges = read_edgelist(superclass, "v")
    G_V.add_weighted_edges_from(G_V_edges)

    knc_U = compute_knc(G_U)
    knc_V = compute_knc(G_V)

    write_knc(superclass, knc_U, knc_V)

print("\n[Runtime] %.3f seconds [Compute knc]" % (time.time() - start_time))
