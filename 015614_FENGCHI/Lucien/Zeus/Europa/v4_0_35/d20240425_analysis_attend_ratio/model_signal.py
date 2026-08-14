# coding: utf-8
# Author：fengchi863
# Date ：2024/4/25 10:46

"""
使用Europa的信号，进行滚动测试
"""

from dataApi import tradeDate
import pandas as pd
import numpy as np
from Zeus.Europa.v4_0_35.d20240425_analysis_attend_ratio.SimBack import SimBack

def process_df(fit_df):
    fit_df['prediction'] = fit_df.iloc[:, 0].astype(bool)
    fit_df['pred_Reg'] = fit_df.iloc[:, 1]
    fit_df['stockID'] = fit_df.index.get_level_values(1).tolist()
    fit_df['datelist'] = fit_df.index.get_level_values(0).map(lambda x: int(x[:4] + x[5:7] + x[8:]))
    fit_df['Indexs'] = fit_df['stockID'].astype(str) + ' ' + (fit_df['datelist'].astype(int)).astype(str)
    fit_df = fit_df.set_index(['Indexs'])
    fit_df = fit_df[['prediction', 'pred_Reg', 'stockID', 'datelist']]
    return fit_df

def get_tscv(date_list=None, ref_size=10, set_size=10, min_ref_size=10):
    rolling_cv_date_list = list()
    train_start_idx = 0
    train_end_idx = min_ref_size - 1
    valid_start_idx = train_end_idx + 1
    valid_end_idx = train_end_idx + set_size
    while valid_end_idx < len(date_list):
        tmp_cv = list(map(lambda x: date_list[x], [train_start_idx, train_end_idx, valid_start_idx, valid_end_idx]))
        rolling_cv_date_list.append(tmp_cv)
        train_end_idx += set_size
        valid_start_idx = train_end_idx + 1
        valid_end_idx = train_end_idx + set_size
        train_start_idx = valid_end_idx - ref_size
    if rolling_cv_date_list[-1][-1] > date_list[-1]:
        valid_end_idx = len(date_list) - 1
        valid_start_idx = len(date_list) - set_size
        train_end_idx = valid_start_idx - 1
        train_start_idx = valid_start_idx - ref_size
        tmp_cv = list(map(lambda x: date_list[x], [train_start_idx, train_end_idx, valid_start_idx, valid_end_idx]))
        rolling_cv_date_list.append(tmp_cv)
    return rolling_cv_date_list


date_list = tradeDate.get_date_range(20230421, 20240424)
root_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v3/'
signal_list = list()
for dat in date_list:
    tmp_signal = pd.read_csv(root_path + f'{dat}/{dat}_{dat}_europa_fac_20230329_daily_pred.csv')
    signal_list.append(tmp_signal)

signal_df = pd.concat(signal_list, axis=0)
signal_df = signal_df.set_index(['dt', 'Ticker'])

my_signal = signal_df[['totalRegFSV8XgbFcModel', 'totalRegFSV8XgbFc_proba1']]
threshold = -4.8e-05

attend_ratio_df = pd.DataFrame(index=date_list)

#%% 开始回测
"""第一种：原始信号"""
fit_df = my_signal.copy()
fit_df = process_df(fit_df)
sb = SimBack(fit_df)
stats_df, model_fit_mingan = sb.single_backtest()
stats_df['平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
stats_df['平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
attend_ratio_df['原始模型'] = (fit_df.groupby('datelist')['prediction'].sum() / fit_df.groupby('datelist')['prediction'].count()).reindex(index=date_list)

stats_df_all = pd.DataFrame(index=stats_df.index)
stats_df_all['原始模型'] = stats_df.values

#%% 第二项
"""第二种：进行滚动的信号"""
fit_df = sb._concat_label_profit(fit_df)
param_list = [(10, 1, 0.008), (5, 1, 0.008), (3, 1, 0.008), (1, 1, 0.008)]
for param in param_list:
    ref_days = param[0]
    set_days = param[1]
    pct_threshold = param[2]
    tscv_days = get_tscv(date_list, ref_days, set_days, min_ref_size=ref_days)
    cur_fit_df = fit_df.copy()
    new_cur_fit_df = fit_df.copy()
    for epoch in tscv_days:
        ref_start, ref_end, set_start, set_end = epoch[0], epoch[1], epoch[2], epoch[3]
        ref_tmp = cur_fit_df.query(f'{ref_start} <= datelist <= {ref_end}')
        label_quantile_ratio = (ref_tmp['label_pct'] > pct_threshold).sum() / len(ref_tmp)
        adapt_threshold = np.quantile(ref_tmp['pred_Reg'], 1 - label_quantile_ratio)

        set_tmp = cur_fit_df.query(f'{set_start} <= datelist <= {set_end}')
        new_cur_fit_df.loc[set_tmp.index, 'prediction'] = new_cur_fit_df.loc[set_tmp.index, 'pred_Reg'] > adapt_threshold

    sb = SimBack(new_cur_fit_df)
    stats_df, model_fit_mingan = sb.single_backtest()
    stats_df['平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
    stats_df['平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
    attend_ratio_df[tuple(param)] = (new_cur_fit_df.groupby('datelist')['prediction'].sum() / new_cur_fit_df.groupby('datelist')['prediction'].count()).reindex(index=date_list)
    stats_df_all[tuple(param)] = stats_df.values

save_dict = {
    '回测结果': stats_df_all,
    '参与率对比': attend_ratio_df
}

from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(save_dict, '/data/user/015614/junkData/', '自适应参与率统计结果.xlsx')