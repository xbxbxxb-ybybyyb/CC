# @Time : 2021/4/20 10:53
# @Author : Zhichen Lu
# @File : compare_real_and_sim.py
import pandas as pd
from OnlineTool.OnlineStat import get_path_conf

date = 20210420
online_path_conf, sim_path_conf = get_path_conf(), get_path_conf('/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210420/')

online_buy_time_info, sim_buy_time_info = pd.read_pickle(online_path_conf['buy_time_info_path'] + '%d.pkl' % date), pd.read_pickle(
    sim_path_conf['buy_time_info_path'] + '%d.pkl' % date)

compare_buy_time = pd.DataFrame({'实盘': pd.Series(online_buy_time_info), '仿真': pd.Series(sim_buy_time_info)})  # .astype(str)

find_different = compare_buy_time[compare_buy_time['实盘'].isnull() | compare_buy_time['仿真'].isnull()].astype(str)

online_holding, sim_holding = pd.read_pickle(online_path_conf['holding_info_path'] + '%d.pkl' % date), pd.read_pickle(
    sim_path_conf['holding_info_path'] + '%d.pkl' % date)
compare_holding = pd.DataFrame({'实盘': pd.Series(online_holding), '仿真': pd.Series(sim_holding)})#.loc[check.index]
compare_holding = compare_holding[(compare_holding['实盘'] >= 100) | (compare_holding['仿真'] >= 100)]

find_different = compare_holding.loc[find_different.index]

find_different = find_different[find_different.count(axis=1)>0]

online_summary = pd.read_pickle(online_path_conf['daily_out_path'] + '%d.pkl' % date)

sim_summary = pd.read_pickle(sim_path_conf['daily_out_path'] + '%d_fake_for_final.pkl' % date)



'300168.SZ' in online_summary['signal'][1000].index
'300168.SZ' in sim_summary['signal'][1000].index
sim_summary['pred_ret'][1000]  # .loc['300168.SZ']

sim_summary['pred_ret'][1000].shape
online_summary['pred_ret'][1000].shape

missing = {'300168.SZ', '002408.SZ', '002037.SZ', '600340.SH', '603900.SH', '600071.SH', '300467.SZ', '002607.SZ', '300725.SZ', '601515.SH', '002416.SZ', '300674.SZ', '603666.SH', '002314.SZ', '000639.SZ', '601009.SH', '002007.SZ', '603922.SH', '000597.SZ', '000498.SZ', '000893.SZ', '600107.SH', '300037.SZ', '600959.SH', '300404.SZ', '600486.SH', '300124.SZ', '002381.SZ'}

import time,os
def getFileModTime(file):
    return time.strftime('%Y%m%d%H%M%S', time.localtime(os.path.getmtime(file)))
import pandas as pd
date = 20210730
summary_730_730 = pd.read_pickle(f'/data/group/800442/800319/StrategyBackup/strategy_local_path3_backup20210731/daily_output/out_930/{date}.pkl')
summary_730_802 = pd.read_pickle(f'/data/user/015664/StrategyOutput/out_930/{date}.pkl')
holding_730_730 = summary_730_730['barly_holding_info'][1000].set_index('Symbol')
holding_730_802 = summary_730_802['barly_holding_info'][1000].set_index('Symbol')


getFileModTime(f'/data/user/015664/StrategyOutput/out_930/{date}.pkl')