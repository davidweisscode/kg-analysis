"""
Build a bipartite graph from an n-triples Knowledge Graph representation.
"""

#!/usr/bin/python3

# TODO: Check Googles Python style guide
# TODO: Check pylint
# TODO: Only import required parts of libs (nx, pd, ...)

import os
import sys
import time
from importlib import import_module
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from logger import get_time
import pandas as pd
import networkx as nx

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
dbo = "http://dbpedia.org/ontology/"
dbr = "http://dbpedia.org/resource/"

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

@get_time
def query_subclasses(ontology, superclass):
    """ Query ontology for subclass rdfs-entailment """
    # Option 1: Sequential querying with pyHDT
    # Option 2: Mappings from dataset.join()
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
    subclass_query = f"""
    SELECT ?subclass
    WHERE 
    {{
        ?subclass <{str(RDFS['subClassOf'])}>* <{dbo + superclass}> .
    }}
    """
    subclasses = []
    results = ontology.query(subclass_query)
    for result in results:
        subclasses.append(str(result['subclass']))
    return subclasses

@get_time
def get_subject_predicate_tuples(dataset, subclasses, subject_limit, predicate_limit, blacklist):
    """ Get edgelist for superclass and all its subclasses """
    subjects = []
    edgelist = []
    print("[Info] query subjects for each subclass")
    for subclass in tqdm(subclasses):
        if subject_limit > 0:
            triples = dataset.search_triples("", rdf + "type", subclass, limit=subject_limit)[0]
        else:
            triples = dataset.search_triples("", rdf + "type", subclass)[0]
        for triple in triples:
            subjects.append(triple[0])
    subjects = list(set(subjects)) # Include unique subjects if subject is both of type superclass and subclasses
    print("[Info] query predicates for each subject")
    for subject in tqdm(subjects):
        if predicate_limit > 0:
            triples = dataset.search_triples(subject, "", "", limit=predicate_limit)[0]
        else:
            triples = dataset.search_triples(subject, "", "")[0]
        for triple in triples:
            if not triple[1] in blacklist:
                edgelist.append((triple[0], triple[1]))
    return list(set(edgelist)) # Include unique properties

def write_edgelist(classname, edgelist):
    """ Write edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df.to_csv(f"out/{classname}.g.csv", index=False)

@get_time
def write_integer_edgelist(classname, edgelist):
    """ Write edgelist to csv file with node labels converted to unique integers """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df["t"] = pd.Categorical(df["t"])
    df["b"] = pd.Categorical(df["b"])
    b_offset = df["t"].nunique()
    df["t"] = df["t"].cat.codes
    df["b"] = df["b"].cat.codes + b_offset
    df.to_csv(f"out/{classname}.i.csv", index=False)

def check_connected(bigraph):
    """ Check whether input graph is connected """
    connected = True
    if not nx.is_connected(bigraph):
        connected = False
    return connected

def check_bipartite(bigraph):
    """ Check whether input graph is bipartite """
    bipartite = True
    if not nx.bipartite.is_bipartite(bigraph):
        bipartite = False
        sys.exit("[Error] Input graph is not bipartite")
    return bipartite

@get_time
def split_edgelist(edges):
    """ Split the input edgelist into top (t) and bottom (b) nodes """
    nodes_top = []
    nodes_bot = []
    for edge in edges:
        nodes_top.append(edge[0])
        nodes_bot.append(edge[1])
    nodes_top = list(set(nodes_top))
    nodes_bot = list(set(nodes_bot))
    return nodes_top, nodes_bot

def add_results(run_name, superclass, **results):
    """ Append result columns in a superclass row """
    df = pd.read_csv(f"out/_results_{run_name}.csv", index_col=0)
    for resultname, result in results.items():
        df.at[superclass, resultname] = result
    df.to_csv(f"out/_results_{run_name}.csv")

@get_time
def main():
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)
    dataset = HDTDocument(run.config["kg_source"])
    t_ontology = time.time()
    ontology = Graph().parse(run.config["kg_ontology"])
    print(f"\n[Time] load-ontology {time.time() - t_ontology:.3f} sec")
    subject_limit = run.config["subject_limit"]
    predicate_limit = run.config["predicate_limit"]
    with open("blacklist.txt", "r") as file:
        blacklist = file.read().splitlines()
    if not os.path.exists(f"out/_results_{run_name}.csv"):
        df = pd.DataFrame(columns=["m"])
        df.to_csv(f"out/_results_{run_name}.csv")

    for superclass in run.config["classes"]:
        print("\n[Build] ", superclass)
        subclasses = query_subclasses(ontology, superclass)
        edgelist = get_subject_predicate_tuples(dataset, subclasses, subject_limit, predicate_limit, blacklist)
        write_edgelist(superclass, edgelist)
        write_integer_edgelist(superclass, edgelist)

        bigraph = nx.Graph()
        bigraph.add_edges_from(edgelist)
        is_connected = check_connected(bigraph)
        is_bipartite = check_bipartite(bigraph)
        nodes_top, nodes_bot = split_edgelist(edgelist)
        n_t, n_b = len(nodes_top), len(nodes_bot)
        m = len(edgelist)
        density = m / (n_t * n_b)
        k_t = m / n_t
        k_b = m / n_b
        print(f"[Info] n {bigraph.number_of_nodes()}, m {bigraph.number_of_edges()}, t {n_t}, b {n_b}")
        # In onemode network edgelists, information about disconnected nodes gets lost
        add_results(run_name, superclass,
                    connected=is_connected, bipartite=is_bipartite,
                    m=m, n_t=n_t, n_b=n_b,
                    density=density, k_t=k_t, k_b=k_b)

main()
