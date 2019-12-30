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

        # fc represent fc result
        self.fc = -1

        # result represent the similarity result
        self.result = -1
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
            df['answer'] = -2
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
            if len(edge.labels_list) != 0:
                continue
            l_df = df.loc[((df['node1'] == edge.node1) & (df['node2'] == edge.node2)) | ((df['node1'] == edge.node2) & (df['node2'] == edge.node1))]
            for _, row in l_df.iterrows():
                edge.labels_list.append(row['work_label'])
                pass
        pass

    # getFc gets the Fc result
    def getFc(self, a_list, r = False):
        q_list = list()
        for edge in a_list:
            if len(edge.labels_list) == 0:
                continue
            if edge.fc != -1 | edge.result != -1:
                continue

            s = 0
            for l in edge.labels_list:
                s += int(l)
                pass
            fc = s/len(edge.labels_list)
            edge.fc = fc
            if (fc < self.fc_threshold) & (r == True):
                q_list.append(edge)
            pass

        return q_list

    # appendQList append edges to q_list for ask
    def appendQList(self, nodeID, node, q_list):
        for adjID,_ in node.adjNodes_dict.items():
            for e in q_list:
                if ((e.node1 == nodeID) & (e.node2 == adjID)) | ((e.node1 == adjID) & (e.node2 == nodeID)):
                    continue
                edge_obj = CLEdge(nodeID, adjID)
                q_list.append(edge_obj)
                pass
            pass
        pass

    def iterationDo(self, l, q_list, subgraph, cb_node_list):
        r_list = list()
        b_list = list()
        for n in l:
            node = subgraph[n]
            i = 0
            for nid,_ in node.adjNodes_dict.items():
                if nid in l:
                    r_list.append([n,nid])
                    i += 1
                pass
            if i == 0:
                b_list.append(n)
            pass

        for p in r_list:
            for e in q_list:
                if (e.node1 == p[0]  & e.node2 == p[1]) | (e.node1 == p[1] & e.node2 == p[0]):
                    e.result = 1
                pass
            pass

        if len(b_list) == 0:
            return

        for nid in b_list:
            node = subgraph[nid]
            self.appendQList(nid, node, q_list)
            pass

        # iteration
        self.askAgain(q_list, cb_node_list, subgraph)
        pass

    # askAgain iteratively calculate different nodes
    def askAgain(self, q_list, cb_node_list, subgraph):
        # 1 if there are problems with the nodes on the entire connected branch, the similarity is written as 0 for all n nodes
        n_list = list()
        for edge in q_list:
            if len(edge.labels_list) == 0:
                n_list.append(edge.node1)
                n_list.append(edge.node2)
            pass

        nu_list = list(set(n_list))
        if len(nu_list) == len(cb_node_list) & len(nu_list) <= 5 & len(nu_list) > 0:
            # if no recode rusult the answer is 0
            return

        if len(nu_list) == 0:
            return

        # 2 score problematic nodes
        scoreBoard_dict = dict()
        for node in nu_list:
            scoreBoard_dict[node] = 0
            pass
        for node in n_list:
            scoreBoard_dict[node] += 1
            pass
        nID = -1
        maxS = 0
        for nodeID, s in scoreBoard_dict.items():
            if maxS < s:
                nID = nodeID
                maxS = s
            pass

        # 3 get the label of the adjacent node of the node with the highest score
        node = subgraph[nID]
        self.appendQList(nID, node, q_list)
        self.getLabel(q_list)

        # 4 split
        self.getFc(q_list)

        l1 = list()
        l2 = list()
        for e in q_list:
            if e.fc > self.fc_threshold:
                e.result = 1
                if e.node1 == nID:
                    l1.append(e.node2)
                else:
                    l1.append(e.node1)

            if e.fc < self.fc_threshold:
                e.result = 0
                if e.node1 == nID:
                    l2.append(e.node2)
                else:
                    l2.append(e.node1)
            pass

        l1 = list(set(l1))
        l2 = list(set(l2))
        # for dissimilar nodes, find connected branches
        # write 1 for all points on the connected branch
        # create edges for independent vertices, put in q_list and apply askAgain
        self.iterationDo(l1, q_list, subgraph, cb_node_list)
        self.iterationDo(l2, q_list, subgraph, cb_node_list)
        pass

    # recodeAnswer recodes the answers
    def recodeAnswer(self, level, nodes, q_list, useNodes=False):
        df = self.dfs_list[level]
        if useNodes:
            for node in nodes:
                df.loc[(df['node1']==node) | (df['node2']==node), 'answer'] = 1
                pass
        else:
            for e in q_list:
                df.loc[((df['node1']==e.node1) & (df['node2']==e.node2)) | ((df['node1']==e.node2) & (df['node2']==e.node1)), 'answer'] = e.result
                pass
        pass

    # similarityInfer calculate the similarity for nodes in the graph, result will be writed as 0 or 1
    def similarityInfer(self):
        for level, subgraph in self.levelSubGraphs_dict.items():
            cb = self.connectedBranches_dict[level]
            df = self.dfs_list[level]
            later_list = list()
            for _, nodes_list in cb.items():
                # if the number of connected branch nodes is less than or equal to 3, record and package them
                if len(nodes_list) <= 3:
                    n_df = pd.DataFrame()
                    for nID in nodes_list:
                        n1_df = df.loc[df.node1 == nID]
                        n2_df = df.loc[df.node2 == nID]
                        n_df = pd.concat([n_df, n1_df])
                        n_df = pd.concat([n_df, n2_df])
                        pass
                    n_df = n_df.drop_duplicates()
                    for _, row in n_df.iterrows():
                        edge_obj = CLEdge(row['node1'], row['node2'])
                        later_list.append(edge_obj)
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
                q_list = self.getFc(ask_list, r=True)

                if len(q_list) == 0:
                    # TODO: write the results
                    df = self.dfs_list[level]
                    self.recodeAnswer(level, nodes_list, None, useNodes=True)
                    # print("level:{}, cb:{}".format(level, nodes_list))
                    continue

                # askAgain
                self.askAgain(q_list, nodes_list, subgraph)
                # TODO: write the q_list result
                self.recodeAnswer(level, None, q_list)
                # print("level:{}, cb:{}".format(level, nodes_list))
                pass
            pass

            if len(later_list) == 0:
                continue
            self.getLabel(later_list)
            self.getFc(later_list)
            # TODO: write the later_list result
            for e in later_list:
                if e.fc > self.fc_threshold:
                    e.result = 1
                else:
                    e.result = 0
                # print("result:{}".format(e.result))
                pass
            self.recodeAnswer(level, None, later_list)
        pass

    # writeBackAnswer write the answer to a file
    def writeBackAnswer(self, path):
        df_r = pd.DataFrame()
        for df in self.dfs_list:
            df_r = pd.concat([df_r, df], axis=0)
            pass
        df_r.loc[(df_r['answer']==-2) | (df_r['answer']==-1),'answer'] = 0
        df_r.to_csv(path)
        print(df_r)
        pass

    def start(self):
        self.loadNodes("./../dataset/paper_pair_test.csv", "./../dataset/5w_paper_alllabels_test")
        print(" ")
        self.similarityInfer()
        self.writeBackAnswer('./../dataset/' + 'r.csv')
        pass

if __name__ == "__main__":
    graph_obj = CLGraph()
    graph_obj.start()