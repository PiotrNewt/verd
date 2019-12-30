# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# dropUselessRows drops some useless rows here
def dropUselessRows(df, threshold_under, threshold_upper):
    df = df.drop(df[df.similarity < threshold_under].index)
    df = df.drop(df[df.similarity > threshold_upper].index)
    return df

# loadDataFromCSV loads data from csv with threshold
def loadDataFromCSV(path):
    df = pd.read_csv(path, usecols=['pair_id','correct_label','similarity'])
    pair_id_arr = df[['pair_id']].values

    # split node id
    node1_arr = []
    node2_arr = []
    for idStr in pair_id_arr:
        arr = idStr[0].split('_')
        node1_arr.append(arr[0])
        node2_arr.append(arr[1])
        pass

    node_data = {'node1':node1_arr, 'node2':node2_arr}
    node_df = pd.DataFrame(node_data)
    df = node_df.join(df[['correct_label','similarity']])
    return df


# loadData loads data by threshold, and it is just used to test
def loadData(path, threshold_under = 0.0, threshold_upper = 1.0):
    df = loadDataFromCSV(path)
    return dropUselessRows(df, threshold_under, threshold_upper)


# loadDataWithThresholdList loads data and splits it by threshold
def loadDataWithThresholdList(path, threshold_list):
    df = loadDataFromCSV(path)

    dfs_list = list()
    for threshold in threshold_list:
        dfs_list.append(dropUselessRows(df, threshold[0], threshold[1]))
        pass

    return dfs_list

# loadLabel loads the worker labels
def loadLabels(path):
    df = pd.DataFrame(columns=('node1', 'node2', 'correct_label', 'work_label'))
    count = len(open(path,'rU').readlines())
    with open(path, 'r') as datafile:
        i = 0
        for line in datafile:
            line = line.strip("\n")
            if line == "":
                continue
            data = line.replace("_"," ")
            node1, node2, correct_label, work_label = data.split(" ")
            df.loc[i] = [node1, node2, correct_label, work_label]
            i += 1
            print('\r' + 'Load Labels: ' + str(round(i/count*100, 2)) + '%', end='', flush=True)
            pass

    return df

# labels2csv loads labels and write back as csv file
def labels2csv(path):
    df = loadLabels(path)
    df.to_csv(path + ".csv", index=False)
    pass

# loadLabelsFromCSV loads labels from csv file
def loadLabelsFromCSV(path):
    df = pd.read_csv(path, usecols=['node1', 'node2', 'correct_label', 'work_label'])
    return df