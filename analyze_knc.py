"""
Analyze various metrics of a KNC plot.
"""

#!/usr/bin/python3

import sys
import time
from importlib import import_module
import pandas as pd
from tqdm import tqdm

def read_knc_list(superclass):
    """ Read KNC plot values from csv file """
    df = pd.read_csv(f"out/{superclass}.k.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(superclass, feature, run_name):
    """ Get the superclasses value in a feature column """
    df = pd.read_csv(f"out/_results_{run_name}.csv")
    return df.loc[df.index[df["superclass"] == superclass][0], feature]

def analyze_knc(superclass, run_name):
    #TODO: rc_u_c2, rc_v_c2, lower_quartile, median, upper_quartile, slope
    knc_list = read_knc_list(superclass)
    k_max_u = int(get_result(superclass, "k_max_u", run_name))
    results_u = analyze_knc_onemode(superclass, knc_list[:k_max_u], "u", run_name)
    results_v = analyze_knc_onemode(superclass, knc_list[k_max_u:], "v", run_name)
    append_result_columns(superclass, results_u, results_v, run_name)

def analyze_knc_onemode(superclass, knc_list, onemode, run_name):
    return compute_rc(superclass, knc_list, onemode, run_name)

def compute_rc(superclass, knc_list, onemode, run_name):
    """ Compute representational consistency based on a KNC plot """
    k_max = int(get_result(superclass, "k_max_" + onemode, run_name))
    density_sum = 0
    for k in tqdm(range(0, k_max)):
        density_sum += knc_list[k][1]
    rc = (1 / k_max) * density_sum
    print(f"rc_{onemode} = {rc:.8f}")
    return rc

def append_result_columns(superclass, rc_u, rc_v, run_name):
    """ Append features in a given superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv")
    df.loc[df.index[df["superclass"] == superclass], "rc_u"] = rc_u
    df.loc[df.index[df["superclass"] == superclass], "rc_v"] = rc_v
    df.to_csv(f"out/_results_{run_name}.csv", index=False)

def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    t_analyze = time.time()
    for superclass in run.config["classes"]:
        print("\n[Analyze knc]", superclass)
        analyze_knc(superclass, run_name)
    print(f"\n[Time] analyze-kncs {time.time() - t_analyze:.3f} sec")

main()
