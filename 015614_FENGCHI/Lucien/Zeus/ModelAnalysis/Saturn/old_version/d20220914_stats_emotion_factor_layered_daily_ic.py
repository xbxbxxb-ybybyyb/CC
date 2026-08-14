# coding: utf-8
# Author：fengchi863
# Date ：2022/9/14 14:41

from Zeus.Saturn.v3_0_8.DataPrepare import DataPrepare
from dataApi import tradeDate
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from scipy.spatial import distance
from Zeus.Saturn.v3_0_8.path_conf import factor_score_fpath
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

import warnings
warnings.filterwarnings('ignore')

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

samples = pd.concat([X_train, y_train], axis=1)

each_group_num = len(samples) // 10
group_id_list = list()
group_id = 1
for idx in range(len(samples)):
    if idx <= each_group_num * group_id:
        group_id_list.append(group_id)
    else:
        group_id_list.append(group_id)
        group_id += 1

#%% 开始计算分层IC
res_dict = dict()

# 分层IC
corr_list = list()
for fac in X_train.columns.tolist():
    samples_copy = samples.copy()
    samples_copy = samples_copy.sort_values(fac, ascending=False)
    samples_copy['group_id'] = np.array(group_id_list)
    fac_median = samples_copy.groupby('group_id')[fac].agg('median')
    label_median = samples_copy.groupby('group_id')[label].agg('median')
    corr_list.append(pearsonr(fac_median, label_median)[0])

corr_res1 = pd.DataFrame(corr_list, index=emotion_factor_list, columns=['分层IC']).sort_values('分层IC')

"""这里绘制分层IC的图"""
fig = plt.figure(figsize=(36, 12))
axes = fig.subplots(3, 6)
row = 0
col = 0
for fac in X_train.columns.tolist():
    samples_copy = samples.copy()
    samples_copy = samples_copy.sort_values(fac, ascending=False)
    samples_copy['group_id'] = np.array(group_id_list)
    fac_median = samples_copy.groupby('group_id')[fac].agg('median')
    label_median = samples_copy.groupby('group_id')[label].agg('median')

    if col > 5:
        row += 1
        col = 0
    axes[row, col].bar(label_median.index.tolist(), label_median.tolist())
    axes[row, col].set_title(fac)
    col += 1
from Zeus.Saturn.v3_0_8.path_conf import junk_path
fig.savefig(junk_path + '分层IC.png', bbox_inches='tight', pad_inches=0.1)
from dataApi.sendInfo import send_file
send_file(junk_path + '分层IC.png')

# 分层rankIC
corr_list = list()
for fac in X_train.columns.tolist():
    samples_copy = samples.copy()
    samples_copy = samples_copy.sort_values(fac, ascending=False)
    samples_copy['group_id'] = np.array(group_id_list)
    fac_median = samples_copy.groupby('group_id')[fac].agg('median')
    label_median = samples_copy.groupby('group_id')[label].agg('median')
    corr_list.append(spearmanr(fac_median, label_median)[0])

corr_res2 = pd.DataFrame(corr_list, index=emotion_factor_list, columns=['分层rankIC']).sort_values('分层rankIC')

# 分层欧氏距离
corr_list = list()
for fac in X_train.columns.tolist():
    samples_copy = samples.copy()
    samples_copy = samples_copy.sort_values(fac, ascending=False)
    samples_copy['group_id'] = np.array(group_id_list)
    fac_median = samples_copy.groupby('group_id')[fac].agg('median')
    label_median = samples_copy.groupby('group_id')[label].agg('median')
    corr_list.append(distance.euclidean(fac_median.rank(), label_median.rank(ascending=False)))

corr_res3 = pd.DataFrame(corr_list, index=emotion_factor_list, columns=['分层欧氏距离'])
corr_res = pd.concat([corr_res1, corr_res2, corr_res3], axis=1)
res_dict['分层IC'] = corr_res

# spearmanr(corr_res['分层IC'].rank(), corr_res['分层欧氏距离'].rank())[0]  # 测试两个相关性计算的相关性 0.83 不为1，说明也不是完全正相关


#%% 开始计算滚动IC
rolling_len = 20
rolling_window = 60

