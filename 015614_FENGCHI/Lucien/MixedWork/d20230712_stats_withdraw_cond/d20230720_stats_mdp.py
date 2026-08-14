# coding: utf-8
# Author：fengchi863
# Date ：2023/7/20 19:20

import pandas as pd
import numpy as np
import re
import datetime as dt
from dataApi.sendInfo import send_file
from tqdm import tqdm
from xquant.marketdata import MarketData
import os
mdp = MarketData()

tick_path = '/data/user/015614/TEST/及时撤单/tick_data/'
trans_path = '/data/user/015614/TEST/及时撤单/trans_data/'

ORDER_MONEY = 1000000
TIME_INTERVAL = 60  # 秒

def delay_time(dt1, sec):
    ret_dt = dt1 + dt.timedelta(seconds=sec)
    if '1130000' < dt1.strftime('%H%M%S') < '1300000':
        ret_dt = dt1 + dt.timedelta(seconds=90*60) + dt.timedelta(seconds=sec)
    return ret_dt

zb_info_fpath = '/data/user/018107/share_file/for_fc/europa_ul_time_20220518_20230528.pkl'
zb_info = pd.read_pickle(zb_info_fpath)
zb_info = zb_info.dropna(axis=0)

profit_data_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
profit_data = pd.read_hdf(profit_data_fpath)

for idx in tqdm(range(len(zb_info))):
    row = zb_info.iloc[idx]
    index = row.name
    stock_code = index[1]
    buy_date_dt = index[0]
    buy_date_str = index[0].strftime('%Y%m%d')
    # trans_df = mdp.get_data_by_date("Transaction", stock_code, buy_date_str, ["2", "3"])
    if not os.path.exists(tick_path + f'{buy_date_str}_{stock_code}.pkl'):
        tick_df = mdp.get_data_by_date("Stock", stock_code, buy_date_str, ["2", "3"])
        tick_df.to_pickle(tick_path + f'{buy_date_str}_{stock_code}.pkl')
    else:
        tick_df = pd.read_pickle(tick_path + f'{buy_date_str}_{stock_code}.pkl')

    ul_price = tick_df['MaxPx'].max()
    first_ul_time_int = int(row['label_touch_ul_time'])
    first_ul_time_dt = pd.datetime.strptime(buy_date_str + str(first_ul_time_int) + '000', '%Y%m%d%H%M%S%f')
    after_ul_1min = delay_time(first_ul_time_dt, TIME_INTERVAL)
    after_ul_1min_mdtime = int(after_ul_1min.strftime('%H%M%S%f')[:-3])
    first_ul_end_time = tick_df.query(f'MDTime > "{str(after_ul_1min_mdtime)}" & LastPx != {ul_price}')['MDTime'].iloc[0]
    on_board = tick_df.query(f'LastPx == {ul_price} & Sell1OrderQty == 0')
    on_board['Buy1OrderMoney'] = on_board['Buy1Price'] * on_board['Buy1OrderQty']
    check = on_board.sort_values('Buy1OrderMoney')
    # NOTE: 20231017，这个方案还是不够准确，根据是否撤单，不太方便计算，还是需要根据tran_df进行分析

    for i in range(len(check)):
        row2 = check.iloc[i]
        if row2['Buy1OrderMoney'] <= ORDER_MONEY:
            if row2['MDTime'] >= after_ul_1min.strftime('%H%M%S%f')[:-3]:
                zb_info.loc[index, 'is_withdraw'] = 1
                print(buy_date_str, stock_code, row2['Buy1OrderMoney'], row2['MDTime'])
                break
        else:
            zb_info.loc[index, 'is_withdraw'] = 0
            break
zb_info.to_pickle(f'/data/user/015614/TEST/及时撤单/orderMoney{ORDER_MONEY}_timeInterval{TIME_INTERVAL}.pkl')

zb_info = pd.read_pickle(f'/data/user/015614/TEST/及时撤单/orderMoney{ORDER_MONEY}_timeInterval{TIME_INTERVAL}.pkl')

