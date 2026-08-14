# coding: utf-8
# Author：fengchi863
# Date ：2023/7/25 9:43

import warnings
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
warnings.filterwarnings("ignore")
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

from Zeus.ProjectSell.v2_0_0.config.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import math
import seaborn as sns

check = pd.read_excel(f'/data/group/800463/sunss/europa/20230805/fsrs/fsrsv3_label_pct_graded_20160101_20190930.xlsx')
print(1)


train_data = pd.read_pickle(data_test_fpath_with_label)
profit_data = pd.read_hdf(profit_data_fpath)
label1 = 'label_pct_graded'
label = 'pct'

fig = plt.figure(figsize=(16, 9))
sns.distplot(train_data[label1], bins=100, kde=True, hist=True, label=label1)
# sns.distplot(train_data[label2], bins=100, kde=True, hist=True, label=label2)
plt.legend()
plt.show()
fig.savefig(junk_path + f'{label1}.png')

fig = plt.figure(figsize=(16, 9))
sns.distplot(profit_data[label], bins=100, kde=True, hist=True, label=label)
# sns.distplot(train_data[label2], bins=100, kde=True, hist=True, label=label2)
plt.legend()
plt.show()
fig.savefig(junk_path + f'{label}.png')

np.corrcoef(train_data[label1], profit_data[label].loc[train_data.index])
profit_data[label].loc[train_data.index].describe()
train_data[label1].describe()
