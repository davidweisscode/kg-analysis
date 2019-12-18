"""
Analyze various metrics of a KNC plot.
"""

#!/usr/bin/python3

import sys
import time
from importlib import import_module
import pandas as pd
from tqdm import tqdm

def read_knc(superclass):
    """ Read KNC plot values from csv file """
    df = pd.read_csv("out/" + superclass + ".k.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(superclass, feature):
    """ Get the superclasses value in a feature column """
    df = pd.read_csv("out/_results.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

def compute_RC(knc, k_max_u, k_max_v):
    """ Compute representational consistency based on a KNC plot """
    density_sum = 0
    for k in tqdm(range(0, k_max_u)):
        density_sum += knc[k][1]
    rc_u = (1 / k_max_u) * density_sum

    density_sum = 0
    for k in tqdm(range(k_max_u, k_max_u + k_max_v)):
        density_sum += knc[k][1]
    rc_v = (1 / k_max_v) * density_sum

    print("rc_u = %.4f" % rc_u, "rc_v = %.4f" % rc_v)
    return rc_u, rc_v

def append_result_columns(superclass, rc_u, rc_v):
    """ Append features in a given superclass row """
    df = pd.read_csv("out/_results.csv")
    df.loc[df.index[df["superclass"] == superclass], "rc_u"] = rc_u
    df.loc[df.index[df["superclass"] == superclass], "rc_v"] = rc_v
    df.to_csv("out/_results.csv", index=False)

start_time = time.time()
config_file = sys.argv[1]
module = import_module(config_file)

for superclass in module.config["classes"]:
    print("\n[Analyze knc]", superclass)
    # .u and .v edgelists only contain nodes, which have at least one connection
    k_max_u = int(get_result(superclass, "k_max_u"))
    k_max_v = int(get_result(superclass, "k_max_v"))
    knc = read_knc(superclass)
    rc_u, rc_v = compute_RC(knc, k_max_u, k_max_v)
    #TODO: Append: rc_u_c1, rc_v_c1, rc_u_c2, rc_v_c2, lower_quartile, median, upper_quartile, slope
    append_result_columns(superclass, rc_u, rc_v)

print("\n[Time] analyze-knc %.3f sec" % (time.time() - start_time))
