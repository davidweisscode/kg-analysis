from hdt import HDTDocument

document = HDTDocument("hdt/swdf.hdt")
# TODO: Use DBPedia 2016-04 English

# Get metadata
print("unique triples: %i" % document.total_triples)
print("unique subjects: %i" % document.nb_subjects)
print("unique predicates: %i" % document.nb_predicates)
print("unique objects: %i" % document.nb_objects)
print("unique shared subject-object: %i" % document.nb_shared, "\n")

# Query all triples that matches { ?s ?p ?o }
triples, cardinality = document.search_triples("", "", "", limit=100, offset=10)
print("query cardinality", cardinality)
for triple in triples:
  print(triple)

# Option 1: Extract from mappings
tp_a = ("?s", "http://swrc.ontoware.org/ontology#url", "?o")
tp_b = ("?s", "?p", "http://dh2010.cch.kcl.ac.uk/academic-programme/abstracts/papers/pdf/ab-753.pdf")
iterator = document.search_join([tp_a, tp_b])
print("estimated join cardinality : %i" % len(iterator))
for mapping in iterator:
  print(mapping)

# Option 2: Sequential search for triples
musicians = list()
edge_list = list()
(triples, card) = document.search_triples("?s", "rdf:type", "Musician")
for triple in triples:
  musicians.append(triple[0])
for musician in musicians:
  (triples, card) = document.search_triples(musicians, "", "")
  for triple in triples:
      edge_list.append((musician, triple[1]))

# Construct Graph sequentially, Iterate over edge_list
