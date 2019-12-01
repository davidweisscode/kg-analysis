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

def read_knc(superclass):
    df = pd.read_csv("csv/" + superclass + ".k.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(superclass, feature):
    df = pd.read_csv("csv/_results.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

# G_U_1 = G_U.copy()
# G_V_1 = G_V.copy()

# # TODO: Refactor into method
# # Calculate connectivity measures
# densitySum = 0
# for k in tqdm(range(1, k_max_U + 1)):
#     densitySum += nx.classes.function.density(G_U)#TODO: Calculate density only one time and save it to variable?
# RC_U = (1 / k_max_U) * densitySum
# print("RC_U = %.4f" % RC_U)

# # Get strongest pairs
# pairs = []
# G_V_adj = nx.to_numpy_matrix(G_V_1)
# for row in range(0, k_max_U):
#     for col in range(0, row):
#         pairs.append((row, col, G_V_adj.item(row, col)))

# sorted_pairs = sorted(pairs, key=lambda x: x[2], reverse=True) # Use edge weight as sorting criterion

# for i in range(0, 10):
#     pair = sorted_pairs[i]
#     print(pair[2], list(G_V_1.nodes)[pair[0]], list(G_V_1.nodes)[pair[1]])

start_time = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Analyze knc]", superclass)
    # .u and .v edgelists only contain nodes, which have at least one connection
    k_max_U = int(get_result(superclass, "k_max_U"))
    k_max_V = int(get_result(superclass, "k_max_V"))
    knc = read_knc(superclass)
    RC_U, RC_V = compute_RC(knc, k_max_U, k_max_V)
    #TODO: Append: RC_U_c1, RC_V_c1, RC_U_c2, RC_V_c2, lower_quartile, median, upper_quartile, slope
    append_result_columns(superclass, RC_U, RC_V)

print("\n[Runtime analyze-knc] %.3f sec" % (time.time() - start_time))
