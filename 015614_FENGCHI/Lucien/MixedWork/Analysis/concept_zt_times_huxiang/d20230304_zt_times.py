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

check_num = check.copy()
check_pct = (check / np.array([check[i][i] for i in range(len(check))])).T

for idx in range(len(check_num)):
    check_num[idx, idx] = np.nan
    check_pct[idx, idx] = np.nan

check_num_ = (check_num >= 5).sum(axis=1)
res_s = pd.Series(index=up714_flag.columns)

check_num = pd.DataFrame(check_num, index=up714_flag.columns, columns=up714_flag.columns)
check_pct = pd.DataFrame(check_pct, index=up714_flag.columns, columns=up714_flag.columns)
check_num_ = pd.Series(check_num_, index=up714_flag.columns)

for stk_id in tqdm(check_num_.index):
    if check_num_[stk_id] >= 20:
        # 进入2
        check_pct_up5 = check_pct.loc[stk_id]
        check_pct_num = (check_pct.loc[stk_id] >= 0.5).sum()
        if check_pct_num >= 20:
            # 进入3
            tmp_res = check_pct_up5.sort_values(ascending=False).index.tolist()[:20]
        else:
            tmp_res = check_pct_up5.sort_values(ascending=False).index.tolist()[:min(20, len(check_pct_up5[check_pct_up5 > 0]))]
    else:
        tmp_res = check_num.loc[stk_id].sort_values(ascending=False).index.tolist()[:min(20, len(check_num.loc[stk_id][check_num.loc[stk_id] > 0]))]

    res_s[stk_id] = ', '.join(map(str, tmp_res)) if len(tmp_res) > 0 else ''


# res_s.to_excel('/data/user/015614/junkData/20220301-20230228个股按规则筛选前20个.xlsx')
res_df = pd.DataFrame(res_s)
res_df.index.names = ['股票代码']
res_df.columns = ['关联个股列表']
res_df.to_excel('/data/user/015614/shared/for_wys/20220301-20230228个股按规则筛选前20个.xlsx')