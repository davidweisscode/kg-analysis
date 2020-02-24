import math
import random

def generate_fully_uniform(n_t=1000, n_b=200):
    """ Each Top node connected with each Bot node """
    with open("FullyUniform.g.csv", "w") as out_file:
        out_file.write("t,b\n")
        for t in range(1, n_t + 1):
            for b in range(1, n_b + 1):
                out_file.write(f"t{t},b{b}\n")

def generate_80_uniform(n_t=1000, n_b=200):
    """ Each Top node connected with each Bot node with 80% probability """
    with open("HighUniform.g.csv", "w") as out_file:
        out_file.write("t,b\n")
        for t in range(1, n_t + 1):
            for b in range(1, n_b + 1):
                if random.random() < 0.8:
                    out_file.write(f"t{t},b{b}\n")

def generate_2_classes(n_t=1000, n_b=200):
    """
    Two classes in Top, 3 groups in Bot
    First class connected with 80% to 1st group in Bot
    Second class connected with 40% to 2nd and 3rd group in Bot
    """
    with open("2Classes.g.csv", "w") as out_file:
        out_file.write("t,b\n")
        for t in range(1, int(n_t / 2 + 1)):
            for b in range(1, math.floor(n_b / 3) * 2 + 1):
                if random.random() < 0.8:
                    out_file.write(f"t{t},b{b}\n")
        for t in range(int(n_t / 2 + 1), n_t + 1):
            for b in range(math.floor(n_b / 3) + 1, n_b + 1):
                if random.random() < 0.4:
                    out_file.write(f"t{t},b{b}\n")

# generate_fully_uniform()
# generate_80_uniform()
generate_2_classes()
