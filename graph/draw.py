# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def drawOnePlane(df,title):
    # now we build the graph
    G = nx.Graph()
    # add nodess
    node1_arr = df[['node1']].values
    node2_arr = df[['node2']].values
    nodes_arr = np.hstack((node1_arr, node2_arr))
    nodes_arr = np.unique(nodes_arr)

    for node in nodes_arr:
        G.add_node(node[0])
        pass

    w_edges_arr = []
    n_edges_arr = []
    # add edges
    for _, row in df.iterrows():
        if row['correct_label'] == 0:
            w_edges_arr.append([row['node1'], row['node2']])
        else:
            n_edges_arr.append([row['node1'], row['node2']])
        G.add_edge(row['node1'], row['node2'])
        pass

    plt.figure(title)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos,
                        nodelist=nodes_arr,
                        font_weight='bold',
                        alpha=1.0)
    nx.draw_networkx_edges(G, pos,
                        edgelist= w_edges_arr,
                        width=1.0, alpha=1.0, edge_color='r')
    nx.draw_networkx_edges(G, pos,
                        edgelist= n_edges_arr,
                        width=1.0, alpha=0.5, edge_color='b')
    plt.title(title)
    plt.show()
    pass