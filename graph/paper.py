# -*- coding: utf-8 -*-

from load_data import loadDataFromCSV
from draw import drawOnePlane

paper_df = loadDataFromCSV("./../dataset/paper_pair.csv", threshold_under = 1.0, threshold_upper = 1.0)
drawOnePlane(paper_df, "paper-1.0")
