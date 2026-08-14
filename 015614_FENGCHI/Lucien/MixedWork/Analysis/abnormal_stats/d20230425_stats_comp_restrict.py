# coding: utf-8
# Author：fengchi863
# Date ：2023/4/25 8:34
"""
近5日解禁限售股数量
"""
from dataApi import tradeDate, sendInfo

from MixedWork.GreyStockGenerator import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
fd = FactorData()
import datetime as dt
from tqdm import tqdm

# 策略样本 Europa
basic_fpath = '/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5'
label_fpath = '/data/group/800463/project/project1_prod/left_v2212/Label_zt_test/Label_zt_001.h5'
all_df = pd.read_hdf(basic_fpath)
all_df['T_o2pre'] = pd.read_hdf(label_fpath)['T_o2pre']
filter_df = all_df[(all_df['ZT_Time'] <= 143000000) &
                   (all_df['open_is_zt'] == 0) &
                   (all_df['T_o2pre'] >= -0.05) &
                   (all_df['after_not_ul_len'] > 10) &
                   (all_df['pre_close'] >= 2) &
                   (all_df['high_price'] < (all_df['trigger_price'])) &
                   (all_df['last_is_zt'] == 0)]

f_data = IO.read_data([fd.tradingday('20230424', -1000)[0], '20230424'],
                          alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCompRestricted/AShareCompRestricted.h5')

date_list = tradeDate.get_date_range(20220101, 20230419)
date_list = list(map(str, date_list))
stats_df = pd.DataFrame(index=date_list)

for nowdate in tqdm(date_list):
    # nowdate = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    nextdate = fd.tradingday(nowdate, 2)[1]

    last_trading_days = fd.tradingday(nowdate, -4)
    last_trading_days.extend([fd.tradingday(nowdate, 2)[1]])
    last_trading_days = list(map(int, last_trading_days))

    f_data2 = f_data.query(f'S_INFO_LISTDATE in {last_trading_days}')
    comp_restrict_list = f_data2.index.get_level_values(1).unique().tolist()
    comp_restrict_list = list(filter(lambda x: x[:2] in ['60', '30', '00'], comp_restrict_list))

    stats_df.loc[nowdate, '近5日解禁限售股数量'] = len(comp_restrict_list)

    # 计算样本数量
    today_strategy_list = filter_df.loc[pd.to_datetime(nowdate)].index.tolist()
    stats_df.loc[nowdate, '当日策略样本数量'] = len(today_strategy_list)
    stats_df.loc[nowdate, '二者交集'] = len(set(today_strategy_list).intersection(set(comp_restrict_list)))
    stats_df.loc[nowdate, '占策略样本比例'] = len(set(today_strategy_list).intersection(set(comp_restrict_list))) / len(today_strategy_list)

sendInfo.send_file(stats_df)