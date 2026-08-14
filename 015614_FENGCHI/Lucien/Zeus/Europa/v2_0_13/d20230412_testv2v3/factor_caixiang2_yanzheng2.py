# coding: utf-8
# Author：fengchi863
# Date ：2023/4/12 13:25

import pandas as pd
from Zeus.Europa.v2_0_13.path_conf import *
from Zeus.Europa.v1_0_32.path_conf import data_test_fpath_with_label as v1032samples_fpath

v2013_samples = pd.read_pickle(data_test_fpath_with_label)  # 没有那四个情绪因子
v1032_samples = pd.read_pickle(v1032samples_fpath)

drop_emotion = ['wyc_buyPMDay253_mean', 't_emo_ave_pct_adj', 't_emo_ave_pct2open_adj']
emotion_factor = ['wyc_buyPMDay253', 't_emo_ave_pct', 'Jlzt_kcs_mbzs_alt']
add_df = v1032_samples[emotion_factor]
v2013_samples = pd.merge(v2013_samples.drop(drop_emotion, axis=1), add_df, on=['dt', 'Ticker'])
v2013_samples.to_pickle(junk_path + 'factor_df_all_20160101_20220630_replace4factors.pkl')

