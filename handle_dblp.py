# Get edgelist from dblp document dataset

import pandas as pd
from tqdm import tqdm

def write_edgelist(classname, edgelist):
    """ Write edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df.to_csv(f"out/DocumentDBLP/{classname}.g.csv", index=False)

df = pd.read_csv(f"out/DocumentDBLP/DocumentDBLP.g.csv")

# print("len Document", len(df))
# for blacklisted_predicate in blacklist:
#     df = df[df["b"] != blacklisted_predicate]

print("unique n_t", df["t"].nunique())
print("unique n_b", df["b"].nunique())

# print(df["b"].unique()[:3])

# Sample subset of same size as WrittenWork in DBpedia (n_t 90862)
df_samples = pd.DataFrame(columns=["t", "b"])
subj_samples = df["t"].unique()[:90862] #[:90862]
for index, row in tqdm(df.iterrows(), total=len(df)):
    if row["t"] in subj_samples:
        df_samples.loc[index] = row

print("unique samples n_t", df_samples["t"].nunique())
print("unique samples n_b", df_samples["b"].nunique())

edgelist = list(df_samples.itertuples(index=False, name=None))
print("example edges\n", edgelist[:10])
write_edgelist("SampleDocumentDBLP", edgelist)
