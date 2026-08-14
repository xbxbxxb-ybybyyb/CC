# coding: utf-8
# Author：fengchi863
# Date ：2023/3/6 13:56

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
md_data['limit_max'] = cal_ul_price(md_data[['pre_close']])
price714 = md_data.reset_index()[['dt', 'Ticker', 'price714']].pivot('dt', 'Ticker', 'price714')
limit_max = md_data.reset_index()[['dt', 'Ticker', 'limit_max']].pivot('dt', 'Ticker', 'limit_max')
price714.index = price714.index.map(lambda x: int(x.strftime('%Y%m%d')))
limit_max.index = limit_max.index.map(lambda x: int(x.strftime('%Y%m%d')))
price714.columns = price714.columns.map(lambda x: stockList.trans_windcode2int(x))
limit_max.columns = limit_max.columns.map(lambda x: stockList.trans_windcode2int(x))
price714 = price714.loc[date_list, code_list]
limit_max = limit_max.loc[date_list, code_list]

close = get_daily_1factor('close', code_list=code_list, date_list=date_list)
high = get_daily_1factor('high', code_list=code_list, date_list=date_list)
up714_flag = (high >= price714) & stk_pool
zt_flag = (high == limit_max) & stk_pool

# 去除科创板
up714_flag = up714_flag[list(filter(lambda x: x // 10000 != 68, code_list))]
zt_flag = zt_flag[list(filter(lambda x: x // 10000 != 68, code_list))]
############################
"""
20230306下午新任务:你试下满足两个条件：>=7%发生的次数>=5次，且占比>=50%，这只股票满足这2个条件对应的数量要>=5个，不满足的置为空。数量大于20个的，按照>=7%的次数、占比和zt的次数进行排序，取前20个。
"""
date_list_1year = tradeDate.get_date_range(20220301, 20230228)
check = np.zeros((4510, 4510))
zt_check = np.zeros((4510, 4510))
from tqdm import tqdm
for _date in tqdm(date_list_1year):
# _date = 20230228
    tmp_check1 = up714_flag.loc[_date].astype(int).values[:, None] * up714_flag.loc[_date].astype(int).values[:, None].T
    tmp_check2 = zt_flag.loc[_date].astype(int).values[:, None] * zt_flag.loc[_date].astype(int).values[:, None].T
    check += tmp_check1
    zt_check += tmp_check2

check_num = check.copy()
zt_check_num = zt_check.copy()
check_pct = (check / np.array([check[i][i] for i in range(len(check))])).T

for idx in range(len(check_num)):
    check_num[idx, idx] = np.nan
    check_pct[idx, idx] = np.nan
    zt_check_num[idx, idx] = np.nan

check_double_flag = ((check_num >= 5) & (check_pct >= 0.5))
check_double_flag_num = ((check_num >= 5) & (check_pct >= 0.5)).sum(axis=1)

# mask取只符合这个条件的那一个元素
check_num = np.where(check_double_flag > 0, check_num, np.zeros((4510, 4510)))
check_pct = np.where(check_double_flag > 0, check_pct, np.zeros((4510, 4510)))
zt_check_num = np.where(check_double_flag > 0, zt_check_num, np.zeros((4510, 4510)))

# 转换成带index的
check_num = pd.DataFrame(check_num, index=up714_flag.columns, columns=up714_flag.columns)
zt_check_num = pd.DataFrame(zt_check_num, index=up714_flag.columns, columns=up714_flag.columns)
check_pct = pd.DataFrame(check_pct, index=up714_flag.columns, columns=up714_flag.columns)
check_double_flag_num = pd.Series(check_double_flag_num, index=up714_flag.columns)

check_double_flag_up5_index = (check_double_flag_num[check_double_flag_num >= 5]).index.tolist()

res_s = pd.Series(index=up714_flag.columns)
for stk_id in tqdm(check_double_flag_up5_index):
    df = pd.DataFrame(columns=['num', 'pct', 'zt_num'])
    df['num'] = check_num.loc[stk_id]
    df['pct'] = check_pct.loc[stk_id]
    df['zt_num'] = zt_check_num.loc[stk_id]
    df[df == 0] = np.nan
    tmp_res = df.dropna(how='all', axis=0).sort_values(['num', 'pct', 'zt_num'],ascending=False).index.tolist()[:min(20, len(df.dropna(how='all', axis=0)))]
    res_s[stk_id] = ', '.join(map(str, tmp_res)) if len(tmp_res) > 0 else ''

# test
# stk_id = 585
# df = pd.DataFrame(columns=['num', 'pct', 'zt_num'])
# df['num'] = check_num.loc[stk_id]
# df['pct'] = check_pct.loc[stk_id]
# df['zt_num'] = zt_check_num.loc[stk_id]
# df[df == 0] = np.nan
# tmp_res = df.dropna(how='all', axis=0).sort_values(['num', 'pct', 'zt_num'],ascending=False)

res_df = pd.DataFrame(res_s)
res_df.index.names = ['股票代码']
res_df.columns = ['关联个股列表']
res_df = res_df.dropna()
res_df.to_excel('/data/user/015614/shared/for_wys/20220301-20230228个股按规则筛选前20个V2_20230306.xlsx')