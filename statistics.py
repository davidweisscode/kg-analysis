import json
import numpy as np
from scipy.stats import skew

classes = [
    "DocumentDBLP",
    "WrittenWork",
    "AcademicJournal",
    "ScientificJournalWikidata"
]

def mean_(val, freq):
    return np.average(val, weights = freq)

def median_(val, freq):
    ord = np.argsort(val)
    cdf = np.cumsum(freq[ord])
    return val[ord][np.searchsorted(cdf, cdf[-1] // 2)]

def mode_(val, freq): #in the strictest sense, assuming unique mode
    return val[np.argmax(freq)]

def var_(val, freq):
    avg = mean_(val, freq)
    dev = freq * (val - avg) ** 2
    return dev.sum() / (freq.sum() - 1)

def std_(val, freq):
    return np.sqrt(var_(val, freq))

def get_stats(classname, onemode):
    with open(f"out/{classname}/{classname}.{onemode}.w.json", "r") as input_file:
        wdist = json.load(input_file)
    wdist = [(int(w), c) for w, c in wdist.items() if int(w) != 0]
    w, c = np.array(wdist).T
    # wdist = np.repeat(weight, count)
    print("\n" + classname)
    print("median", median_(w, c))
    print("mean", mean_(w, c))
    print("mode", mode_(w, c))
    print("sdev", std_(w, c))
    # print("skew", skew(wdist))

for classname in classes:
    get_stats(classname, "b")
