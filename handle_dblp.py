# Create classes from dblp document dataset
# Split into journals, conf, ...
# Get edgelists

import pandas as pd

def write_edgelist(classname, edgelist):
    """ Write edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df.to_csv(f"out/{classname}/{classname}.g.csv", index=False)

df = pd.read_csv(f"out/JournalDBLP/DocumentDBLP.g.csv")
print("len Document", len(df))

# for blacklisted_predicate in blacklist:
#     df = df[df["b"] != blacklisted_predicate]

conferences = df["t"].str.contains("/conf/")
df = df[~conferences]
print("len Journal", len(df))

print("unique n_t", df["t"].nunique())
print("unique n_b", df["b"].nunique())

edgelist = list(df.itertuples(index=False, name=None))

print("example edges\n", edgelist[:10])

# TODO: How to sample subset of same size as AcademicJournal in DBpedia (n_t 7688) ?

write_edgelist("JournalDBLP", edgelist)
