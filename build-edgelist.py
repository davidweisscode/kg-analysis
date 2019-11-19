#!/usr/bin/python3

import sys
import csv
import time
import networkx as nx
from tqdm import tqdm
from hdt import HDTDocument
from rdflib import Graph, RDFS
from importlib import import_module

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DBO = "http://dbpedia.org/ontology/"
DBR = "http://dbpedia.org/resource/"
BLACKLIST = [
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

start_time = time.time()

# Read config
config_file = sys.argv[1]
module = import_module(config_file)

# Query ontology for subclass rdfs-entailment
    # Option 1: Mappings from dataset.join()
    # Option 2: Sequential querying with pyHDT
    # Option 3: https://github.com/comunica/comunica-actor-init-sparql-hdt
ontology = Graph().parse(module.config["kgOntology"])
superclass = DBO + module.config["classes"][0] #TODO: Support a list of classes
subclass_query = f"""
SELECT ?subclass
WHERE 
{{
    ?subclass <{str(RDFS['subClassOf'])}>* <{superclass}> .
}}
"""
subclasses = []
results = ontology.query(subclass_query)
for result in results:
    subclasses.append(str(result['subclass']))

# Query dataset
dataset = HDTDocument(module.config["kgSource"])
subjects = []
edge_list = []

for subclass in tqdm(subclasses):
    (triples, card) = dataset.search_triples("", RDF + "type", subclass, limit=2)
    for triple in triples:
        subjects.append(triple[0])

for subject in tqdm(subjects):
    (triples, card) = dataset.search_triples(subject, "", "", limit=100)
    for triple in triples:
        if not triple[1] in BLACKLIST:
            edge_list.append((triple[0], triple[1]))

with open(module.config["classes"][0] + ".g.csv", "w", newline="") as file_out:
    wr = csv.writer(file_out)
    wr.writerows(edge_list)

print("\nScript execution time: %.3f seconds" % (time.time() - start_time))
