"""
Build a bipartite graph from an n-triples Knowledge Graph representation.
"""

#!/usr/bin/python3

# TODO: Check Googles Python style guide
# TODO: Check pylint
# TODO: Save named log file
# TODO: Optimize changing data structures (nested for loops, DataFrame, ndarray, builtin functions)

import os
import sys
import time
from importlib import import_module
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
import pandas as pd

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
dbo = "http://dbpedia.org/ontology/"
dbr = "http://dbpedia.org/resource/"

# DBpedia classes: http://mappings.dbpedia.org/server/ontology/classes/

def query_subclasses(ontology, superclass):
    """ Query ontology for subclass rdfs-entailment """
    # Option 1: Sequential querying with pyHDT
    # Option 2: Mappings from dataset.join()
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
    t_start = time.time()
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
    #TODO: Remove "dpbedia URL" from subclass names ?
    print("[Time] query-subclasses %.3f sec" % (time.time() - t_start), superclass)
    return subclasses

def get_subject_predicate_tuples(dataset, subclasses, subject_limit, predicate_limit, blacklist):
    """ Get edgelist for a superclass and all its subclasses """
    t_start = time.time()
    subjects = []
    edgelist = []
    print("[Info] Query subjects for each subclass")
    for subclass in tqdm(subclasses):
        triples = dataset.search_triples("", rdf + "type", subclass, limit=subject_limit)[0]
        for triple in triples:
            subjects.append(triple[0])
    print("[Info] Query predicates for each subject")
    for subject in tqdm(subjects):
        triples = dataset.search_triples(subject, "", "", limit=predicate_limit)[0]
        for triple in triples:
            if not triple[1] in blacklist:
                edgelist.append((triple[0], triple[1]))
    print("[Time] get-subj-pred-tuples %.3f sec" % (time.time() - t_start))
    return edgelist

def write_edgelist(classname, edgelist):
    """ Write edgelist to csv file """
    df = pd.DataFrame(edgelist, columns=["u", "v"])
    df.to_csv("out/" + classname + ".g.csv", index=False)

def append_result_rows(superclass, subclasses, number_of_edges):
    """ Append result rows for each superclass """
    df = pd.read_csv("out/_results.csv")
    df.loc[len(df)] = (superclass, subclasses, number_of_edges)
    df.to_csv("out/_results.csv", index=False)

def main():
    config_file = sys.argv[1]
    config_module = import_module(config_file)
    dataset = HDTDocument(config_module.config["kg_source"])
    t_ontology = time.time()
    ontology = Graph().parse(config_module.config["kg_ontology"])
    print("[Time] load-ontology %.3f sec" % (time.time() - t_ontology))
    subject_limit = config_module.config["subject_limit"]
    predicate_limit = config_module.config["predicate_limit"]
    with open("blacklist.txt", "r") as file:
        blacklist = file.read().splitlines()
    if os.path.exists("out/_results.csv"):
        print("[Info] Remove old results file")
        os.remove("out/_results.csv")
    results = pd.DataFrame(columns=["superclass", "subclasses", "num_edges"])
    results.to_csv("out/_results.csv", index=False)

    t_build = time.time()
    for superclass in config_module.config["classes"]:
        print("\n[Build] ", superclass)
        subclasses = query_subclasses(ontology, superclass)
        edgelist = get_subject_predicate_tuples(dataset, subclasses, subject_limit, predicate_limit, blacklist)
        write_edgelist(superclass, edgelist)
        append_result_rows(superclass, subclasses, len(edgelist))
    print("\n[Time] build-edgelist %.3f sec" % (time.time() - t_build))

main()
