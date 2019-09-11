import networkx as nx
import matplotlib.pyplot as plt

data = open("graph.csv", "r")


csvGraph = nx.parse_edgelist(data)


nx.draw(csvGraph, with_labels=True)
plt.show()
