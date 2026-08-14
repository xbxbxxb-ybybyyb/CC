# coding: utf-8
# Author：fengchi863
# Date ：2023/7/25 9:43

import warnings
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
warnings.filterwarnings("ignore")
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

from Zeus.ProjectSell.v1_1_2.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import math
import seaborn as sns


train_data = pd.read_pickle(data_test_fpath_with_label)
profit_data = pd.read_hdf(profit_data_fpath)
label1 = 'label_diff_pct_v1'
label2 = 'label_diff_pct'
label = 'label_diff_pct'

fig = plt.figure(figsize=(16, 9))
sns.distplot(train_data[label1], bins=100, kde=True, hist=True, label=label1)
# sns.distplot(train_data[label2], bins=100, kde=True, hist=True, label=label2)
plt.legend()
plt.show()
fig.savefig(junk_path + f'{label1}.png')

np.corrcoef(train_data[label2], profit_data[label].loc[train_data.index])
profit_data[label].loc[train_data.index].mean()
train_data[label1].mean()
train_data[label2].mean()
