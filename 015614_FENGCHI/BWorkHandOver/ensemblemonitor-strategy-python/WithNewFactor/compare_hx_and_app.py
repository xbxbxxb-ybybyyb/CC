# @Time : 2021/9/6 9:46
# @Author : Zhichen Lu
# @File : compare_hx_and_app.py

import pandas as pd
import numpy as np

# hx_path = '/data/group/800442/800319/strategy_HFfactor/check/online_hx_20210803_1000.pkl'
hx_path = '/data/group/800442/800319/strategy_HFfactor4/check/online_hx_20210803_1000.pkl'
app_path = f'/data/group/800319/strategy_local_path3_ForMix20210803_rea/daily_output/20210803/5min_factor_1000.pkl'

hx_factor = pd.read_pickle(hx_path)
app_factor = pd.read_pickle(app_path).loc[hx_factor.index]

different = pd.DataFrame(~np.isclose(hx_factor,app_factor),index=hx_factor.index,columns=hx_factor.columns)
different.sum().sum()

check = app_factor[different]

hx_factor.values[different.values]
app_factor.values[different.values]