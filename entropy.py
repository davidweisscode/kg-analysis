import math
import numpy as np
import pandas as pd

def entropy(dist):
    unique, count = np.unique(dist, return_counts=True)
    count_norm = count / len(dist)

    ent = 0
    for p in count_norm:
        ent -= p * math.log10(p)

    return ent

def rc(dist):
    unique, count = np.unique(dist, return_counts=True)
    count_norm = count / len(dist)

    rc = 0
    for i in range(0, len(unique)):
        rc += unique[i] * count_norm[i]

    return rc

kncs = {
    "homo": np.array([0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]),
    "hetero_same_stepsize": np.array([1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]),
    "hetero_diff_stepsize": np.array([1.0, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11]),
    "more_slope": np.linspace(0.7, 0.3, 10),
    "less_slope": np.linspace(0.6, 0.4, 10),
    "early_k0": np.array([1.0, 0.8, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "later_k0": np.array([1.0, 0.8, 0.6, 0.5, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0]),
    "early_k0_same_rc": np.array([1.0, 0.8, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "later_k0_same_rc": np.array([0.5, 0.5, 0.3, 0.3, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0]),
    "10_k_max": np.linspace(1.0, 0.0, 10),
    "11_k_max": np.linspace(1.0, 0.0, 11),
    "100_k_max": np.linspace(1.0, 0.0, 100),
    "500_k_max": np.linspace(1.0, 0.0, 500),
    "10000_k_max": np.linspace(1.0, 0.0, 10000),
}

df = pd.DataFrame(columns=["k_max", "entropy", "rc", "norm_rc"])
for kncname, knc in kncs.items():
    df.loc[kncname] = (len(knc), entropy(knc), rc(knc), "?")

print(df)
