"""
This is a docstring. Contained in a module.
"""

#!/usr/bin/python3

# TODO: Check Googles Python style guide
# TODO: Check pylint
# TODO: Save named log file

import os
import sys
import time
from importlib import import_module
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
import pandas as pd

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DBO = "http://dbpedia.org/ontology/"
DBR = "http://dbpedia.org/resource/"

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

def query_subclasses(superclass):
    """ Query ontology for subclass rdfs-entailment """
    # Option 1: Mappings from dataset.join()
    # Option 2: Sequential querying with pyHDT
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
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
    #TODO: Remove "dpbedia URL" from subclass names ?
    return subclasses

def get_subject_predicate_tuples(subclasses, subject_limit, predicate_limit):
    """ Get edgelist for a superclass and all its subclasses """
    subjects = []
    edgelist = []
    print("Query subjects for each subclass")
    for subclass in tqdm(subclasses):
        triples = dataset.search_triples("", RDF + "type", subclass, limit=subject_limit)[0]
        for triple in triples:
            subjects.append(triple[0])
    print("Query predicates for each subject")
    for subject in tqdm(subjects):
        triples = dataset.search_triples(subject, "", "", limit=predicate_limit)[0]
        for triple in triples:
            if not triple[1] in BLACKLIST:
                edgelist.append((triple[0], triple[1]))
    return edgelist

def write_edgelist(classname, edgelist):
    """ Write edge list to csv file """
    df = pd.DataFrame(edgelist, columns=["u", "v"])
    df.to_csv("csv/" + classname + ".g.csv", index=False)

def append_result_rows(superclass, subclasses, number_of_edges):
    """ Append result rows for each superclass """
    df = pd.read_csv("csv/_results.csv")
    df.loc[len(df)] = (superclass, subclasses, number_of_edges)
    df.to_csv("csv/_results.csv", index=False)

#TODO: Setup: Check, create and reset any missing dirs or files
#             (csv, kg, _results.csv, csv/*.csv, config, log.txt)
with open("blacklist.txt", "r") as file:
    BLACKLIST = file.read().splitlines()
config_file = sys.argv[1]
module = import_module(config_file)
dataset = HDTDocument(module.config["kg_source"])
t_ontology = time.time()
ontology = Graph().parse(module.config["kg_ontology"])
print("\n[Runtime] load-ontology %.3f sec" % (time.time() - t_ontology))
subject_limit = module.config["subject_limit"]
predicate_limit = module.config["predicate_limit"]
if os.path.exists("csv/_results.csv"):
    print("Remove old results file")
    os.remove("csv/_results.csv")
results = pd.DataFrame(columns=["superclass", "subclasses", "num_edges"])
results.to_csv("csv/_results.csv", index=False)

t_build = time.time()

for superclass in module.config["classes"]:
    print("\n[Build edgelist]", superclass)
    subclasses = query_subclasses(superclass)
    edgelist = get_subject_predicate_tuples(subclasses, subject_limit, predicate_limit)
    write_edgelist(superclass, edgelist)
    append_result_rows(superclass, subclasses, len(edgelist))

print("\n[Runtime] build-edgelist %.3f sec" % (time.time() - t_build))
