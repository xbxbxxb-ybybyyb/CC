# coding: utf-8
# Author：fengchi863
# Date ：2022/11/15 14:21

"""
v1_0_10为测试版本：用于尝试进行滚动标准化的因子
"""

from Zeus.Europa.v1_0_10.path_conf import saturn_data_test_fpath, factor_path, junk_path
from LucienUtil.FileUtil import FileUtil
import pandas as pd
from dataApi.sendInfo import send_file
import numpy as np
import shutil
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

factor = pd.read_pickle(saturn_data_test_fpath)
label_list = factor.filter(regex='label*').columns.tolist()

factor = factor.drop(label_list, axis=1)

# 读取根据重要性选出来的因子
strategy_name = 'Europa'
version = 'v1_0_10'
model_name = 'lgb_reg_model'
output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'
selected_factor_list = FileUtil.read_list(output_path, 'factor_list.pkl')

# 读取被选取的因子
factor = factor[selected_factor_list]

# 分析因子在train区间和valid区间上的分布情况
date_config = dict(
    train_start_date=20160104,
    train_end_date=20200331,
    valid_start_date=20200401,
    valid_end_date=20200930,
    test_start_date=20201001,
    test_end_date=20210630
)
factor['trade_date'] = factor.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

period_list = ['mean_train', 'mean_valid', 'mean_test',
               'std_train', 'std_valid', 'std_test',
               'skew_train', 'skew_valid', 'skew_test',
               'kurt_train', 'kurt_valid', 'kurt_test']
stats_df = pd.DataFrame(index=selected_factor_list, columns=period_list)
for period in ['train', 'valid', 'test']:
    start_date = date_config[f'{period}_start_date']
    end_date = date_config[f'{period}_end_date']
    factor_copy = factor.query('trade_date >= @start_date & trade_date <= @end_date')
    factor_copy = factor_copy.drop(['trade_date'], axis=1)
    factor_std = factor_copy.std()
    factor_mean = factor_copy.mean()
    factor_skew = factor_copy.skew()
    factor_kurt = factor_copy.kurt()
    stats_df[f'mean_{period}'] = factor_mean.values
    stats_df[f'std_{period}'] = factor_std.values
    stats_df[f'skew_{period}'] = factor_skew.values
    stats_df[f'kurt_{period}'] = factor_kurt.values

mean_diff_abs = abs(stats_df['mean_train'] - stats_df['mean_test']) + \
                abs(stats_df['mean_test'] - stats_df['mean_valid']) + \
                abs(stats_df['mean_valid'] - stats_df['mean_test'])
std_diff_abs = abs(stats_df['std_train'] - stats_df['std_test']) + \
                abs(stats_df['std_test'] - stats_df['std_valid']) + \
                abs(stats_df['std_valid'] - stats_df['std_test'])
skew_diff_abs = abs(stats_df['skew_train'] - stats_df['skew_test']) + \
                abs(stats_df['skew_test'] - stats_df['skew_valid']) + \
                abs(stats_df['skew_valid'] - stats_df['skew_test'])
kurt_diff_abs = abs(stats_df['kurt_train'] - stats_df['kurt_test']) + \
                abs(stats_df['kurt_test'] - stats_df['kurt_valid']) + \
                abs(stats_df['kurt_valid'] - stats_df['kurt_test'])
stats_df['mean_diff_abs'] = mean_diff_abs.values / (stats_df['mean_train'] + stats_df['mean_valid'] + stats_df['mean_test'])
stats_df['std_diff_abs'] = std_diff_abs.values / (stats_df['std_train'] + stats_df['std_valid'] + stats_df['std_test'])
stats_df['skew_diff_abs'] = skew_diff_abs.values / (stats_df['skew_train'] + stats_df['skew_valid'] + stats_df['skew_test'])
stats_df['kurt_diff_abs'] = kurt_diff_abs.values / (stats_df['kurt_train'] + stats_df['kurt_valid'] + stats_df['kurt_test'])
# 按照mean_diff_abs排序
stats_df = stats_df.sort_values(['mean_diff_abs'], ascending=False)
# send_file(stats_df)

#%% 开始绘图
output_path = junk_path + f'{version}_因子分布统计/'
plot_output_path = output_path + '绘图/'
if os.path.exists(plot_output_path):
    shutil.rmtree(plot_output_path)

os.makedirs(output_path, exist_ok=True)
os.makedirs(plot_output_path, exist_ok=True)
color_dict = {'train': 'r',
              'valid': 'b',
              'test': 'y'}
period_num_dict = {'train': 0,
                  'valid': 1,
                  'test': 2}

sorted_diff_factor_list = stats_df.index.tolist()
for indicator in sorted_diff_factor_list[:30]:
    fig, axes = plt.subplots(1, 3, figsize=(24, 6))  # 第一个参数表示有几行
    for period in ['train', 'valid', 'test']:
        start_date = date_config[f'{period}_start_date']
        end_date = date_config[f'{period}_end_date']
        factor_copy = factor.query('trade_date >= @start_date & trade_date <= @end_date')

        factor_copy = factor_copy.drop(['trade_date'], axis=1)

        ax0 = sns.distplot(factor_copy[indicator].dropna(),
                           bins=100,
                           kde=True,
                           hist=True,
                           ax=axes[0],
                           label=period)
    factor_copy = factor.query(f'trade_date >= {date_config["train_start_date"]} & trade_date <= {date_config["test_end_date"]}')
    factor_daily_mad_copy = factor_copy.groupby('trade_date').apply(lambda x: x.median())
    factor_daily_mad_copy.index = factor_daily_mad_copy.index.astype(str)
    ax1 = factor_daily_mad_copy[[indicator]].plot(title=indicator, ax=axes[1])
    fig.savefig(plot_output_path + f'{indicator}.png', bbox_inches='tight', pad_inches=0.1)
    print(f'{indicator}已保存')



