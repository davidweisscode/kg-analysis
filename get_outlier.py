import sys
import json
import math
import numpy as np
import pandas as pd

def get_subj_outlier(outlier_dict):
    for classname, peaks in outlier_dict.items():
        print(f"\n{classname}")
        for peak in peaks[0]: # k dist outliers
            save_subj_outlier("k", classname, peak[0], peak[1])
        for peak in peaks[1]: # c dist outliers
            save_subj_outlier("c", classname, peak[0], peak[1])

def save_subj_outlier(disttype, classname, kmin, kmax):
    # global df
    subj_outlier = get_nodes_k_range(disttype, classname, "t", kmin, kmax)
    print(f"\n{disttype} [{kmin} - {kmax}] {len(subj_outlier)}")
    for entity, degree in subj_outlier[:5]:
        print(degree, entity)
        # row = pd.Series({"k":degree, "class":classname, "kmin":kmin, "kmax":kmax}, name=entity)
        # df = df.append(row)

def get_nodes_k_range(disttype, classname, onemode, start, end):
    with open(f"out/{classname}/{classname}.{onemode}.n{disttype}.json", "r") as in_file:
        nodedegrees = json.load(in_file)
    myresults = []
    for entity, degree in nodedegrees.items():
        if degree in range(start, end):
            myresults.append((entity, degree))
    myresults.sort(key=lambda x: x[1])
    return myresults

# Get n lowest predicates for each class
def get_pred_outlier(classnames):
    pred_freq_k = {} # How often a predicate is an outlier across all classes of a run, according to degreedist
    pred_freq_c = {} # How often a predicate is an outlier across all classes of a run, according to connectivitydist
    print("\nPredicates\n")
    for classname in classnames:
        print(f"\n{classname}")
        print("k")
        with open(f"out/{classname}/{classname}.b.nk.json", "r") as in_file:
            ddist = json.load(in_file)
        ddist = {key: ddist[key] for key in sorted(ddist, key=ddist.get, reverse=False)[:10]}
        for entity, degree in ddist.items():
            print(degree, entity)
            pred_freq_k[entity] = pred_freq_k.get(entity, 0) + 1

        print("c")
        with open(f"out/{classname}/{classname}.b.nc.json", "r") as in_file:
            cdist = json.load(in_file)
        cdist = {key: cdist[key] for key in sorted(cdist, key=cdist.get, reverse=False)[:10]}
        for entity, connectivity in cdist.items():
            print(connectivity, entity)
            pred_freq_c[entity] = pred_freq_c.get(entity, 0) + 1

    set_k = set()
    set_c = set()
    # Count how many classes have each predicate in their "n lowest"
    print("\nLeast frequent outlier predicates k")
    pred_freq_k = {key: pred_freq_k[key] for key in sorted(pred_freq_k, key=pred_freq_k.get, reverse=False)}
    # keymax = max(pred_freq_k.keys(), key=(lambda k: pred_freq_k[k]))
    # highest_freq_k = pred_freq_k[keymax]
    for entity, count in pred_freq_k.items():
        print(count, entity)
        if count == 1:
            set_k.add(entity)
    print("\nLeast frequent outlier predicates c")
    pred_freq_c = {key: pred_freq_c[key] for key in sorted(pred_freq_c, key=pred_freq_c.get, reverse=False)}
    # keymax = max(pred_freq_c.keys(), key=(lambda k: pred_freq_c[k]))
    # highest_freq_c = pred_freq_c[keymax]
    for entity, count in pred_freq_c.items():
        print(count, entity)
        if count == 1:
            set_c.add(entity)

    outlier_both = set_k.intersection(set_c)
    print("\nBoth outlier in k and c")
    for outlier in outlier_both:
        print(outlier)



