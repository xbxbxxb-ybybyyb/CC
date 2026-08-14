# coding: utf-8
# Author：fengchi863
# Date ：2022/9/8 19:47

"""
统计Saturn新加的18个情绪因子与这些样本的日频标签的均值收益的相关性
"""

from Zeus.Saturn.v3_0_8.DataPrepare import DataPrepare
from dataApi import tradeDate
import pandas as pd
from scipy.stats import pearsonr
from Zeus.Saturn.v3_0_8.path_conf import factor_score_fpath

dp = DataPrepare()
dataset = dp.get_samples()

#%% 定义一些参数
start_date = 20160101
end_date = 20190930
date_list = tradeDate.get_date_range(start_date, end_date)
label = 'label_v2o10d1'

#%% 获取18个情绪因子的列表
factor_score = pd.read_excel(factor_score_fpath, index_col=0)
factor_score = factor_score.query('factor_owner == "emotion"')
emotion_factor_list = factor_score['factor_name'].tolist()

#%% 获取情绪因子的序列
dataset_factor = dataset.copy()[emotion_factor_list]
dataset_factor['trade_date'] = dataset_factor.index.get_level_values(0).map(lambda x: int(x.strftime('%Y%m%d')))
X_train = dataset_factor.query('trade_date >= @start_date & trade_date <= @end_date')
X_train = X_train.groupby('trade_date').first()

#%% 获取样本标签的均值
dataset_label = dataset.copy()[[label]]
dataset_label['trade_date'] = dataset_label.index.get_level_values(0).map(lambda x: int(x.strftime('%Y%m%d')))
y_train = dataset_label.query('trade_date >= @start_date & trade_date <= @end_date')
y_train = y_train.groupby('trade_date').mean()

#%% 开始计算
corr_list = list()
for emotion_factor in emotion_factor_list:
    corr_list.append(pearsonr(X_train[emotion_factor].values, y_train.values[:, 0])[0])

res = pd.DataFrame(corr_list, index=emotion_factor_list, columns=['相关性'])
res.index.name = '情绪因子列表'
from dataApi.sendInfo import send_file
send_file(res)

