from rdflib import Graph
from rdflib_hdt import HDTStore, optimize_sparql
from rdflib.namespace import FOAF

# Load an HDT file. Missing indexes are generated automatically
# You can provide the index file by putting it in the same directory as the HDT file.
store = HDTStore("./kg/dbpedia2016-04en.hdt")

# Display some metadata about the HDT document itself
# print(f"Number of RDF triples: {len(store)}")
# print(f"Number of subjects: {store.nb_subjects}")
# print(f"Number of predicates: {store.nb_predicates}")
# print(f"Number of objects: {store.nb_objects}")
# print(f"Number of shared subject-object: {store.nb_shared}")

# Create an RDFlib Graph with the HDT document as a backend
graph = Graph(store=store)

# Fetch all triples that matches { ?s foaf:name ?o }
# Use None to indicates variables
# for s, p, o in graph.triples((None, FOAF["name"], None)): # Pull request
#     print(s, p, o)

# Calling this function optimizes the RDFlib SPARQL engine for HDT documents
optimize_sparql()

# You can execute SPARQL queries using the regular RDFlib API
query_results = graph.query("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?s ?img
    WHERE {
        ?s a dbo:City .
        ?s dbo:thumbnail ?img .
    }
    """)

for row in query_results:
    print(row.s, row.img)