# 滚动IC
start_idx = 0
corr_res = list()
while start_idx <= len(samples):
    end_idx = start_idx + rolling_window
    if end_idx >= len(samples):
        end_idx = len(samples)
    samples_copy = samples.iloc[start_idx:end_idx]
    start_date = samples_copy.index[0]
    end_date = samples_copy.index[-1]

    each_group_num = len(samples_copy) // 5
    group_id_list = list()
    group_id = 1
    for idx in range(len(samples_copy)):
        if idx <= each_group_num * group_id:
            group_id_list.append(group_id)
        else:
            group_id_list.append(group_id)
            group_id += 1

    corr_list = list()
    for fac in emotion_factor_list:
        samples_copy2 = samples_copy.copy()
        samples_copy2 = samples_copy2.sort_values(fac, ascending=False)
        samples_copy2['group_id'] = np.array(group_id_list)
        fac_median = samples_copy2.groupby('group_id')[fac].agg('median')
        label_median = samples_copy2.groupby('group_id')[label].agg('median')
        corr_list.append(pearsonr(fac_median, label_median)[0])

    tmp_res = pd.DataFrame(corr_list, index=emotion_factor_list, columns=[f'{start_date}-{end_date}'])
    corr_res.append(tmp_res)

    start_idx += rolling_len

corr_res = pd.concat(corr_res, axis=1)
corr_res = corr_res.T
corr_res.loc['小于0的比例', :] = corr_res.apply(lambda x: (x < 0).sum() / len(x))
# corr_res.loc['std', :] = corr_res.apply(lambda x: x.std())
corr_res = corr_res.T

res_dict['滚动分层IC'] = corr_res

# 滚动分层rankIC
start_idx = 0
corr_res = list()
while start_idx <= len(samples):
    end_idx = start_idx + rolling_window
    if end_idx >= len(samples):
        end_idx = len(samples)
    samples_copy = samples.iloc[start_idx:end_idx]
    start_date = samples_copy.index[0]
    end_date = samples_copy.index[-1]

    each_group_num = len(samples_copy) // 5
    group_id_list = list()
    group_id = 1
    for idx in range(len(samples_copy)):
        if idx <= each_group_num * group_id:
            group_id_list.append(group_id)
        else:
            group_id_list.append(group_id)
            group_id += 1

    corr_list = list()
    for fac in emotion_factor_list:
        samples_copy2 = samples_copy.copy()
        samples_copy2 = samples_copy2.sort_values(fac, ascending=False)
        samples_copy2['group_id'] = np.array(group_id_list)
        fac_median = samples_copy2.groupby('group_id')[fac].agg('median')
        label_median = samples_copy2.groupby('group_id')[label].agg('median')
        corr_list.append(spearmanr(fac_median, label_median)[0])

    tmp_res = pd.DataFrame(corr_list, index=emotion_factor_list, columns=[f'{start_date}-{end_date}'])
    corr_res.append(tmp_res)

    start_idx += rolling_len

corr_res = pd.concat(corr_res, axis=1)
corr_res = corr_res.T
corr_res.loc['小于0的比例', :] = corr_res.apply(lambda x: (x < 0).sum() / len(x))
# corr_res.loc['std', :] = corr_res.apply(lambda x: x.std())
corr_res = corr_res.T

res_dict['滚动分层rankIC'] = corr_res

# 滚动分层欧氏距离
start_idx = 0
corr_res = list()
while start_idx <= len(samples):
    end_idx = start_idx + rolling_window
    if end_idx >= len(samples):
        end_idx = len(samples)
    samples_copy = samples.iloc[start_idx:end_idx]
    start_date = samples_copy.index[0]
    end_date = samples_copy.index[-1]

    each_group_num = len(samples_copy) // 5
    group_id_list = list()
    group_id = 1
    for idx in range(len(samples_copy)):
        if idx <= each_group_num * group_id:
            group_id_list.append(group_id)
        else:
            group_id_list.append(group_id)
            group_id += 1

    corr_list = list()
    for fac in emotion_factor_list:
        samples_copy2 = samples_copy.copy()
        samples_copy2 = samples_copy2.sort_values(fac, ascending=False)
        samples_copy2['group_id'] = np.array(group_id_list)
        fac_median = samples_copy2.groupby('group_id')[fac].agg('median')
        label_median = samples_copy2.groupby('group_id')[label].agg('median')
        corr_list.append(distance.euclidean(fac_median.rank(), label_median.rank(ascending=False)))

    tmp_res = pd.DataFrame(corr_list, index=emotion_factor_list, columns=[f'{start_date}-{end_date}'])
    corr_res.append(tmp_res)

    start_idx += rolling_len

corr_res = pd.concat(corr_res, axis=1)
corr_res = corr_res.T
corr_res.loc['小于0的比例', :] = corr_res.apply(lambda x: (x < 0).sum() / len(x))
# corr_res.loc['std', :] = corr_res.apply(lambda x: x.std())
corr_res = corr_res.T

res_dict['滚动分层欧氏距离'] = corr_res

#%% 输出
from LucienUtil.FileUtil import FileUtil
from dataApi.sendInfo import send_file
FileUtil.save_dict2xls(res_dict, '/data/user/015614/junkData/', '市场情绪因子分层IC.xlsx')
send_file('/data/user/015614/junkData/市场情绪因子分层IC.xlsx')
