import os
import sys
import time
import resource
import pandas as pd
import networkx as nx
from tqdm import tqdm
from functools import wraps

def loadbuild_add_weighted_edges_from():
    start = time.perf_counter()

    omgraph = nx.Graph()
    df = pd.read_csv(filepath, delim_whitespace=True)
    end = time.perf_counter()
    print(f"[Time] load omedgelist finished {end - start:.3f} sec")
    max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
    print(f"[Info] load omedgelist max RAM {max_ram:.6f} GB")
    start = time.perf_counter()
    omgraph.add_weighted_edges_from([tuple(edge) for edge in df.values])

    end = time.perf_counter()
    print(f"[Time] loadbuild_add_weighted_edges_from finished {end - start:.3f} sec")
    max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
    print(f"[Info] loadbuild_add_weighted_edges_from RAM {max_ram:.6f} GB")
    return omgraph

def loadbuild_read_weighted_edgelist():
    start = time.perf_counter()

    with open(filepath, "rb") as input_file:
        next(input_file, "")
        omgraph = nx.read_weighted_edgelist(input_file) # nodetype=int

    end = time.perf_counter()
    print(f"[Time] loadbuild_read_weighted_edgelist finished {end - start:.3f} sec")
    max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
    print(f"[Info] loadbuild_read_weighted_edgelist max RAM {max_ram:.6f} GB")
    return omgraph

def loadbuild_read_edgelist():
    start = time.perf_counter()

    with open(filepath, "rb") as input_file:
        next(input_file, "")
        omgraph = nx.read_edgelist(input_file, edgetype=int, data=(('w', int),)) # nodetype=int

    end = time.perf_counter()
    print(f"[Time] loadbuild_read_edgelist finished {end - start:.3f} sec")
    max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
    print(f"[Info] loadbuild_read_edgelist max RAM {max_ram:.6f} GB")
    return omgraph

# integer edgelist uses slightly less ram in combination with nx.read_edgelist()
# filepath = "out/integer-edgelist/Boxer.t.csv"
filepath = "out/Boxer.t.csv"

# RAM at start
max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
print(f"[Info] start max RAM {max_ram:.3f} GB")

# Get edgelist filesize
filesize = os.path.getsize(filepath) / (1024 ** 3)
print(f"[Info] size of {filepath} {filesize:.3f} GB")

# Load edgelist and build graph
# omgraph = loadbuild_add_weighted_edges_from()
# omgraph = loadbuild_read_weighted_edgelist()
omgraph = loadbuild_read_edgelist()

# Graph info
print(f"[Info] omgraph number of nodes {omgraph.number_of_nodes()}")
print(f"[Info] omgraph number of edges {omgraph.number_of_edges()}")

# < 0.2 GB does not add up to max_ram at all
print(f"[Info] omgraph space for nodes {sys.getsizeof(list(omgraph.nodes)) / (1024 ** 3):.3f} GB")
print(f"[Info] omgraph space for edges {sys.getsizeof(list(omgraph.edges)) / (1024 ** 3):.3f} GB")
