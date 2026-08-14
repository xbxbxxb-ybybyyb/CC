# @Time : 2022/2/9 11:03
# @Author : Zhichen Lu
# @File : signal_frequencey.py

import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file

long_param = {i: f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window_8bar//signal_long_XGB_DTC_Future_{i}_Bar_pct_0.05.pkl' for i in range(1,9)}
short_param = {i:f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/short_8bar//signal_short_XGB_DTC_Future_{i}_Bar_pct_0.pkl' for i in range(1,8)}

short_signal = {}
long_signal = {}
long_actual_label = {}
for i in range(1, 9):
    res = pd.read_pickle(long_param[i])#[:2]
    long_signal[i] = res[0][res[0].fillna(False)]
    long_actual_label[i] = res[-1].stack()
    # if i<8:
    #     temp_signal, temp_pred_ret = pd.read_pickle(short_param[i])[:2]
    #     short_signal[i] = temp_pred_ret[temp_signal.fillna(False)]



daily_stat_signal = {}
barly_stat_signal = {}

future_mean = {x:long_actual_label[x].groupby(level=1).mean() for x in long_actual_label}
future_std = {x:long_actual_label[x].groupby(level=1).std() for x in long_actual_label}
future_mean = pd.DataFrame(future_mean)
future_std = pd.DataFrame(future_std)

for future in long_signal:
    daily_stat_signal[future] = (long_signal[future].groupby(level=0).count() > 0).sum(axis=1)
    barly_stat_signal[future] = long_signal[future].count(axis=1).groupby(level=1).mean()

daily_stat_signal = pd.DataFrame(daily_stat_signal)
barly_stat_signal = pd.DataFrame(barly_stat_signal)
barly_ratio = barly_stat_signal / barly_stat_signal.sum()


out_file = './信号统计.xlsx'
with pd.ExcelWriter(out_file) as writer:
    barly_stat_signal.to_excel(writer,sheet_name='每个bar平均信号量')
    future_std.to_excel(writer,sheet_name='各个bar未来收益率波动率')
    daily_stat_signal.to_excel(writer,sheet_name='每日触发股票数量')
    writer.close()

from dataApi.sendInfo import send_file

send_file(['015664'],out_file)

# origin_signal = long_signal[7].copy()
# bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
# non_fix_trigger = []
# non_fix_trigger_limit = []
# for idx, time_point in enumerate(bar_list):
#     bar_trigger = long_signal[7 - idx].swaplevel(0, 1).loc[[time_point]].swaplevel(0, 1)
#     non_fix_trigger.append(bar_trigger)
#     if idx < 6:
#         shorting = {}
#         for short_window in range(1, 7 - idx):
#             shorting[short_window] = short_signal[short_window].swaplevel(0, 1).loc[[time_point]].swaplevel(0, 1).notnull()
#         shorting = pd.Panel(shorting)
#         shorting = shorting.sum(axis=0)
#         non_fix_trigger_limit.append(bar_trigger[shorting.eq(0)])
#     else:
#         non_fix_trigger_limit.append(bar_trigger)
#
# non_fix_trigger = pd.concat(non_fix_trigger).sort_index()
# non_fix_trigger_limit = pd.concat(non_fix_trigger_limit).sort_index()
# daily_trigger_stk = pd.DataFrame({
#     '原信号': (origin_signal.groupby(level=0).count() > 0).sum(axis=1),
#     '非固定时点信号': (non_fix_trigger.groupby(level=0).count() > 0).sum(axis=1),
#     '非固定时点中途无看空信号': (non_fix_trigger_limit.groupby(level=0).count() > 0).sum(axis=1),
# })
# out_file = './触发股票量统计.xlsx'
# with pd.ExcelWriter(out_file) as writer:
#     daily_trigger_stk.to_excel(writer, sheet_name='逐日')
#     daily_trigger_stk['year'] = daily_trigger_stk.index.map(lambda x: x // 10000)
#     daily_trigger_stk.groupby('year').mean().to_excel(writer, sheet_name='逐年')
# send_file(['015664'], out_file)