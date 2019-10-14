from hdt import HDTDocument

document = HDTDocument("swdf.hdt")

# Display metadata
print("unique triples: %i" % document.total_triples)
print("unique subjects: %i" % document.nb_subjects)
print("unique predicates: %i" % document.nb_predicates)
print("unique objects: %i" % document.nb_objects)
print("unique shared subject-object: %i" % document.nb_shared, "\n")

# Query all triples that matches { ?s ?p ?o }
triples, cardinality = document.search_triples("", "", "", limit=3, offset=10)
print("query cardinality", cardinality)
for triple in triples:
  print(triple)

# Searching for triple IDs
triples, cardinality = document.search_triples_ids(0, 0, 0, limit=3, offset=10)

for s, p, o in triples:
  print(s, p, o) # will print 3-element tuples of integers
  print(document.convert_tripleid(s, p, o)) # convert a triple ID to a string format
