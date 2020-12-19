"""
Build a bipartite graph from an n-triples Knowledge Graph representation.
"""

#!/usr/bin/python3

# TODO: Check Googles Python style guide
# TODO: Check pylint
# TODO: Remove .pack file from git history https://rtyley.github.io/bfg-repo-cleaner/

import os
import sys
import time
from tqdm import tqdm
from hdt import HDTDocument
from logger import get_time
from rdflib import Graph, RDFS
from importlib import import_module
import pandas as pd
import networkx as nx

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
dbo = "http://dbpedia.org/ontology/"
dbr = "http://dbpedia.org/resource/"

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

@get_time
def query_subclasses(superclass):
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
    t_ontology = time.time()
    ontology = Graph().parse(run.config["kg_ontology"])
    print(f"\n[Time] load-ontology {time.time() - t_ontology:.3f} sec")
    results = ontology.query(subclass_query)
    for result in results:
        subclasses.append(str(result['subclass']))
    return subclasses

@get_time
def extract_dbpedia(superclass):
    """ Get edgelist for superclass and all its subclasses """
    edgelist = []
    instances = set()
    doc = HDTDocument(run.config["kg_source"])
    subject_limit = run.config["subject_limit"]
    predicate_limit = run.config["predicate_limit"]
    subclasses = query_subclasses(superclass)
    print("[Info] query instances for each subclass")
    for subclass in tqdm(subclasses):
        if subject_limit > 0:
            (triples, count) = doc.search_triples("", rdf + "type", subclass, limit=subject_limit)
        else:
            (triples, count) = doc.search_triples("", rdf + "type", subclass)
        for triple in triples:
            instances.add(triple[0])
    print("[Info] query predicates for each instance")
    for subject in tqdm(instances):
        if predicate_limit > 0:
            triples = doc.search_triples(subject, "", "", limit=predicate_limit)[0]
        else:
            (triples, count) = doc.search_triples(subject, "", "")
        for triple in triples:
            # Either blacklist
            if not triple[1] in blacklist:
                edgelist.append((triple[0], triple[1]))
            # Or whitelist
            # if triple[1] in whitelist:
            #     edgelist.append((triple[0], triple[1]))
    return list(set(edgelist)) # Exclude duplicate entity-property relations

def extract_wikidata(classname, typeproperty):
    doc = HDTDocument("kg/wikidata-20170313-all-BETA.hdt")
    wd = "http://www.wikidata.org/entity/"
    wdt = "http://www.wikidata.org/prop/direct/"
    wd_classes = {
        "BoxerWikidata" : "Q11338576",
        "CyclistWikidata": "Q2309784",
        "CapitalWikidata" : "Q5119",
        "CountryWikidata" : "Q6256",
        "MetroAreaWikidata" : "Q1907114",
        "GeographicRegionWikidata" : "Q82794",
        "FilmFestivalWikidata" : "Q220505",
    }
    edgelist = []
    instances = set()
    (triples, count) = doc.search_triples("", f"{wdt}{typeproperty}", f"{wd}{wd_classes[classname]}")

    for triple in triples:
        instances.add(triple[0])

    for instance in tqdm(instances, total=len(instances)):
        (triples, count) = doc.search_triples(instance, "", "")
        for triple in triples:
            if not triple[1] in blacklist:
                edgelist.append((triple[0], triple[1]))

    return list(set(edgelist)) # Exclude duplicate entity-property relations

def write_edgelist(classname, edgelist):
    """ Write edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df.to_csv(f"out/{classname}/{classname}.g.csv", index=False)

def write_integer_edgelist(classname, edgelist):
    """ Write edgelist to csv file with node labels converted to unique integers """
    df = pd.DataFrame(edgelist, columns=["t", "b"])
    df["t"] = pd.Categorical(df["t"])
    df["b"] = pd.Categorical(df["b"])
    b_offset = df["t"].nunique()
    df["t"] = df["t"].cat.codes
    df["b"] = df["b"].cat.codes + b_offset
    df.to_csv(f"out/{classname}/{classname}.i.csv", index=False)

def check_connected(bigraph):
    """ Check whether input graph is connected and throw NetworkXPointlessConcept if null graph """
    print("[Info] Graph connected", nx.is_connected(bigraph))

def check_bipartite(bigraph):
    """ Check whether input graph is bipartite """
    if not nx.bipartite.is_bipartite(bigraph):
        sys.exit("[Error] Input graph is not bipartite")

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

if __name__ == "__main__":
    run_name = sys.argv[1][:-3]
    run = import_module(run_name)

    with open("blacklist.txt", "r") as file:
        blacklist = file.read().splitlines()
    with open("whitelist-boxer.txt", "r") as file:
        whitelist = file.read().splitlines()
    if not os.path.exists(f"out/_results_{run_name}.csv"):
        df = pd.DataFrame(columns=["n_t"])
        df.to_csv(f"out/_results_{run_name}.csv")

    for superclass in run.config["classes"]:
        print("\n[Build] ", superclass)
        if not os.path.exists(f"./out/{superclass}"):
                os.mkdir(f"./out/{superclass}")

        if superclass == "Mixed":
            df = pd.read_csv(f"out/{superclass}/{superclass}.g.csv")
            edgelist = list(df.itertuples(index=False, name=None))

        elif run.config["kg_source"] == "kg/wikidata-20170313-all-BETA.hdt":
            # "instance_of" :  "P31"
            # "occupation" : "P106"
            edgelist = extract_wikidata(superclass, "P31")
            write_edgelist(superclass, edgelist)

        elif run.config["kg_source"] == "kg/dbpedia2016-04en.hdt":
            edgelist = extract_dbpedia(superclass)
            write_edgelist(superclass, edgelist)

        try:
            bigraph = nx.Graph()
            bigraph.add_edges_from(edgelist)
            check_connected(bigraph)
            check_bipartite(bigraph)
            nodes_top, nodes_bot = split_edgelist(edgelist)
            n_t, n_b = len(nodes_top), len(nodes_bot)
            m_g = len(edgelist)
            dens_g = m_g / (n_t * n_b)
            k_t_g = m_g / n_t
            k_b_g = m_g / n_b
            print(f"[Info] n_t {n_t}, n_b {n_b}, m_g {len(edgelist)}")
            # In onemode network edgelists, information about disconnected nodes gets lost
            add_results(run_name, superclass,
                        n_t=n_t, n_b=n_b,
                        m_g=m_g, dens_g=dens_g,
                        k_t_g=k_t_g, k_b_g=k_b_g)
        except nx.NetworkXPointlessConcept as e:
            print(f"[Info] {superclass} graph is the null graph\n{e}")
