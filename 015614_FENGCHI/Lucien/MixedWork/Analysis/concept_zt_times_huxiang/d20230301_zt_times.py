# coding: utf-8
# Author：fengchi863
# Date ：2023/3/1 18:37

import numpy as np
import pandas as pd

from LucienUtil import IO
from dataApi import stockList, tradeDate
from dataApi.getData import get_daily_1factor


def cal_ul_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt'] >= pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.1 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.2 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']

def cal_714pct_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt'] >= pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.07 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.14 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']

start_date = 20160101
end_date = 20230228
# stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=0, least_normal_days=10, no_pause=True, least_recover_days=0, start_date=start_date, end_date=end_date)
# stk_pool.to_pickle('/data/user/015614/junkData/stk_pool.pkl')
stk_pool = pd.read_pickle('/data/user/015614/junkData/stk_pool.pkl')
date_list = tradeDate.get_date_range(start_date, end_date)
code_list = stk_pool.columns.tolist()
# limit_max = get_daily_1factor('limit_max', code_list=code_list, date_list=date_list)

md_data = IO.read_data([start_date, end_date], columns=['pre_close'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['price714'] = cal_714pct_price(md_data[['pre_close']])
price714 = md_data.reset_index()[['dt', 'Ticker', 'price714']].pivot('dt', 'Ticker', 'price714')
price714.index = price714.index.map(lambda x: int(x.strftime('%Y%m%d')))
price714.columns = price714.columns.map(lambda x: stockList.trans_windcode2int(x))
price714 = price714.loc[date_list, code_list]

close = get_daily_1factor('close', code_list=code_list, date_list=date_list)
high = get_daily_1factor('high', code_list=code_list, date_list=date_list)
up714_flag = (high >= price714) & stk_pool


# 去除科创板
up714_flag = up714_flag[list(filter(lambda x: x // 10000 != 68, code_list))]
############################
"""
20230302上午新任务:AB两股票之间是否都触发该事件，如果是同时触发，那么则为1，否则为0
"""
date_list_1year = tradeDate.get_date_range(20220301, 20230228)
check = np.zeros((4510, 4510))
from tqdm import tqdm
for _date in tqdm(date_list_1year):
# _date = 20230228
    tmp_check = up714_flag.loc[_date].astype(int).values[:, None] * up714_flag.loc[_date].astype(int).values[:, None].T
    check += tmp_check

check = check / np.array([check[i][i] for i in range(len(check))])
check = pd.DataFrame(check, index=up714_flag.columns, columns=up714_flag.columns)
check.to_excel('/data/user/015614/junkData/20220301-20230228个股关联触发7%次数_比例.xlsx')

_date = 20230228
tmp_check = up714_flag.loc[_date].astype(int).values[:, None] * up714_flag.loc[_date].astype(int).values[:, None].T
tmp_check = pd.DataFrame(tmp_check, index=up714_flag.columns, columns=up714_flag.columns)
tmp_check.to_excel('/data/user/015614/junkData/20230228个股关联触发次数.xlsx')
#############################
"""
(up714_flag.sum(axis=0) > 0).sum() # 4258只个股涨停过, 4430只个股到达过7%、14%以上
len(up714_flag.columns)  # 全市场股票数4510   # 股票数量4510只


daily_up714_time = up714_flag.sum(axis=0)
daily_up714_time = daily_up714_time.sort_values(ascending=False)
daily_up714_time.to_excel('/data/user/015614/junkData/各股票自2016年至昨日盘中涨幅超过7%或14%次数.xlsx')
from dataApi.sendInfo import send_file
send_file(pd.DataFrame(daily_up714_time))
"""