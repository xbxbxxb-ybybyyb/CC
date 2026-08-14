# coding: utf-8
# Author：fengchi863
# Date ：2022/7/7 17:32

import os
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dataApi.sendInfo import send_message, send_file

# saturns策略的所有因子和标签
saturns_path = '/data/group/800463/wangj/For_FC/data/'
file_name = 'saturns1_v5_20160101_20190930.pkl'
samples_file_path = os.path.join(saturns_path, file_name)

root_path = '/data/user/015614/MyData/'
dist_save_path = os.path.join(root_path, 'Saturn数据分析可视化保存/')

train_data = pd.read_pickle(samples_file_path)

# %% 分析标签
train_label = train_data.filter(regex='label')
# 11个label，分析每个label的数据特点
dc_label_list = [
    'label_T_open_is_zt',
    'label_T_open_is_dt',
    'label_T_first_trans_ZT'
]
con_label_list = [
    'label_v2o10',
    'label_v2o10d1',
    'label_v2o10d10',
    'label_o2o10',
    'label_o2o10d1',
    'label_o2o10d10',
]

dc_stats_df = pd.DataFrame(index=dc_label_list)
for dc_label in dc_label_list:
    dc_stats_df.loc[dc_label, '离散个数'] = len(set(train_label[dc_label]))
    dc_stats_df.loc[dc_label, '最大值'] = train_label[dc_label].max()
    dc_stats_df.loc[dc_label, '最小值'] = train_label[dc_label].min()

con_stats_df = pd.DataFrame(index=con_label_list)
for con_label in con_label_list:
    con_stats_df.loc[con_label, '空值个数'] = train_label[con_label].isna().sum()
    con_stats_df.loc[con_label, '总个数'] = train_label.shape[0]
    con_stats_df.loc[con_label, '空值比例'] = train_label[con_label].isna().sum() / len(train_label[con_label])
    con_stats_df.loc[con_label, '不同个数比例'] = len(set(train_label[con_label])) / len(train_label[con_label])
    con_stats_df.loc[con_label, '最大值'] = train_label[con_label].max()
    con_stats_df.loc[con_label, '最小值'] = train_label[con_label].min()
    con_stats_df.loc[con_label, '平均值'] = train_label[con_label].mean()
    con_stats_df.loc[con_label, '中位数'] = train_label[con_label].median()
    con_stats_df.loc[con_label, '75%分位数'] = train_label[con_label].quantile(0.75)
    con_stats_df.loc[con_label, '25%分位数'] = train_label[con_label].quantile(0.25)
    con_stats_df.loc[con_label, '大于等于0的比例'] = len(train_label.query(f'{con_label} >= 0')) / len(train_label[con_label])

# send_file(con_stats_df, filename='标签统计特征')
# 检测这个空的样本是什么
# check = train_data[train_label[con_label].isna()]


# %% 分析因子
factor_list = list(set(train_data.columns.tolist()) - set(train_label.columns.tolist()))
train_factor = train_data[factor_list]
print(len(factor_list))

# 定义归一化的上下容忍度
EPS1 = 1e-3
EPS2 = 1e-2

factor_stats_df = pd.DataFrame(index=factor_list)
for factor in factor_list:
    factor_stats_df.loc[factor, 'set个数'] = len(set(train_factor[factor]))
    factor_stats_df.loc[factor, '空值比例'] = train_factor[factor].isna().sum() / len(train_factor[factor])
    factor_stats_df.loc[factor, '不同个数比例'] = len(set(train_factor[factor])) / len(train_factor[factor])
    factor_stats_df.loc[factor, '最大值'] = train_factor[factor].max()
    factor_stats_df.loc[factor, '最小值'] = train_factor[factor].min()
    factor_stats_df.loc[factor, '平均值'] = train_factor[factor].mean()
    factor_stats_df.loc[factor, '中位数'] = train_factor[factor].median()
    factor_stats_df.loc[factor, '偏度'] = train_factor[factor].skew()

# train_data['saturn_wd_high_ul_250_mean']    # 可能是过去250天以内的涨停次数
# train_data['saturn_cb_num']     # 猜测为触板次数

# 寻找set个数过少的离散因子，定义10个以下为离散因子
dc_factor = factor_stats_df.query('set个数 < 10')
dc2_factor = factor_stats_df.query('set个数 >= 10 & set个数 <= 100').sort_values(['set个数'])
dc3_factor = factor_stats_df.query('set个数 >= 100 & set个数 <= 20000').sort_values(['set个数'])
dc_factor_list = dc_factor.index.tolist()
dc2_factor_list = dc2_factor.index.tolist()
dc3_factor_list = dc3_factor.index.tolist()

