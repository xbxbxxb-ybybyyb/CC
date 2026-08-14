# coding: utf-8
# Author：fengchi863
# Date ：2024/4/23 9:10
import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
from dataApi.sendInfo import send_message
from dataApi import tradeDate
import datetime as dt

today_dt = int(dt.datetime.today().strftime('%Y%m%d'))

manual_black_fpath = '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx'

manual_black = pd.read_excel(manual_black_fpath, index_col=0)
start_time = '2024-01-01'
manual_black['入池时间'] = manual_black['入池时间'].apply(lambda x: x.replace('/', '-'))
manual_black['出池时间'] = manual_black['出池时间'].apply(lambda x: str(x))
manual_black = manual_black.query(f'出池时间 == "nan" & 入池时间 >= "{start_time}"')

manual_black['gap_days'] = manual_black['入池时间'].apply(lambda x: tradeDate.get_trade_date_interval(today_dt, int(x.replace('-', ''))))
manual_black = manual_black.reset_index().drop_duplicates('证券名称', keep='last').set_index('证券名称')
should_out = manual_black.query('gap_days >= 10')

message = '麻烦刘老师确认下以下标的是否已经出池：\n'

if len(should_out) > 0:
    out_dict = should_out['gap_days'].to_dict()
    for stk_name in out_dict.keys():
        message += f'{stk_name}(已入池{out_dict[stk_name]}个交易日)\n'
    send_message(message)