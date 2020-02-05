import os
import time
from multiprocessing import Pool, current_process
from logger import get_time, get_ram
from itertools import combinations, islice
from math import ceil

def my_func(x):
    return x * x

@get_time
@get_ram
def single_3(n):
    for batch in range(3):
        for i in range(n):
            my_func(i)

@get_time
@get_ram
def single(n):
    for i in range(n):
        my_func(i)

@get_time
@get_ram
def hyper(n):
    if __name__ == "__main__":
        with Pool() as pool:
            pool.map(single, [n, n, n])

n = 30000000

# single_3(n)

# hyper(n)

my_list = ["a", "b", "c", "d"]
my_al = [('0', {28, 30, 31}), ('1', {32, 33, 35, 29, 30, 31}), ('11', {33, 35, 36, 38, 40}), ('17', {34, 35, 50, 51, 54}), ('6', {55}), ('7', {55}), ('13', {33, 34, 35, 46, 53}), ('15', {33, 35, 44, 46, 47}), ('2', {32, 33, 35, 51}), ('4', {37, 42, 43, 44, 49}), ('5', {27, 28, 29, 30, 31}), ('19', {28, 30, 31}), ('21', {50}), ('20', {48}), ('22', {33, 36, 38, 40, 48}), ('8', {33, 35, 36, 38, 40}), ('12', {33, 34, 35, 36, 52, 55, 56}), ('10', {33, 36, 37, 38, 40}), ('18', {33, 36}), ('3', {33, 34, 35, 36, 38, 39, 40, 51, 27, 28}), ('9', {33, 35, 41, 45, 25, 26}), ('16', {33, 35, 45, 25, 26, 57}), ('23', {33, 35, 36, 51, 28}), ('24', {33, 35, 36, 51, 53, 28}), ('14', {33, 35, 36, 38, 40})]

def project_gen(al_gen):
    """ Get a weigthed edgelist by intersecting pairs from adjacency list generator slices """
    om_edges = []
    for node_a, node_b in al_gen:
        neighbors_a = node_a[1]
        neighbors_b = node_b[1]
        weight = len(set.intersection(neighbors_a, neighbors_b))
        if weight > 0:
            om_edges.append((int(node_a[0]), int(node_b[0]), weight))
    my_process = current_process()
    print(my_process)
    print(my_process.name)
    print(my_process._identity[0])
    print(om_edges, "\n")
    return om_edges
    # TODO: Write batchwise into file

def project_hyper(adj_list):
    gen_pairs = combinations(adj_list, 2)
    n = len(adj_list)
    pairs_len = n * (n - 1) * 0.5
    ncores = os.cpu_count()
    size = ceil(pairs_len / ncores)

    with Pool() as pool:
        gen_slices = [islice(gen_pairs, size * i, size * (i + 1)) for i in range(0, ncores)]
        results = list(pool.map(project_gen, gen_slices))
        print("Result length (k)", len(results), "Slice length", len(results[1]))

if __name__ == "__main__":
    project_hyper(my_al)