# [0, 1]归一化的因子
check1 = factor_stats_df.query(f'(最大值 <= 1 + {EPS1}) & (最大值 >= 1 - {EPS1}) & (最小值 >= -{EPS1}) & (最小值 <= {EPS1})')
common_index = list(set(check1.index).intersection(set(dc_factor_list + dc2_factor_list)))
check1 = check1.drop(common_index)
check2 = factor_stats_df.query(f'(最大值 <= 1 + {EPS2}) & (最大值 >= 1 - {EPS2}) & (最小值 >= -{EPS2}) & (最小值 <= {EPS2})')
common_index = list(set(check2.index).intersection(set(dc_factor_list + dc2_factor_list)))
check2 = check2.drop(common_index)
print(check1.shape, check2.shape)
# send_file(check2)
normed_factor_list01 = check2.index.tolist()

# [-1, 1]归一化的因子
check1 = factor_stats_df.query(
    f'(最大值 <= 1 + {EPS1}) & (最大值 >= 1 - {EPS1}) & (最小值 >= -1 - {EPS1}) & (最小值 <= -1 + {EPS1})')
common_index = list(set(check1.index).intersection(set(dc_factor_list + dc2_factor_list)))
check1 = check1.drop(common_index)
check2 = factor_stats_df.query(
    f'(最大值 <= 1 + {EPS2}) & (最大值 >= 1 - {EPS2}) & (最小值 >= -1 - {EPS2}) & (最小值 <= -1 + {EPS2})')
common_index = list(set(check2.index).intersection(set(dc_factor_list + dc2_factor_list)))
check2 = check2.drop(common_index)
print(check1.shape, check2.shape)
# send_file(check2)
normed_factor_list11 = check2.index.tolist()

# 寻找包含空值的因子，但测试下来空值比例只有万2左右，也25799个样本中只有四五个空值
has_nan_factor_list = factor_stats_df.query('空值比例 > 0').index.tolist()
# 寻找最大值大于1的因子，也就是没有经过归一化的因子
non_standard_factor_list = factor_stats_df.query('最大值 > 1').index.tolist()
factor_stats_df['最大值-最小值'] = factor_stats_df['最大值'] - factor_stats_df['最小值']
check = factor_stats_df.query('最大值 > 1')

# %% 绘图保存每个因子的分布情况
"""
使用seaborn绘制多个子图的其中一个最灵活的方法：配合matplotlib的subplots()方法
"""


def plot_dist(_factor, dir_name=None, skew=None):
    # _factor = 'label_v2o10d1'
    if not os.path.exists(dist_save_path + dir_name + '/'):
        os.makedirs(dist_save_path + dir_name + '/')
    if skew:
        axlabel = _factor + f' {str(round(skew, 2))}'
    else:
        axlabel = _factor
    fig, axes = plt.subplots(1, 3, figsize=(24, 6))
    ax0 = sns.distplot(train_data[_factor].dropna(),
                       bins=100,
                       kde=True,
                       hist=True,
                       ax=axes[0],
                       axlabel=axlabel)
    ax1 = sns.boxplot(train_data[_factor].dropna(),
                      ax=axes[1])
    ax2 = sns.violinplot(train_data[_factor].dropna(),
                         ax=axes[2])
    # tight去白边
    plt.savefig(dist_save_path + dir_name + '/' + _factor, bbox_inches='tight')



# for factor in tqdm(dc_label_list):
#     plot_dist(factor, '离散标签')
# for factor in tqdm(con_label_list):
#     plot_dist(factor, '连续标签')
# for factor in tqdm(dc_factor_list + dc2_factor_list):
#     plot_dist(factor, '离散因子')
# for factor in tqdm(normed_factor_list01):
#     plot_dist(factor, '[0,1]归一化因子')
for factor in tqdm(normed_factor_list11):
    plot_dist(factor, '[-1,1]归一化因子')


factor_stats_df2 = factor_stats_df.copy()
factor_stats_df2 = factor_stats_df2.drop(common_index + normed_factor_list01 + normed_factor_list11)
factor_stats_df2 = factor_stats_df2.sort_values(['中位数'])
for factor in tqdm(factor_stats_df2.index):
    plot_dist(factor, '未归一化因子', factor_stats_df2.loc[factor, '偏度'])
