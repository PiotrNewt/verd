# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random

from load_data import loadDataWithThresholdList, loadLabels

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
        self.connectedBranch = -1
        pass

    def getAdjNodes(self):
        l = list()
        for k, _ in self.adjNodes_dict:
            l.append(k)
            pass
        return l

# CLEdge represents a edge, used to find and record answer
class CLEdge(object):
    def __init__(self, node1ID, node2ID):
        super(CLEdge, self).__init__()

        # node is the entity node id
        self.node1 = node1ID
        self.node2 = node2ID

        # labels represent the work labels
        self.labels_list = list()
        pass


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

        # fc_threshold represents the fc threshold
        self.fc_threshold = 0.5

        # threshold_list represents the level splited
        self.threshold_list = [[0.3, 0.5],
                            [0.5, 0.7],
                            [0.7, 0.8],
                            [0.8, 0.9],
                            [1.0, 1.0]]

        # dfs_list represents the all records
        self.dfs_list = pd.DataFrame()

        # labels_df represent all the worker labels
        self.labels_df = pd.DataFrame()
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

    def addAdjNodes(self, node, cb_l):
        for adjID, _ in node.adjNodes_dict.items():
            cb_l.append(adjID)
            pass
        pass

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
                    self.addAdjNodes(node, cb[0])
                    j += 1
                    continue

                for adjID, _ in node.adjNodes_dict.items():
                    for b, l in cb.items():
                        if adjID in l:
                            cb[b].append(node.id)
                            self.addAdjNodes(node, cb[b])
                            loop = True
                            break
                        pass

                    if loop == True:
                        loop = False
                        break
                    pass

                cb[j] = list()
                cb[j].append(node.id)
                self.addAdjNodes(node, cb[j])
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

            # write the connectedBranch for each node
            for cdID,li in curcb.items():
                for nodeID in li:
                    subgraph[nodeID].connectedBranch = cdID
                    pass
                pass

            self.connectedBranches_dict[level] = curcb
            print('\r' + 'Calculating the Connected Branch: ' + str((level+1)/len(self.threshold_list) * 100) + '%', end='', flush=True)
            pass
        pass


    # loadNodes loads data and generates a graph
    def loadNodes(self, csvPath, labelsPath):
        self.dfs_list = loadDataWithThresholdList(csvPath, self.threshold_list)

        level = 0
        for df in self.dfs_list:
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

        print("Load Data: 100%\nCalculating the Connected Branch")
        self.calculateCB()

        # get all labels
        self.labels_df = loadLabels(labelsPath)
        pass

    # getLabel gets the label from worker
    def getLabel(self, ask_list):
        df = self.labels_df
        for edge in ask_list:
            l_df = df.loc[((df['node1'] == edge.node1) & (df['node2'] == edge.node2)) | ((df['node1'] == edge.node2) & (df['node2'] == edge.node1))]
            for _, row in l_df.iterrows():
                edge.labels_list.append(row['work_label'])
                pass
        pass


    # askAgain iteratively calculate different nodes
    def askAgain(self, nodes):
        # TODO: any cluster algorithm?
        # 1 如果整个连通分支上的节点都有问题，n 个节点时候 similarity 全部写为 0
        # 2 对有问题的节点记分
        # 3 获取记分最高的节点的邻接节点的 label
        # 4 从这个节点出发分离整个图
        # ---
        # 获取这些点的一些边的 label
        # 如果这些点大多数边 fc 都小于阈值，将他们加入另一个 set
        # ---
        # 判断这个 set 中的点是不是同一类
        # ---
        pass

    # similarityInfer calculate the similarity for nodes in the graph, result will be writed as 0 or 1
    def similarityInfer(self):
        for level, subgraph in self.levelSubGraphs_dict.items():
            cb = self.connectedBranches_dict[level]
            df = self.dfs_list[level]
            later_list = list()
            for _, nodes_list in cb.items():
                # if the number of connected branch nodes is less than or equal to 3, record and package them
                if len(nodes_list) in [2,3]:
                    for nodeID in nodes_list:
                        n_df = df.loc[df.node1 == nodeID]
                        for _, row in n_df.iterrows():
                            edge_obj = CLEdge(row['node1'], row['node2'])
                            later_list.append(edge_obj)
                            pass
                        pass
                    continue

                # apply algorithms on the remaining connected branches
                # for each connected branch, each point randomly takes n edges to obtain the label
                ask_list = list()
                for nodeID in nodes_list:
                    a = random.sample(subgraph[nodeID].adjNodes_dict.keys(), 1)
                    adjID = a[0]
                    edge_obj = CLEdge(nodeID, adjID)
                    ask_list.append(edge_obj)
                    pass

                self.getLabel(ask_list)

                q_list = list()
                for edge in ask_list:
                    if len(edge.labels_list) == 0:
                        continue
                    s = 0
                    for l in edge.labels_list:
                        s += int(l)
                        pass
                    fc = s/len(edge.labels_list)
                    if fc < self.fc_threshold:
                        q_list.append(edge)
                    pass

                if len(q_list) == 0:
                    # TODO: write the results
                    print("all node in cb is same entity, we should write the answers")
                    continue

                # collect nodes
                n_list = list()
                for edge in q_list:
                    n_list.append(edge.node1)
                    n_list.append(edge.node2)
                    pass

                n_list = list(set(n_list))
                # TODO: now we should find the different nodes
                print("need ask: {}".format(n_list))

                pass
            pass
        pass

    def start(self):
        self.loadNodes("./../dataset/paper_pair_test.csv", "./../dataset/5w_paper_alllabels_test")
        print(" ")
        self.similarityInfer()
        pass

if __name__ == "__main__":
    graph_obj = CLGraph()
    graph_obj.start()