from hdt import HDTDocument

document = HDTDocument("swdf.hdt")

# Display metadata
print("nb triples: %i" % document.total_triples)
print("nb subjects: %i" % document.nb_subjects)
print("nb predicates: %i" % document.nb_predicates)
print("nb objects: %i" % document.nb_objects)
print("nb shared subject-object: %i" % document.nb_shared)

# Fetch all triples that matches { ?s ?p ?o }
(triples, cardinality) = document.search_triples("", "", "", limit=10, offset=10)

for triple in triples:
  print(triple)

# Searching for triple IDs
(triples, cardinality) = document.search_triples_ids(0, 0, 0, limit=10, offset=10)

for s, p, o in triples:
  print(s, p, o) # will print 3-element tuples of integers
  print(document.convert_tripleid(s, p, o)) # convert a triple ID to a string format