# Subjects in leaf classes # 1st is k dist # 2nd is c dist
outliers_writtenwork = {
    "WrittenWork": (
        [(1,10)],
        [(1,15)]),
    "AcademicJournal": (
        [(0,2), (3,5), (19,21), (60, 110), (400, 610)],
        [(1,5), (10,25), (70,150), (900,1100)]),
    "Comic": (
        [(0,2), (4,7), (20,40), (80,110), (330,400)],
        [(1,10), (10,40), (50,120), (300,500), (600,1000)]),
    "Manga": (
        [(60,70), (700,900)],
        [(50,200), (800,1000), (1000,2000)]),
    "Novel": (
        [(0,2), (2,3)],
        [(1,2), (3,10), (10,22)]),
    "Newspaper": (
        [(20,30), (70,110), (2000,2500)],
        [(20,30), (60,150), (150,210), (300,450)]),
    "Poem": (
        [(10,20), (20,30), (30,40), (100,200)],
        [(4,6), (9,11), (11,18), (20,30), (30,40), (40,60)]),
}
outliers_species = {
    "Bird": (
        [],
        [(0, 1000)]),
    "Crustacean": (
        [],
        [(0, 3000)]),
    "Fish": (
        [],
        [(0, 100)]),
    "ClubMoss": (
        [],
        [(0, 100)]),
    "Fern": (
        [],
        [(0, 3000)]),
}
outliers_athlete = {
    "Boxer": (
        [(10,60), (300,600), (1000, 3000)],
        [(40,100), (300,400), (800,1100)]),
    "AmateurBoxer": (
        [(15,25)],
        [(200,300)]),
    "AmericanFootballPlayer": (
        [(20,40), (550,900)],
        [(80,100), (500,1000)]),
    "MotorsportRacer": (
        [(20,30), (50,100), (800, 1000)],
        [(50,100), (100,200)]),
    "FormulaOneRacer": (
        [(300,400), (700,750), (750, 850)],
        [(700,850), (1500,2000), (2000,3000), (4000,5000)]),
    "NascarDriver": (
        [(20,30), (300,500)],
        [(100,150), (250,350), (800,1000)]),
    "Curler": (
        [(1,6), (100,200)],
        [(1,5), (20,40), (200,400)]),
    "IceHockeyPlayer": (
        [(1,6), (10,20), (80, 200), (1000, 2000)],
        [(20,40), (50,140), (400,500)]),
    "Skier": (
        [(100,200), (200,350), (800, 1100)],
        [(200,500), (1000,2000), (2000,3000)]),
    "BaseballPlayer": (
        [(20,30), (300,400), (1000, 2000)],
        [(10,60), (60,100), (300,500)]),
    "BasketballPlayer": (
        [(10,20), (100,200), (1000, 3000)],
        [(30,50), (100,150)]),
    "ChessPlayer": (
        [(1,10), (200,300)],
        [(10,20), (50,90), (200,300), (1000,2000)]),
    "Cyclist": (
        [(10,20), (20,30), (1000,2000), (4000,5000)],
        [(20,30), (40,60), (1000,1500)]),
    "Fencer": (
        [(20,30), (500,600)],
        [(1,50), (1000,2000)]),
    "GolfPlayer": (
        [(1,9), (10,20), (900,1100)],
        [(1,10), (30,50), (300,500)]),
    "HorseRider": (
        [(8,10), (40,60), (90, 100), (200,250), (300,400)],
        [(1,40), (40,90), (90,150), (400,500), (600,1000)]),
    "SoccerPlayer": (
        [(10,20), (25,35), (50, 80), (200,350), (800,1000), (8000,10000)],
        [(10,80), (100,200), (300,400), (800,1000)]),
    "TennisPlayer": (
        [(8,10), (20,40), (200, 450)],
        [(90,200), (300,500), (2000,3000)]),
}

run = "species_depth"
res = pd.read_csv(f"out/_results_{run}.csv", index_col=0)
res_wikidata_glob = pd.read_csv("out/_results_wikidata.csv", index_col=0)
res_athlete_glob = pd.read_csv("out/_results_athlete.csv", index_col=0)
res_random_glob = pd.read_csv("out/_results_random_run.csv", index_col=0)

# Control which classes to analyze. Add or remove rows in res DataFrame
# res = pd.concat([res, res_athlete_glob, res_wikidata_glob, res_random_glob], sort=True)
# res = res.loc[[
#                 "WrittenWork",# "WrittenWorkRandom",
#                 "AcademicJournal",# "AcademicJournalRandom", "ScientificJournalWikidata",
#                 "Comic",# "ComicRandom", "ComicWikidata",
#                 "Manga",# "MangaRandom",
#                 "Novel",
#                 "PeriodicalLiterature",# "PeriodicalLiteratureRandom",
#                 "Newspaper",# "NewspaperRandom",
#                 "Poem",# "PoemRandom",
#                 # "Boxer",# "BoxerWikidata",
#                 # "Cyclist",# "CyclistWikidata",
#             ]]


# Control which classes to analyze. Add or remove rows in res DataFrame
# print(res.index.tolist())

classes = list(res.index.values)

# df = pd.DataFrame(columns=["k", "class", "kmin", "kmax"])

# Subject outliers may be grouped together
# get_subj_outlier(outliers_species)

classes = [
    "Bird","Crustacean","Fish","ClubMoss","Fern",
]
# Predicate outliers belong to the n least used predicates in multiple classes
# get_pred_outlier(classes)

