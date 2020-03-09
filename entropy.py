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
    "hetero_diff_stepsize": np.array([1.0, 0.2, 0.18, 0.15, 0.13, 0.1, 0.08, 0.05, 0.02, 0.01]),
    "more_slope": np.linspace(0.8, 0.3, 10),
    "less_slope": np.linspace(0.6, 0.4, 10),
    "early_k0": np.array([1.0, 0.8, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "later_k0": np.array([1.0, 0.8, 0.6, 0.5, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0]),
    "early_k0_same_rc": np.array([1.0, 0.8, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "later_k0_same_rc": np.array([0.5, 0.5, 0.3, 0.3, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0]),
    "low_k_max": np.linspace(0.8, 0.0, 100),
    "big_k_max": np.linspace(0.8, 0.0, 500),
}

df = pd.DataFrame(columns=["entropy", "rc", "rel_rc"])
for kncname, knc in kncs.items():
    df.loc[kncname] = (entropy(knc), rc(knc), entropy(knc) / rc(knc))

print(df)
