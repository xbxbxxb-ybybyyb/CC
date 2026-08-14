# coding: utf-8
# Author：fengchi863
# Date ：2023/7/25 9:43

import warnings
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
warnings.filterwarnings("ignore")
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

from Zeus.Neptune.v1_0_6.config.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import math
import seaborn as sns

junk_path = '/data/user/015614/junkData/'
train_data = pd.read_pickle('/data/group/800463/sunss/neptune/20250416/factor_df_hs1_20160101_20230630.pkl')
profit_data = pd.read_hdf('/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5')
label1 = 'label_pct_graded'
label = 'label_v2o10dh1'

"""
 'label_TN_o2ul',
 'label_T_is_zt',
 'label_TN_vwap2ul',
 'label_T_o2ul',
 'label_firstUL_end_Time',
 'label_pattern',
 'label_T1_is_zt',
 """

fig = plt.figure(figsize=(16, 9))
sns.distplot(train_data[label1], bins=100, kde=True, hist=True, label=label1)
# sns.distplot(profit_data[label2], bins=100, kde=True, hist=True, label=label2)
plt.legend()
plt.show()
fig.savefig(junk_path + f'{label1}.png')

fig = plt.figure(figsize=(16, 9))
sns.distplot(train_data[label], bins=100, kde=True, hist=True, label=label)
# sns.distplot(profit_data[label2], bins=100, kde=True, hist=True, label=label2)
plt.legend()
plt.show()
fig.savefig(junk_path + f'{label}.png')

np.corrcoef(train_data[label1], profit_data[label].loc[train_data.index])
profit_data[label].loc[train_data.index].describe()
train_data[label1].describe()
