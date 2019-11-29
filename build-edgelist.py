#!/usr/bin/python3

# TODO: Python style guide http://google.github.io/styleguide/pyguide.html#3164-guidelines-derived-from-guidos-recommendations
# TODO: Save a log file

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
BLACKLIST = [ #TODO: Outsource to own file
    "http://dbpedia.org/ontology/abstract",
    "http://dbpedia.org/ontology/wikiPageID",
    "http://dbpedia.org/ontology/wikiPageLength",
    "http://dbpedia.org/ontology/wikiPageWikiLink",
    "http://dbpedia.org/ontology/wikiPageOutDegree",
    "http://dbpedia.org/ontology/wikiPageRevisionID",
    "http://dbpedia.org/ontology/wikiPageExternalLink",
    "http://dbpedia.org/ontology/wikiPageWikiLinkText",
    "http://dbpedia.org/property/name",
    "http://dbpedia.org/property/wikiPageUsesTemplate",
    "http://www.w3.org/2002/07/owl#sameAs",
    "http://www.w3.org/ns/prov#wasDerivedFrom",
    "http://www.w3.org/2000/01/rdf-schema#label",
    "http://www.w3.org/2000/01/rdf-schema#comment",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    "http://purl.org/dc/terms/subject",
    "http://xmlns.com/foaf/0.1/isPrimaryTopicOf",
]

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

# Query ontology for subclass rdfs-entailment
def query_subclasses(superclass):
    # Option 1: Mappings from dataset.join()
    # Option 2: Sequential querying with pyHDT
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
    ontology = Graph().parse(module.config["kg_ontology"])
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

# Get edgelist for one superclass using its subclasses
def query_edgelist(subclasses, subject_limit, predicate_limit):
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

# Write edgelist file
def write_edgelist(classname, edgelist):
    #TODO: Create dir if required: https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    df = pd.DataFrame(edgelist, columns=["u", "v"])
    df.to_csv("csv/" + classname + ".g.csv", index=False)

def append_result_rows(superclass, subclasses, number_of_edges):
    df = pd.read_csv("csv/results.csv")
    df.loc[len(df)] = (superclass, subclasses, number_of_edges)
    df.to_csv("csv/results.csv", index=False)

start_time = time.time()

config_file = sys.argv[1]
module = import_module(config_file)

dataset = HDTDocument(module.config["kg_source"])
subject_limit = module.config["subject_limit"]
predicate_limit = module.config["predicate_limit"]

if os.path.exists("csv/results.csv"):
    print("Remove old results file")
    os.remove("csv/results.csv")

results = pd.DataFrame(columns=["superclass", "subclasses", "num_edges"])
results.to_csv("csv/results.csv", index=False)

for superclass in module.config["classes"]:
    print("\n[Build edgelist]", superclass)
    subclasses = query_subclasses(superclass)
    edgelist = query_edgelist(subclasses, subject_limit, predicate_limit)
    write_edgelist(superclass, edgelist)
    append_result_rows(superclass, subclasses, len(edgelist))#TODO: Remove "dpbedia URL" from subclass names

print("\nRuntime: %.3f seconds [Build edgelist]" % (time.time() - start_time))