scatter_ranges = { # 1st for subj, 2nd for pred
    # athlete
    "Athlete": [(200000, 8), (4000, 1600)],
    "Boxer": [(3000, 10), (250, 150)],
    "AmericanFootballPlayer": [(10000, 15), (600, 500)],
    "MotorsportRacer": [(4000, 8), (500, 80)],
    "RacingDriver": [(2800, 7), (350, 80)],
    "NascarDriver": [(500, 12), (150, 120)],
    "IceHockeyPlayer": [(10000, 15), (1250, 700)],
    "Curler": [(500, 7), (130, 70)],
    "ChessPlayer": [(800, 8), (120, 70)],
    "GolfPlayer": [(1500, 10), (200, 200)],
    "SoccerPlayer": [(80000, 11), (1200, 1500)],
    "TennisPlayer": [(2500, 13), (250, 150)],
}
classes = list(scatter_ranges.keys())
def get_scatter_outliers(classes):
    print("\nScatter\n")
    for classname in classes:
        # Top
        print(f"\n{classname} t\n")
        with open(f"out/{classname}/{classname}.t.nk.json", "r") as in_file:
            ddist = json.load(in_file)
        with open(f"out/{classname}/{classname}.t.nc.json", "r") as in_file:
            cdist = json.load(in_file)
        low_degree = set()
        high_degree = set()
        low_avg_edgeweight = set()
        high_avg_edgeweight = set()

        for entity, degree in ddist.items():
            if degree >= scatter_ranges[classname][0][0]:
                high_degree.add(entity)
            else:
                low_degree.add(entity)
        for entity, connectivity in cdist.items():
            aew = connectivity / ddist[entity]
            if aew >= scatter_ranges[classname][0][1]:
                high_avg_edgeweight.add(entity)
            else:
                low_avg_edgeweight.add(entity)

        subj_tl = list(low_degree.intersection(high_avg_edgeweight))
        subj_tr = list(high_degree.intersection(high_avg_edgeweight))
        subj_bl = list(low_degree.intersection(low_avg_edgeweight))
        subj_br = list(high_degree.intersection(low_avg_edgeweight))

        print("tl")
        for subj in subj_tl[:5]:
            print(subj, ddist[subj], round(cdist[subj] / ddist[subj]))
        print("tr")
        for subj in subj_tr[:5]:
            print(subj, ddist[subj], round(cdist[subj] / ddist[subj]))
        print("bl")
        for subj in subj_bl[:5]:
            print(subj, ddist[subj], round(cdist[subj] / ddist[subj]))
        print("br")
        for subj in subj_br[:5]:
            print(subj, ddist[subj], round(cdist[subj] / ddist[subj]))

        # Bot
        print(f"\n{classname} b\n")
        with open(f"out/{classname}/{classname}.b.nk.json", "r") as in_file:
            ddist = json.load(in_file)
        with open(f"out/{classname}/{classname}.b.nc.json", "r") as in_file:
            cdist = json.load(in_file)
        low_degree = set()
        high_degree = set()
        low_avg_edgeweight = set()
        high_avg_edgeweight = set()

        for entity, degree in ddist.items():
            if degree >= scatter_ranges[classname][1][0]:
                high_degree.add(entity)
            else:
                low_degree.add(entity)
        for entity, connectivity in cdist.items():
            aew = connectivity / ddist[entity]
            if aew >= scatter_ranges[classname][1][1]:
                high_avg_edgeweight.add(entity)
            else:
                low_avg_edgeweight.add(entity)

        pred_tl = list(low_degree.intersection(high_avg_edgeweight))
        pred_tr = list(high_degree.intersection(high_avg_edgeweight))
        pred_bl = list(low_degree.intersection(low_avg_edgeweight))
        pred_br = list(high_degree.intersection(low_avg_edgeweight))

        print("tl")
        for pred in pred_tl[:10]:
            print(pred, ddist[pred], round(cdist[pred] / ddist[pred]))
        print("tr")
        for pred in pred_tr[:10]:
            print(pred, ddist[pred], round(cdist[pred] / ddist[pred]))
        print("bl")
        for pred in pred_bl[:10]:
            print(pred, ddist[pred], round(cdist[pred] / ddist[pred]))
        print("br")
        for pred in pred_br[:10]:
            print(pred, ddist[pred], round(cdist[pred] / ddist[pred]))


# Scatter outliers (avg edgeweight vs k)
# get_scatter_outliers(classes)

def get_disc_outliers(classname, onemode):
    # Get nodes of one-mode
    with open(f"out/{classname}/{classname}.{onemode}.nk.json", "r") as in_file:
        ddist = json.load(in_file)
    gnodes = []
    for key, value in ddist.items():
        gnodes.append(key)
    gnodes = set(gnodes)

    # Get nodes of two-mode
    df = pd.read_csv(f"out/{classname}/{classname}.g.csv")
    bnodes = list(df.itertuples(index=False, name=None))
    bnodes = [node[0] for node in bnodes]
    bnodes = set(bnodes)

    discnodes = bnodes - gnodes

    [print(node) for node in discnodes]

get_disc_outliers("Novel", "t")
# build bipartite graph for edge list, get all unique nodes, get difference of set