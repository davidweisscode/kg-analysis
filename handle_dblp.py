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

print("unique n_b", df["b"].unique())

# 22 unique predicates used in DBLP
# [
#  'http://purl.org/dc/elements/1.1/identifier'
#  'http://swrc.ontoware.org/ontology#volume'
#  'http://purl.org/dc/elements/1.1/type'
#  'http://purl.org/dc/elements/1.1/title'
#  'http://purl.org/dc/terms/issued'
#  'http://purl.org/dc/elements/1.1/creator'
#  'http://xmlns.com/foaf/0.1/homepage'
#  'http://swrc.ontoware.org/ontology#series'
#  'http://purl.org/dc/terms/partOf'
#  'http://swrc.ontoware.org/ontology#number'
#  'http://xmlns.com/foaf/0.1/maker'
#  'http://swrc.ontoware.org/ontology#pages'
#  'http://purl.org/dc/terms/bibliographicCitation'
#  'http://swrc.ontoware.org/ontology#journal'
#  'http://purl.org/dc/elements/1.1/subject'
#  'http://purl.org/dc/terms/tableOfContent'
#  'http://swrc.ontoware.org/ontology#isbn'
#  'http://purl.org/dc/elements/1.1/publisher'
#  'http://swrc.ontoware.org/ontology#month'
#  'http://xmlns.com/foaf/0.1/page'
#  'http://swrc.ontoware.org/ontology#editor'
#  'http://purl.org/dc/terms/references'
# ]

# print(df["b"].unique()[:3])

# # Sample subset of same size as WrittenWork in DBpedia (n_t 90862)
# df_samples = pd.DataFrame(columns=["t", "b"])
# subj_samples = df["t"].unique()[:90862] #[:90862]
# for index, row in tqdm(df.iterrows(), total=len(df)):
#     if row["t"] in subj_samples:
#         df_samples.loc[index] = row

# print("unique samples n_t", df_samples["t"].nunique())
# print("unique samples n_b", df_samples["b"].nunique())

# edgelist = list(df_samples.itertuples(index=False, name=None))
# print("example edges\n", edgelist[:10])
# write_edgelist("SampleDocumentDBLP", edgelist)
