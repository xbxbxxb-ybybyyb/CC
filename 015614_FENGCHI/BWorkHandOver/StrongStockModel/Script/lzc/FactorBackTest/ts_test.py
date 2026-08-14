# @Time : 2020/9/25 9:57
# @Author : Zhichen Lu
# @File : ts_test.py

from dataApi.TimeSeriesFactorTest import TimeSeriesFactorTest
from dataApi.getData import get_minute_1factor
import pandas as pd
import numpy as np
import os


def get_signal_by_val_pct_threshold(pct, subset_path, signal_file_name):
    """
    在验证集上计算pct处于多少分位数，然后用分位数在预测值上的阈值作为分类阈值
    :param pct:
    :param subset_path:
    :param signal_file_name:
    :return:
    """
    point_list = os.listdir(subset_path)
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    for date in point_list:
        subset = pd.read_pickle(subset_path + '%d.pkl' % date)
        th = (subset[0] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
    threshold_series = threshold_series.reset_index()
    signal = pd.read_pickle(signal_file_name)
    # signal['prediction'] = ((signal['prediction'] > th) * 1).replace(0, -1)
    signal = signal.reset_index()
    signal = signal.pivot_table(index=['level_0', 'level_2'], columns='level_1', values='prediction')  # .replace(-1, 0).fillna(0).sort_index()

    signal['date'] = [x[0] for x in signal.index]
    signal['time'] = [x[1] for x in signal.index]
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list))))
    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])

    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = (signal > 0).replace(False, -1) * 1
    return signal


start_date = 20160101
end_date = 20181231
freq = 7
ft = TimeSeriesFactorTest(start_date, end_date, freq)
ft.set_stock_pool()
ft.set_future()
date_num = ft.date_num
code_num = ft.code_num
code_list = ft.code_list

###load_signal
pct_threshold = 0.05
train_period = 200
test_period = 10
factor_num = 400
cost = 0.001
N = 40
#    signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/lr_train%d_test%d_factor_num%d_norm_window_%d.pkl' % \
#                  (train_period, test_period, factor_num, N)
# yearly
signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/NN_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
train_period, test_period, factor_num, N)

# signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg/XGB_extra_v2_train%d_test%d.pkl' % (train_period, test_period)
subpath = signal_file.replace('.pkl', '_val_pred/')

df = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl', '_val_pred/'), signal_file)

# df = pd.read_pickle('/data/user/015664/AFuckingTrigger/XGB_40_signal.pkl')
import itertools

index_list = pd.MultiIndex.from_tuples(list(itertools.product(ft.date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))

#
# 用框架回测结果
factor = df.reindex(index_list).reindex(code_list, axis=1).replace(-1, 0).fillna(0).values.reshape(date_num, 7, code_num)
result = ft.test_factor(factor, standardize_days=0, top_tile=0, chunks=48)
result = ft.result
result['t_c_d_ret'].mean()
# 回测报告详见说明文档

# 单独计算
close_badj = get_minute_1factor('close_badj', df.index[0][0], df.index[-1][0], code_list=df.columns.tolist())
deal_price = close_badj.rolling(5).mean().shift(-5)

future_pct = deal_price.shift(-242) / deal_price - 1
future_pct = future_pct.loc[df.index]
future_pct[future_pct == np.inf] = np.nan
future_pct[future_pct == -np.inf] = np.nan
df[~df.eq(1)] = np.nan

trigger = df.mul(future_pct)
daily_stk_mean = trigger.groupby('date').mean()
daily_stk_count = trigger.groupby('date').count()
daily_stk_mean[daily_stk_count.eq(0)] = np.nan
daily_mean = daily_stk_mean.mean(axis=1)

win = (trigger > 0) * 1.
win[trigger.isnull()] = np.nan
np.nanmean(win.values)
# 对比
print(daily_mean.loc[20160101:].mean(), result['t_c_d_ret'].mean())
daily_mean.mean(), result['dtc_all_ret'].mean()  # (0.002947954904903449, -0.0006870352107336416)

future_pct.groupby('date').mean().loc[20160101:].mean(axis=1).mean()
