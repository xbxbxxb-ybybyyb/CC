import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import pandas as pd

from HANXU.Timing.StrategyTest import test_factor_np, test_signal_np, date_list, wf1d1000

signal_address = '/data/group/800442/800319/Timing/BackTest/Signal/'
signal_name = 'DiscreteXGB600300gain_mdd_pos_stack'

signal = pd.read_pickle(f'{signal_address}/{signal_name}.pkl')
long_pred = pd.read_pickle(f'{signal_address}/long_pred_{signal_name}.pkl')
short_pred = pd.read_pickle(f'{signal_address}/short_pred_{signal_name}.pkl')

signal = signal.reindex(date_list).fillna(0).values
long_pred = long_pred.reindex(date_list).values
short_pred = short_pred.reindex(date_list).values

long_pred_res, long_pred_ins, long_pred_oos = test_factor_np(
    long_pred, future=wf1d1000, freq='Y', signal_months=12, pct_max=0.3, pct_min=0.3)
short_pred_res, short_pred_ins, short_pred_oos = test_factor_np(
    short_pred, future=wf1d1000, freq='Y', signal_months=12, pct_max=0.3, pct_min=0.3)
signal_res, signal_ins, signal_oos = test_signal_np(signal, future=wf1d1000, freq='Y', signal_months=12)

with pd.ExcelWriter(f'{signal_address}/AT_{signal_name}.xlsx') as w:
    signal_res.to_excel(w, '信号统计')
    long_pred_res.to_excel(w, '多头统计')
    short_pred_res.to_excel(w, '空头统计')
    signal_ins.to_excel(w, '信号样本内净值')
    long_pred_ins.to_excel(w, '多头样本内净值')
    short_pred_ins.to_excel(w, '空头样本内净值')
    signal_oos.to_excel(w, '信号样本外净值')
    long_pred_oos.to_excel(w, '多头样本外净值')
    short_pred_oos.to_excel(w, '空头样本外净值')

from dataApi.sendInfo import send_file
send_file('015614', f'{signal_address}/AT_{signal_name}.xlsx')