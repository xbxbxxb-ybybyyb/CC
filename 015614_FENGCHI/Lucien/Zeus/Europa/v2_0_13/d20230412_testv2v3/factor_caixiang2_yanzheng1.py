# coding: utf-8
# Author：fengchi863
# Date ：2023/4/12 13:25

import pandas as pd
from Zeus.Europa.v2_0_13.path_conf import *
from Zeus.Europa.v1_0_32.path_conf import data_test_fpath_with_label as v1032samples_fpath

v2013_samples = pd.read_pickle(data_test_fpath_with_label)  # 没有那四个情绪因子
v1032_samples = pd.read_pickle(v1032samples_fpath)

emotion_factor = ['t1_ulnu_t_ul_rate5', 't1_ulnu_t_ret_mean5', 'EF_time_first_T1_10', 't_emo_ask_amtpct_mean']
add_df = v1032_samples[emotion_factor]
v2013_samples = pd.merge(v2013_samples, add_df, on=['dt', 'Ticker'])
v2013_samples.to_pickle(junk_path + 'factor_df_all_20160101_20220630_add4factors.pkl')

