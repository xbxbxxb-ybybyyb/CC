# coding: utf-8
# Author：fengchi863
# Date ：2023/4/12 10:24

import pandas as pd
from Zeus.Europa.v1_0_32.path_conf import *
from Zeus.Europa.v2_0_13.path_conf import data_test_fpath_with_label as v3_data_test_fpath_with_label

all_samples = pd.read_pickle(data_test_fpath_with_label)
v3_all_samples = pd.read_pickle(v3_data_test_fpath_with_label)

v2duiqi_all_samples = all_samples.loc[v3_all_samples.index]
v2duiqi_all_samples.to_pickle('/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20220630_v2v3duiqi.pkl')