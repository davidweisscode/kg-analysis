import networkx as nx
import matplotlib.pyplot as plt

simpleGraph = nx.Graph()

simpleGraph.add_node(1)
simpleGraph.add_node(2)
simpleGraph.add_node(3)

simpleGraph.add_edge(1, 2)
simpleGraph.add_edge(1, 3)

nx.draw(simpleGraph, with_labels=True)
plt.show()
