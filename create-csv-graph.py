import networkx as nx
import matplotlib.pyplot as plt

data = open("simple-query.csv", "r")
next(data, None)

simpleGraph = nx.parse_edgelist(data, delimiter=",")

leftSide = nx.bipartite.sets(simpleGraph)[0]

bipartiteLayout = nx.bipartite_layout(simpleGraph, leftSide, aspect_ratio=0.5, scale=0.2)

nx.draw_networkx(simpleGraph, bipartiteLayout, with_labels=True, font_size=10, edge_color="grey")
plt.show()
