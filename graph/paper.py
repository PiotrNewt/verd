# -*- coding: utf-8 -*-

from load_data import loadData, loadLabels, labels2csv
from draw import drawOnePlane

labels2csv("./../dataset/5w_restaurant_alllabels")
# paper_df = loadData("./../dataset/paper_pair_test.csv", threshold_under = 1.0, threshold_upper = 1.0)
# drawOnePlane(paper_df, "paper-3-5")
