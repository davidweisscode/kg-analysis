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

def compute_RC(knc, k_max_U, k_max_V):
    density_sum = 0
    for k in tqdm(range(0, k_max_U)):
        density_sum += knc[k][1]
    RC_U = (1 / k_max_U) * density_sum

    density_sum = 0
    for k in tqdm(range(k_max_U, k_max_U + k_max_V)):
        density_sum += knc[k][1]
    RC_V = (1 / k_max_V) * density_sum

    print("RC_U = %.4f" % RC_U, "RC_V = %.4f" % RC_V)
    return RC_U, RC_V

def append_result_columns(superclass, RC_U, RC_V):
    df = pd.read_csv("csv/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "RC_U"] = RC_U
    df.loc[df.index[df["superclass"] == superclass], "RC_V"] = RC_V
    df.to_csv("csv/_results.csv", index=False)

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
