# coding: utf-8
# Author：fengchi863
# Date ：2023/2/10 14:19

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

start_date = 20160101
end_date = 20230209
# stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=0, least_normal_days=10, no_pause=True, least_recover_days=0, start_date=20160101, end_date=20230209)
# stk_pool.to_pickle('/data/user/015614/junkData/stk_pool.pkl')
stk_pool = pd.read_pickle('/data/user/015614/junkData/stk_pool.pkl')
date_list = tradeDate.get_date_range(20160101, 20230209)
code_list = stk_pool.columns.tolist()
# limit_max = get_daily_1factor('limit_max', code_list=code_list, date_list=date_list)

md_data = IO.read_data([start_date, end_date], columns=['pre_close'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['limit_max'] = cal_ul_price(md_data[['pre_close']])
limit_max = md_data.reset_index()[['dt', 'Ticker', 'limit_max']].pivot('dt', 'Ticker', 'limit_max')
limit_max.index = limit_max.index.map(lambda x: int(x.strftime('%Y%m%d')))
limit_max.columns = limit_max.columns.map(lambda x: stockList.trans_windcode2int(x))
limit_max = limit_max.loc[date_list, code_list]

close = get_daily_1factor('close', code_list=code_list, date_list=date_list)
zt_flag = (close == limit_max) & stk_pool

# 去除科创板
zt_flag = zt_flag[list(filter(lambda x: x // 10000 != 68, code_list))]

(zt_flag.sum(axis=0) > 0).sum() # 4258只个股涨停过
len(zt_flag.columns)  # 全市场股票数4503

daily_zt_time = zt_flag.sum(axis=0)
daily_zt_time = daily_zt_time.sort_values(ascending=False)
daily_zt_time.to_excel('/data/user/015614/junkData/各股票自2016年至昨日涨停次数.xlsx')
from dataApi.sendInfo import send_file
send_file(pd.DataFrame(daily_zt_time))