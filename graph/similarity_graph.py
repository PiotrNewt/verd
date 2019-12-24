# -*- coding: utf-8 -*-

import numpy as np

from load_data import loadDataWithThresholdList, dropUselessRows

# CLNode represents a entity node
class CLNode(object):
    def __init__(self, nodeID):
        super(CLNode, self).__init__()

        # id represents the node id
        self.id = nodeID

        # level_set represents which level the node will belong
        self.level_set = set()

        # adjNodes represents the adjacency of the node
        self.adjNodes = dict()
        pass


# CLGraph represents the similarity graph
class CLGraph(object):
    def __init__(self):
        super(CLGraph, self).__init__()

        # levelSubGraphs represents all sub-graph splited by similarity | {levelId:dict{nodeId:CLNode}}
        self.levelSubGraphs = dict()

        # nodes_dict is used to store all nodes
        self.nodes_dict = dict()

        # similarity_threshold represents the similarity threshold, which is the machine result
        self.similarity_threshold = 0.3

        # threshold_list represents the level splited
        self.threshold_list = [[0.3, 0.5],
                            [0.5, 0.7],
                            [0.7, 0.8],
                            [0.8, 0.9],
                            [1.0, 1.0]]
        pass


    # loadNodes loads data and generates a graph
    def loadNodes(self, path):
        df, dfs_list = loadDataWithThresholdList(path, self.threshold_list)

        df = dropUselessRows(df, self.similarity_threshold, 1)
        node1_arr = df[['node1']].values
        node2_arr = df[['node2']].values
        nodes_arr = np.hstack((node1_arr, node2_arr))
        nodes_arr = np.unique(nodes_arr)

        # initialize all nodes
        for node in nodes_arr:
                nodeID = node[0]
                self.nodes_dict[nodeID] = CLNode(nodeID)
                pass

        # generate relationships
        level = 0
        for dfl in dfs_list:
            for _, row in dfl.iterrows():
                id1, id2 = row['node1'], row['node2']
                self.nodes_dict[id1].level_set.add(level)
                self.nodes_dict[id1].adjNodes[id2] = row['similarity']
                self.nodes_dict[id2].level_set.add(level)
                self.nodes_dict[id2].adjNodes[id1] = row['similarity']
                pass
            level += 1
            pass

        # generate subgraph
        for i in range(level):
            subgraph = dict()
            for _, v in self.nodes_dict.items():
                if i in v.level_set:
                    subgraph[v.id] = v
                pass
            self.levelSubGraphs[i] = subgraph
            pass
        pass


    def similarityInfer(self, level):
        subgraph = self.levelSubGraphs[level]
        # core algorithm
        # ---
        # 寻找连通分支
        # ---
        # 对每个连通分支，每个点随机取 n 条边获取 label
        # 计算每个边的 fc
        # 如果所有的 fc 都大于阈值，认为这个点连通分支为同一个 clster
        # 如果存在小于阈值的边，收集这些点
        # 获取这些点的一些边的 label
        # 如果这些点大多数边 fc 都小于阈值，将他们加入另一个 set
        # ---
        # 判断这个 set 中的点是不是同一类
        pass

    def start(self):
        self.loadNodes("./../dataset/paper_pair.csv")
        # 开始算法
        # (结果放在哪里呢？) --> 结果放在每个节点上
        # 结果写回
        pass

