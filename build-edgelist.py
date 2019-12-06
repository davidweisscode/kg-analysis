#!/usr/bin/python3

# TODO: Python style guide http://google.github.io/styleguide/pyguide.html#3164-guidelines-derived-from-guidos-recommendations
# TODO: Save named log file

import os
import sys
import csv
import time
import pandas as pd
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DBO = "http://dbpedia.org/ontology/"
DBR = "http://dbpedia.org/resource/"

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

# Query ontology for subclass rdfs-entailment
def query_subclasses(superclass):
    # Option 1: Mappings from dataset.join()
    # Option 2: Sequential querying with pyHDT
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
    ontology = Graph().parse(module.config["kg_ontology"])#TODO: Do this only once?
    subclass_query = f"""
    SELECT ?subclass
    WHERE 
    {{
        ?subclass <{str(RDFS['subClassOf'])}>* <{DBO + superclass}> .
    }}
    """
    subclasses = []
    results = ontology.query(subclass_query)
    for result in results:
        subclasses.append(str(result['subclass']))
    return subclasses

# Get edgelist for a superclass and all its subclasses
def get_subject_predicate_tuples(subclasses, subject_limit, predicate_limit):
    subjects = []
    edgelist = []
    print("Query subjects for each subclass")
    for subclass in tqdm(subclasses):
        (triples, card) = dataset.search_triples("", RDF + "type", subclass, limit=subject_limit)
        for triple in triples:
            subjects.append(triple[0])
    print("Query predicates for each subject")
    for subject in tqdm(subjects):
        (triples, card) = dataset.search_triples(subject, "", "", limit=predicate_limit)
        for triple in triples:
            if not triple[1] in BLACKLIST:
                edgelist.append((triple[0], triple[1]))
    return edgelist

def write_edgelist(classname, edgelist):
    df = pd.DataFrame(edgelist, columns=["u", "v"])
    df.to_csv("csv/" + classname + ".g.csv", index=False)#TODO: Create dir if required

def append_result_rows(superclass, subclasses, number_of_edges):
    df = pd.read_csv("csv/_results.csv")
    df.loc[len(df)] = (superclass, subclasses, number_of_edges)
    df.to_csv("csv/_results.csv", index=False)

start_time = time.time()
with open("blacklist.txt", "r") as file:
    BLACKLIST = file.read().splitlines()
config_file = sys.argv[1]
module = import_module(config_file)

dataset = HDTDocument(module.config["kg_source"])
subject_limit = module.config["subject_limit"]
predicate_limit = module.config["predicate_limit"]

if os.path.exists("csv/_results.csv"):
    print("Remove old results file")
    os.remove("csv/_results.csv")

results = pd.DataFrame(columns=["superclass", "subclasses", "num_edges"])
results.to_csv("csv/_results.csv", index=False)

for superclass in module.config["classes"]:
    print("\n[Build edgelist]", superclass)
    subclasses = query_subclasses(superclass)
    edgelist = get_subject_predicate_tuples(subclasses, subject_limit, predicate_limit)
    write_edgelist(superclass, edgelist)
    append_result_rows(superclass, subclasses, len(edgelist))#TODO: Remove "dpbedia URL" from subclass names

print("\n[Runtime build-edgelist] %.3f sec" % (time.time() - start_time))
