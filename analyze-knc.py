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

# U = list(set(U))
# V = list(set(V))

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

classes = module.config["classes"]

#TODO: Main loop
for superclass in classes:
    #TODO: Append: RC_U_c1, RC_V_c1, RC_U_c2, RC_V_c2, lower_quartile, median, upper_quartile, slope
    print("\n[Analyze knc]", superclass)
    print(read_knc(superclass)) # [(k, c1, c2, ...), (), ...]

print("\nRuntime: %.3f seconds [Compute knc list]" % (time.time() - start_time))
