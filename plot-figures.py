#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

RED = "#e13232"
GREEN = "#32c832"

#TODO: Read a <classname>.csv file to plot the KNC curve
# Required here: G, U, V, G_U_1, G_V_1, knc_list_U, knc_list_V, 

# Get bipartite coloring
coloring = nx.greedy_color(G)
colorList = []
for node in G.nodes():
    if coloring[node] == 0:
        colorList.append(GREEN)
    else:
        colorList.append(RED)

# Visualize analysis results
plt.subplot(321, frameon=False) # Bipartite graph G
bipartiteLayout = nx.bipartite_layout(G, U, aspect_ratio=0.5, scale=0.2)
nx.draw_networkx(G, bipartiteLayout, with_labels=True, font_size=6, node_color=colorList, edge_color="grey")

# plt.subplot(323, frameon=False) # One mode network G_U
# nx.draw_networkx(G_U_1, nx.circular_layout(G_U_1), with_labels=True, font_size=6, node_color=RED, edge_color="grey")
# nx.draw_networkx_edge_labels(G_U_1, nx.circular_layout(G_U_1), font_size=6)

# plt.subplot(324, frameon=False) # One mode network G_V
# nx.draw_networkx(G_V_1, nx.circular_layout(G_V_1), with_labels=False, node_color=GREEN, edge_color="grey")

plt.subplot(322, frameon=False) # KNC plot
# plt.plot(*zip(*knc_list_U), color="#ff0000")
# plt.plot(*zip(*knc_list_V), color="#00ff00")
plt.bar(list(zip(*knc_list_U))[0], list(zip(*knc_list_U))[1], width=-1/k_max_U, align="edge", color=RED+"aa", edgecolor=RED+"55")
plt.bar(list(zip(*knc_list_V))[0], list(zip(*knc_list_V))[1], width=-1/k_max_V, align="edge", color=GREEN+"aa", edgecolor=GREEN+"55")

G_U_adj = nx.to_numpy_matrix(G_U_1)
G_U_adj[np.triu_indices_from(G_U_adj, 0)] = 0 # Set upper triangle to zeros
ax_U = plt.subplot(325, frameon=False) # Adjacency matrix G_U as heatmap
ax_U.set_xticks(np.arange(len(G_U_1.nodes())))
ax_U.set_yticks(np.arange(len(G_U_1.nodes())))
ax_U.set_xticklabels(G_U_1.nodes()) # TODO: Shorten node names?
ax_U.set_yticklabels(G_U_1.nodes())
plt.setp(ax_U.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
plt.imshow(G_U_adj, interpolation='nearest', cmap=plt.cm.Reds)
plt.colorbar()

G_V_adj = nx.to_numpy_matrix(G_V_1)
G_V_adj[np.triu_indices_from(G_V_adj, 0)] = 0
ax_V = plt.subplot(326, frameon=False) # Adjacency matrix G_V as heatmap
ax_V.set_xticks(np.arange(len(G_V_1.nodes())))
ax_V.set_yticks(np.arange(len(G_V_1.nodes())))
ax_V.set_xticklabels(G_V_1.nodes(), {"fontsize": 6})
ax_V.set_yticklabels(G_V_1.nodes(), {"fontsize": 6})
plt.setp(ax_V.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
plt.imshow(G_V_adj, interpolation='nearest', cmap=plt.cm.Greens)
plt.colorbar()

plt.show()
