import time
import resource
from functools import wraps

def get_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # time.perf_counter() - system time, including time when the Python process is not running
        # time.process_time() - user time, only the time of the Python process
        start = time.perf_counter()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[Time] {func.__name__} {end - start:.3f} sec")
        return func_return_val
    return wrapper

def get_ram(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_return_val = func(*args, **kwargs)
        max_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
        print(f"[Info] {func.__name__} max RAM in GB {max_ram:.6f}")
        return func_return_val
    return wrapper
