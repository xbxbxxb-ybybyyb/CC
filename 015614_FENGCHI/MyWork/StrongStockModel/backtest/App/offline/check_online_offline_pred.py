# @Time : 2021/1/13 16:06
# @Author : Zhichen Lu
# @File : check_online_offline_pred.py

from online_conf import daily_out_path, model_config_path
import pandas as pd
import numpy as np
import gc
import os

date = 20201026
online_output = pd.read_pickle(daily_out_path + '%d.pkl' % date)
online_pred_ret = online_output['pred_ret']
_, threshold = pd.read_pickle(model_config_path + 'model_conf20201020.pkl')

online = pd.DataFrame()
for time_point in online_pred_ret:
    bar_pred_ret = online_pred_ret[time_point].reset_index()
    bar_pred_ret['time'] = int(time_point)
    ind_name = bar_pred_ret.columns[0]
    bar_pred_ret[ind_name] = bar_pred_ret[ind_name].apply(lambda x: int(x[:-3]))
    bar_pred_ret = bar_pred_ret.set_index(['time', ind_name])
    online = online.append(bar_pred_ret)

pred_ret_map = {
    'XGB_T': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
    'XGB_D': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
    'XGB_C': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
}

offline = []
for each in pred_ret_map:
    temp = pd.read_pickle(pred_ret_map[each])
    temp = temp.loc[date].rename(columns={'prediction': each})
    offline.append(temp[[each]])

offline = pd.concat(offline, axis=1)

offline = offline.reindex(online.index)

corr = pd.Series(index=offline.columns)
relative_error = pd.Series(index=offline.columns)
mae = pd.Series(index=offline.columns)
for each in corr.index:
    corr[each] = online[each].corr(offline[each])
    relative_error[each] = (online[each] / offline[each] - 1).apply(abs).replace(np.inf, np.nan).mean()
    mae[each] = (online[each] - offline[each]).apply(abs).mean()

col_list = ['XGB_T', 'XGB_D', 'XGB_C']

offline.mean(axis=1).corr(online.mean(axis=1))
compare = pd.DataFrame({'online': online.mean(axis=1), 'offline': offline.mean(axis=1)})
online_output.keys()
(compare['online'] - compare['offline']).apply(abs).mean()
signal = compare > threshold

recall = signal[signal['offline']]  # .loc[1000]

precision = signal[signal['online']]  # .loc[1000]
recall['online'].eq(recall['offline']).mean(), precision['online'].eq(precision['offline']).mean()
signal.sum()

acc = signal['online'].eq(signal['offline'])
