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

def get_result(run_name, superclass, result):
    """ Get the result value of a superclass """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    return df.loc[superclass, result]

def analyze_knc(run_name, superclass):
    #TODO: rc_u_c2, rc_v_c2, lower_quartile, median, upper_quartile, slope
    knc_list = read_knc_list(superclass)
    k_max_u = int(get_result(run_name, superclass, "n_v"))
    results_u = analyze_knc_onemode(run_name, superclass, knc_list[:k_max_u], "v")
    results_v = analyze_knc_onemode(run_name, superclass, knc_list[k_max_u:], "u")
    add_results(run_name, superclass, rc_u=results_u, rc_v=results_v)

def analyze_knc_onemode(run_name, superclass, knc_list, onemode):
    return compute_rc(run_name, superclass, knc_list, onemode)

def compute_rc(run_name, superclass, knc_list, onemode):
    """ Compute representational consistency based on a KNC plot """
    k_max = int(get_result(run_name, superclass, "n_" + onemode))
    density_sum = 0
    for k in tqdm(range(0, k_max)):
        density_sum += knc_list[k][1]
    rc = (1 / k_max) * density_sum
    print(f"rc_{onemode} = {rc:.8f}")
    return rc

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.loc[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    t_analyze = time.time()
    for superclass in run.config["classes"]:
        print("\n[Analyze knc]", superclass)
        analyze_knc(run_name, superclass)
    print(f"\n[Time] analyze-kncs {time.time() - t_analyze:.3f} sec")

main()
