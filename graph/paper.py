# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# paper_df is the paper data load from .csv
paper_df = pd.read_csv("./../dataset/paper_pair.csv", usecols=['pair_id','correct_label','similarity'])
pair_id_arr = paper_df[['pair_id']].values

# we split node id here
node1_arr = []
node2_arr = []
for idStr in pair_id_arr:
    arr = idStr[0].split('_')
    node1_arr.append(arr[0])
    node2_arr.append(arr[1])
    pass

node_data = {'node1':node1_arr, 'node2':node2_arr}
node_df = pd.DataFrame(node_data)
paper_df = node_df.join(paper_df[['correct_label','similarity']])

# we kill some useless rows here
threshold = 0.3
paper_df = paper_df.drop(paper_df[paper_df.similarity < threshold].index)

# now we build the graph
G = nx.Graph()
# add nodes
node1_arr = paper_df[['node1']].values
node2_arr = paper_df[['node2']].values
nodes_arr = np.hstack((node1_arr, node2_arr))
nodes_arr = np.unique(nodes_arr)

for node in nodes_arr:
    G.add_node(node[0])
    pass

w_edges_arr = []
n_edges_arr = []
# add edges
for _, row in paper_df.iterrows():
    if row['correct_label'] == 0:
        w_edges_arr.append([row['node1'], row['node2']])
    else:
        n_edges_arr.append([row['node1'], row['node2']])
    G.add_edge(row['node1'], row['node2'])
    pass

pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos,
                       nodelist=nodes_arr,
                       node_color='k',
                       alpha=0.8)
nx.draw_networkx_edges(G, pos,
                       edgelist= w_edges_arr,
                       width=1.0, alpha=1.0, edge_color='r')
nx.draw_networkx_edges(G, pos,
                       edgelist= n_edges_arr,
                       width=1.0, alpha=0.5, edge_color='b')
plt.show()
