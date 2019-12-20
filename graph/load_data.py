# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def loadDataFromCSV(path, threshold_under = 0.0, threshold_upper = 1.0):
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

    # drop some useless rows here
    df = df.drop(df[df.similarity < threshold_under].index)
    df = df.drop(df[df.similarity > threshold_upper].index)
    return df
