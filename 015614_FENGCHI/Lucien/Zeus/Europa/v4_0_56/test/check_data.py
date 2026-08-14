# coding: utf-8
# Author：fengchi863
# Date ：2023/7/14 13:24

"""
半小时的因子数据和因子列表、因子筛选文件。其中因子数据中包含s_xx列，分别为1000、1030、1100三个时点；label_diff_pct为当前时点开始快速卖出的收益率-剩余时间均匀卖出的收益率-0.1%
这是半小时的模拟收益文件，其中buy_vol,buy_amt为前日europa模拟买入量、买入额；pct_v2为v2卖出模拟收益率-0.2%;pct_v1为时点s_xx后快速卖出的模拟收益率-0.3%；pct_diff=pct_v1-pct_v2。需要注意收益率均已扣费。
"""

from Zeus.Europa.v4_0_56.path_conf import *
import pandas as pd
import numpy as np

train_data_check = pd.read_pickle(data_fpath)
train_data_check.shape
profit_data_check = pd.read_pickle(profit_data_fpath)
print(1)