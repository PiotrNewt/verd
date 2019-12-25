# -*- coding: utf-8 -*-

import numpy as np

from load_data import loadDataWithThresholdList

# CLNode represents a entity node
class CLNode(object):
    def __init__(self, nodeID):
        super(CLNode, self).__init__()

        # id represents the node id
        self.id = nodeID

        # level represents the level node belong
        self.level = -1

        # adjNodes represents the adjacency of the node
        self.adjNodes_dict = dict()

        # connectedBranch represents which the connected branch belong in which level
        self.connectedBranch_dict = dict()
        pass

    def getAdjNodes(self):
        l = list()
        for k, _ in self.adjNodes_dict:
            l.append(k)
            pass
        return l

# CLGraph represents the similarity graph
class CLGraph(object):
    def __init__(self):
        super(CLGraph, self).__init__()

        # levelSubGraphs represents all sub-graph splited by similarity | {levelID:dict{nodeID:CLNode}}
        self.levelSubGraphs_dict = dict()

        # connectedBranches represents connected branches for every level | {levelIDdict{branchID:List[nodeID]}}
        self.connectedBranches_dict = dict()

        # similarity_threshold represents the similarity threshold, which is the machine result
        self.similarity_threshold = 0.3

        # threshold_list represents the level splited
        self.threshold_list = [[0.3, 0.5],
                            [0.5, 0.7],
                            [0.7, 0.8],
                            [0.8, 0.9],
                            [1.0, 1.0]]
        pass

    # merge duplicate lists
    def mergeDuplicateList(self, cb):
        for k1, inner in cb.items():
            for k2, outer in cb.items():
                if k1 == k2: continue
                l = list(set(inner) & set(outer))
                if len(l) > 0:
                    cb[k1] = list(set(inner+outer))
                    del cb[k2]
                    return cb, False
                pass
            pass
        return cb, True

    # calculateCB calculates the connected branch
    def calculateCB(self):
        for level, subgraph in self.levelSubGraphs_dict.items():
            cb = dict() # cdID:[nodeID]
            j = 0
            loop = False
            for _, node in subgraph.items():

                if j == 0 :
                    cb[0] = list()
                    cb[0].append(node.id)
                    j += 1
                    continue

                for adjID, _ in node.adjNodes_dict.items():
                    for b, l in cb.items():
                        if adjID in l:
                            cb[b].append(node.id)
                            loop = True
                            break
                        pass

                    if loop == True:
                        loop = False
                        break
                    pass

                cb[j] = list()
                cb[j].append(node.id)
                j += 1
                pass

            while 1:
                cb,ok = self.mergeDuplicateList(cb)
                if ok == True: break

            curcb = dict()
            i = 0
            for _,v in cb.items():
                curcb[i] = v
                i += 1

            # write the connectedBranch_dict for each node
            ##

            self.connectedBranches_dict[level] = curcb
            print("calculating the connected branch: {}%".format((level+1)/len(self.threshold_list) * 100))
            pass
        pass


    # loadNodes loads data and generates a graph
    def loadNodes(self, path):
        dfs_list = loadDataWithThresholdList(path, self.threshold_list)

        level = 0
        for df in dfs_list:
            node1_arr = df[['node1']].values
            node2_arr = df[['node2']].values
            nodes_arr = np.hstack((node1_arr, node2_arr))
            nodes_arr = np.unique(nodes_arr)

            # initialize nodes
            nodes_dict = dict()
            for node in nodes_arr:
                nodeID = node
                nodes_dict[nodeID] = CLNode(nodeID)
                pass

            # generate relationship
            for _, row in df.iterrows():
                id1, id2 = row['node1'], row['node2']
                nodes_dict[id1].level = level
                nodes_dict[id1].adjNodes_dict[id2] = row['similarity']
                nodes_dict[id2].level = level
                nodes_dict[id2].adjNodes_dict[id1] = row['similarity']
                pass

            # generate subgraph
            self.levelSubGraphs_dict[level] = nodes_dict
            level += 1
            pass

        print("loadData: 100%\ncalculating the connected branch")
        self.calculateCB()
        pass


    # getCB gets the connected branch of one level subgraph
    def getCB(self, subgraph):
        pass

    def similarityInfer(self, level):
        # subgraph = self.levelSubGraphs_dict[level]
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
        # ---
        pass

    def start(self):
        self.loadNodes("./../dataset/paper_pair.csv")
        # 开始算法
        # (结果放在哪里呢？) --> 结果放在每个节点上
        # 结果写回
        pass

if __name__ == "__main__":
    graph_obj = CLGraph()
    graph_obj.start()