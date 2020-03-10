# -*- coding: utf-8 -*-

import pandas as pd
from load_data import loadResultFile

# confusion matrix calculate the coefficient.
# True Positive(TP)：number of predicting positive class as positive class
# True Negative(TN)：number of predicting negative class as negative class
# False Positive(FP)：number of predicting negative class as positive class (Type I error)
# False Negative(FN)：number of predicting positive class as negative class (Type II error)
def confusionMatrix(df):
    # tp,tn,fp,fn = 0,0,0,0
    tp = len(df.loc[(df['correct_label'] == int(1)) & (df['answer'] == int(1))])
    tn = len(df.loc[(df['correct_label'] == int(0)) & (df['answer'] == int(0))])
    fp = len(df.loc[(df['correct_label'] == int(0)) & (df['answer'] == int(1))])
    fn = len(df.loc[(df['correct_label'] == int(1)) & (df['answer'] == int(0))])
    return tp,tn,fp,fn

# getPrecision caculates precision.
# P = TP / (TP + FP)
def getPrecision(tp, tn, fp, fn):
    p = tp / (tp + fp)
    return p

# getRecall caculates recall.
# R = TP / (TP + FN) = TP / P
def getRecall(tp, tn, fp, fn):
    r = tp / (tp + fn)
    return r

# getFMeasure calculates the F-Measure by result file path.
# path represents the result file path.
# F = (pow(a,a) + 1)P * R / (pow(a,a)(P + R))
# P represents precision.
# R represents recall.
def getFMeasure(alpha, path):
    df_res = loadResultFile(path)

    tp, tn, fp, fn = confusionMatrix(df_res)
    p = getPrecision(tp, tn, fp, fn)
    r = getRecall(tp, tn, fp, fn)

    pa = pow(alpha,alpha)
    f = float(pa + 1) * p * r / (float(pa) * (p + r))
    return f


if __name__ == "__main__":
    f1_paper = getFMeasure(1, '../dataset/result/result_paper.csv')
    print(f1_paper)