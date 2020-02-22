"""
Analyze various metrics of a KNC plot.
"""

#!/usr/bin/python3

import sys
from logger import get_time
from importlib import import_module
import pandas as pd
from tqdm import tqdm

def read_knc_list(superclass, onemode):
    """ Read KNC plot values from csv file """
    df = pd.read_csv(f"out/{superclass}/{superclass}.{onemode}.knc.csv")
    return list(df.itertuples(index=False, name=None))

def get_result(run_name, superclass, result):
    """ Get the result value of a superclass """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    return df.loc[superclass, result]

def analyze_knc(run_name, superclass):
    n_t = int(get_result(run_name, superclass, "n_t"))
    n_b = int(get_result(run_name, superclass, "n_b"))

    knc_t = read_knc_list(superclass, "t")
    rc_t_density, rc_t_ncomponents, rc_t_slcc = analyze_knc_onemode(run_name, superclass, knc_t, n_t, n_b)

    knc_b = read_knc_list(superclass, "b")
    rc_b_density, rc_b_ncomponents, rc_b_slcc = analyze_knc_onemode(run_name, superclass, knc_b, n_b, n_t)

    add_results(run_name, superclass,
                rc_t_density=rc_t_density, rc_t_ncomponents=rc_t_ncomponents, rc_t_slcc=rc_t_slcc,
                rc_b_density=rc_b_density, rc_b_ncomponents=rc_b_ncomponents, rc_b_slcc=rc_b_slcc)

def analyze_knc_onemode(run_name, superclass, knc_list, n_max, k_max):
    #TODO: lower_quartile, median, upper_quartile, slope
    return compute_rc(run_name, superclass, knc_list, n_max, k_max)

def compute_rc(run_name, superclass, knc_list, n_max, k_max):
    """ Compute representational consistency (AUC of KNC) based on connectivity measure """
    density_sum = 0
    if len(knc_list[0]) == 4: # Graph was build to compute connectivity measures
        ncomponents_sum = 0
        slcc_sum = 0
        for k in tqdm(range(0, k_max)):
            density_sum += knc_list[k][1]
            ncomponents_sum += (n_max - knc_list[k][2]) / (n_max - 1)
            slcc_sum += (knc_list[k][3] - 1) / (n_max - 1)
        rc_density = (1 / k_max) * density_sum
        rc_ncomponents = (1 / k_max) * ncomponents_sum
        rc_slcc = (1 / k_max) * slcc_sum
        print(f"[Info] rc_density {rc_density:.8f}")
        print(f"[Info] rc_ncomponents {rc_ncomponents:.8f}")
        print(f"[Info] rc_slcc {rc_slcc:.8f}")
        return rc_density, rc_ncomponents, rc_slcc
    elif len(knc_list[0]) == 2: # Weight distribution was used to compute density
        for k in tqdm(range(0, k_max)):
            density_sum += knc_list[k][1]
        rc_density = (1 / k_max) * density_sum
        print(f"[Info] rc_density {rc_density:.8f}")
        return rc_density, None, None

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.loc[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

@get_time
def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    for superclass in run.config["classes"]:
        print("\n[Analyze knc]", superclass)
        try:
            analyze_knc(run_name, superclass)
        except FileNotFoundError as e:
            print(f"[Info] file not found {superclass} graph is the null graph\n{e}")
        except KeyError as e:
            print(f"[Info] key not found {superclass} graph is the null graph\n{e}")

main()
