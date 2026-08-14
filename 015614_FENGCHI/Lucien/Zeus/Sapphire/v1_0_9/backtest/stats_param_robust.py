# coding: utf-8
# Author：fengchi863
# Date ：2023/8/30 10:45

import os
import pandas as pd
import numpy as np
from Zeus.Sapphire.v1_0_9.path_conf import *
import math

period = 'period1'
pred_type = 'fit'
date_dict = date_config[period]
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
model_names = os.listdir('/data/user/015614/Zeus/pred/Sapphire/v1_0_9/')
model_names1 = list(sorted(list(filter(lambda x: 'pct_' in x, model_names))))
model_names2 = list(sorted(list(filter(lambda x: 'pctAfter_' in x, model_names))))
model_names = model_names1 + model_names2

min_attend_ratio = 20
max_attend_ratio = 50

def trans_pred_index(_pred_df):
    pred_df = _pred_df.copy()
    pred_df['dt'] = pred_df['datelist'].map(lambda x: pd.to_datetime(str(x)))
    pred_df['Ticker'] = pred_df['stockID']
    pred_df = pred_df.set_index(['dt', 'Ticker'], drop=True)
    return pred_df

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def calc_sharp(_s, ref_col):
    mean_ret = _s.query('buy_amt > 0')[ref_col].mean()
    std_ret = _s.query('buy_amt > 0')[ref_col].std()
    sharp = abs(mean_ret / std_ret) * math.sqrt(250)
    return sharp

def backtest(pred_df):
    from Zeus.Sapphire.v1_0_9.path_conf import profit_data_fpath
    profit_data = pd.read_hdf(profit_data_fpath)
    # profit_data['pct'] = profit_data['pct'] - 0.002
    profit_data['pct'] = profit_data['label_diff_pct']
    pred_df = trans_pred_index(pred_df)
    profit_data = pred_df.join(profit_data)
    profit_data['profit'] = profit_data['buy_amt'] * profit_data['pct']

    """计算当前参与率下各指标，平均收益率、累计收益、最大回撤、收益风险比、收益夏普比率"""
    res_s = pd.Series(index=['样本数量', '收益率均值', '累计收益', '最大回撤', '收益风险比', '收益夏普比率',
                              '平均收益率均值', '平均累计收益', '平均最大回撤', '平均收益风险比', '平均收益夏普比率'])
    profit_data['trade_date'] = profit_data.index.get_level_values(0).map(lambda x: x.strftime('%Y%m%d'))
    daily_profit = pd.DataFrame()
    daily_profit['日收益'] = profit_data.query('prediction == 1').groupby('trade_date')['profit'].sum()
    daily_profit = daily_profit.reindex(index=list(set(profit_data['trade_date'].unique()))).fillna(0).sort_index()
    daily_profit['累计收益'] = daily_profit['日收益'].cumsum()
    mdd = calc_mdd(daily_profit['日收益'])
    res_s['样本数量'] = len(pred_df)
    res_s['收益率均值'] = profit_data.query('prediction == 1')['pct'].mean()
    res_s['累计收益'] = daily_profit['累计收益'].iloc[-1]
    res_s['最大回撤'] = mdd
    res_s['收益风险比'] = -res_s['累计收益'] / res_s['最大回撤']
    res_s['收益夏普比率'] = calc_sharp(profit_data.query('prediction == 1'), 'profit')

    """计算不同参与率下的均值"""
    attend_ratio_list = list(map(lambda x: x / 100, list(range(min_attend_ratio, max_attend_ratio))))

    diff_attend_df = pd.DataFrame()
    for attend_ratio in attend_ratio_list:
        threshold = profit_data['pred_Reg'].quantile(1 - attend_ratio)
        profit_data['prediction'] = profit_data['pred_Reg'] >= threshold
        concat_df = profit_data.query('prediction == 1')

        daily_profit = concat_df.groupby('datelist')['profit'].sum()
        cumsum_profit = daily_profit.cumsum()

        pct_cost = concat_df['pct'].mean()
        mdd = calc_mdd(daily_profit)
        profit_sharp = calc_sharp(concat_df, ref_col='profit')

        diff_attend_df.loc[attend_ratio, '参与率'] = attend_ratio
        diff_attend_df.loc[attend_ratio, '阈值'] = threshold
        diff_attend_df.loc[attend_ratio, '参与个数'] = concat_df.shape[0]
        diff_attend_df.loc[attend_ratio, '累计收益'] = cumsum_profit.iloc[-1]
        diff_attend_df.loc[attend_ratio, '平均收益率'] = pct_cost
        diff_attend_df.loc[attend_ratio, '最大回撤'] = mdd
        diff_attend_df.loc[attend_ratio, '收益风险比'] = cumsum_profit.iloc[-1] / -mdd
        diff_attend_df.loc[attend_ratio, '收益夏普比率'] = profit_sharp

    res_s['平均收益率均值'] = diff_attend_df['平均收益率'].mean()
    res_s['平均累计收益'] = diff_attend_df['累计收益'].mean()
    res_s['平均最大回撤'] = diff_attend_df['最大回撤'].mean()
    res_s['平均收益风险比'] = diff_attend_df['收益风险比'].mean()
    res_s['平均收益夏普比率'] = diff_attend_df['收益夏普比率'].mean()

    return res_s


pred_out_path = pred_out_path + 'Sapphire/v1_0_9/'
summary_df = pd.DataFrame()
for model_name in model_names:
        print(f'{model_name}')
        pred_df = pd.read_csv(pred_out_path + model_name + f'/{out_begin}~{out_end}.csv', index_col=0)
        res_s = backtest(pred_df)
        res_s.name = f'{model_name}'
        summary_df = summary_df.append(res_s)

summary_df['model_name'] = summary_df.index
summary_df2 = summary_df.groupby('model_name').mean()
summary_df2 = summary_df2.loc[model_names]

from dataApi.sendInfo import send_file
# send_file(summary_df)
send_file(summary_df2)