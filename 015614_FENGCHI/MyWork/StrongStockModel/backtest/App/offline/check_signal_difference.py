# @Time : 2021/1/17 17:48
# @Author : Zhichen Lu
# @File : check_signal_difference.py
import pandas as pd
import numpy as np
from online_conf import code_list_path

tag = 'OutSample_XGB_Light_OnlineTest'


def get_intersec(date, pre_date):
    offline_signal, offline_pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s.pkl' % tag)
    code_list = pd.read_pickle(code_list_path + '%d.pkl' % pre_date)
    code_list = [int(x[:-3]) for x in code_list]
    offline_bar_pred_ret = offline_pred_ret.loc[date, code_list]  # .loc[1000]
    offline_signal = offline_signal[code_list]

    online_output = pd.read_pickle('/data/group/800319/strategy_local_path3/daily_output/%d.pkl' % date)
    signal = pd.DataFrame()
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        online_bar_pred_ret = online_output['pred_ret'][time_point]
        offline_bar_signal = offline_signal.loc[date].loc[time_point]
        offline_bar_signal = offline_bar_signal[offline_bar_signal]
        online_bar_pred_ret.index = [int(x[:-3]) for x in online_bar_pred_ret.index]
        online_bar_pred_ret = online_bar_pred_ret.mean(axis=1)

        online_bar_signal = online_output['signal'][time_point]

        online_bar_signal.index = [int(x[:-3]) for x in online_bar_signal.index]

        online_bar_signal.loc[:] = True
        bar = pd.DataFrame({'online': online_bar_signal, 'offline': offline_bar_signal})
        bar = bar.reset_index()
        bar['time'] = time_point
        bar = bar.set_index(['time', 'index'])
        signal = signal.append(bar.fillna(False))

    isolation_pool = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/隔离池20201010.xls')['证券代码'].astype(int)
    black_name_list = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/黑名单20201010.xls')['证券代码'].astype(int)
    unavailable_pool = set(isolation_pool).union(set(black_name_list))
    offline_unavailabel_stk = set([x[1] for x in signal.index]).intersection(set(unavailable_pool))

    signal = signal.swaplevel(0, 1)
    signal.loc[list(offline_unavailabel_stk)] = np.nan
    signal = signal.dropna() > 0.5
    inter_sec = signal[(signal['online']) & (signal['offline'])]
    signal_info = signal.sum()
    signal_info['intersection'] = inter_sec.shape[0]
    return signal_info


date_list = [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126,
             20210127]
pre_date_list = [20210104] + date_list[:-1]
signal_stat = {}
for date, pre_date in list(zip(date_list, pre_date_list)):
    signal_stat[date] = get_intersec(date, pre_date)
    print(date)

signal_stat = pd.DataFrame(signal_stat).T
signal_stat['online_inter_ratio'] = signal_stat['intersection'] / signal_stat['online']
signal_stat['offline_inter_ratio'] = signal_stat['intersection'] / signal_stat['offline']
signal_stat.columns = ['线上信号数', '线下信号数', '交集', '交集占线上信号比例', '交集占线下信号比例']
signal_stat.to_excel('/data/user/015664/AFuckingTrigger/online_stat/信号重合统计.xlsx')
