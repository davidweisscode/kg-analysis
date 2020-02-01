from multiprocessing import Pool
from logger import get_time, get_ram

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

n = 300000000

# single_3(n)

hyper(n)
