"""
Generate a random graph edgelist based on top and bot degree sequences of real bipartite graphs.
"""

#!/usr/bin/python3

import os
import pandas as pd
import networkx as nx

def read_edgelist(classname, label):
    """ Read real graph edgelist from csv file """
    return pd.read_csv(f"out/{classname}/{classname}.{label}.csv")

def write_edgelist(classname, edgelist):
    """ Write random graph edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df.to_csv(f"out/{classname}Random/{classname}Random.g.csv", index=False)

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.at[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

# Classes of which to create randomized versions
# with same and prescribed degree distribution
# based on .g.csv
classnames = [
    "WrittenWork",
    "Comic",
    "ComicStrip",
    "Manga",
    "PeriodicalLiterature",
    "AcademicJournal",
    "Newspaper",
    "Poem",
]

for classname in classnames:
    if not os.path.exists(f"./out/{classname}Random"):
        os.mkdir(f"./out/{classname}Random")
    real_el = read_edgelist(classname, "g")

    # Degree sequence for top and bot nodes
    tseq = real_el["t"].value_counts().tolist()
    bseq = real_el["b"].value_counts().tolist()

    # Configuration model
        # Resulting degree sequences might not be exact, Simple graph, no multi graph with parallel edges
    # G = nx.bipartite.configuration_model(tseq, bseq, create_using=nx.Graph())
    # Havel Hakimi model
        # High degree nodes connected with high degree nodes first
        # High degree nodes connected with low degree nodes first
        # High degree nodes connected alternating with high and low degree nodes
    G = nx.bipartite.havel_hakimi_graph(tseq, bseq, create_using=nx.Graph())

    write_edgelist(classname, G.edges)

    n_t = len(tseq)
    n_b = len(bseq)
    m_g = G.number_of_edges()
    dens_g = m_g / (n_t * n_b)
    k_t = sum(tseq) / n_t
    k_b = sum(bseq) / n_b

    add_results("random", f"{classname}Random",
                n_t=n_t, n_b=n_b, m_g=m_g,
                dens_g=dens_g, k_t=k_t, k_b=k_b)

    edgelist = G.edges
    print(f"[Info] {classname}")
    print(f"n_t {n_t} n_b {n_b}")
    print(f"m_g {len(pd.DataFrame(edgelist, columns=['t', 'b']).drop_duplicates())} unique out of {sum(tseq)} real")
