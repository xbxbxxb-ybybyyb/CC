# coding: utf-8
# Author：fengchi863
# Date ：2023/3/6 20:34

import numpy as np
import pandas as pd

from LucienUtil import IO
from dataApi import stockList, tradeDate
from dataApi.getData import get_daily_1factor
from dataApi.indName import sw2021_level1
from tqdm import tqdm


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

start_date = 20220101
end_date = 20230228
# stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=0, least_normal_days=10, no_pause=True, least_recover_days=0, start_date=start_date, end_date=end_date)
# tszl_df = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5')
# tszl_df = tszl_df.query('S_TYPE_ST == "L"')[['ENTRY_DT']].reset_index()
# tszl_df['Ticker'] = tszl_df['Ticker'].apply(lambda x: stockList.trans_windcode2int(x))
# tszl_df = tszl_df.query(f'ENTRY_DT >= {start_date}')
# for idx in range(len(tszl_df)):
#     stk_id = tszl_df.iloc[idx]['Ticker']
#     tszl_date = tszl_df.iloc[idx]['ENTRY_DT']
#     stk_pool.loc[tszl_date:, stk_id] = False
# # stk_pool.to_pickle('/data/user/015614/junkData/stk_pool.pkl')

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
sw1 = get_daily_1factor('SW20211', code_list=code_list, date_list=date_list)
up714_flag = (high >= price714) & stk_pool
zt_flag = (high == limit_max) & stk_pool

# 去除科创板
up714_flag = up714_flag[list(filter(lambda x: x // 10000 != 68, code_list))]
zt_flag = zt_flag[list(filter(lambda x: x // 10000 != 68, code_list))]
############################
"""
20230306下午新任务：你试下满足两个条件：>=7%发生的次数>=5次，且占比>=50%，这只股票满足这2个条件对应的数量要>=5个，不满足的置为空。数量大于20个的，按照>=7%的次数、占比和zt的次数进行排序，取前20个。
20230306晚上任务：一级行业作为筛选，根据20230228当天的行业作为基础
20230308上午任务：进行log加权
"""
stk_len = up714_flag.shape[1]
date_list_1year = tradeDate.get_date_range(20220301, 20230228)
# date_list_1year = tradeDate.get_date_range(20230201, 20230228)
check_num = np.zeros((stk_len, stk_len))  # AB超过7%次数
weighted_check_num = np.zeros((stk_len, stk_len))  # AB超过7%次数 加权
zt_check_num = np.zeros((stk_len, stk_len))   # AB涨停次数
weighted_zt_check_num = np.zeros((stk_len, stk_len))   # AB涨停次数 加权
weighted_check_pct = np.zeros((stk_len, stk_len))   # AB 7% 比例 加权
weighted_zt_check_pct = np.zeros((stk_len, stk_len))    # AB 涨停比例 加权

# 计算log分母
e_sum = 0
interval_month_list = list()
for _date in date_list_1year:
    interval_month_list.append(-tradeDate.get_trade_date_interval(_date, base_date=end_date) // 21 + 1)

for interval_month in list(set(interval_month_list)):
    e_sum += np.exp(interval_month)

for _date in tqdm(date_list_1year):
    interval_month = -tradeDate.get_trade_date_interval(_date, base_date=end_date) // 21 + 1
    tmp_check1 = up714_flag.loc[_date].astype(int).values[:, None] * up714_flag.loc[_date].astype(int).values[:, None].T
    tmp_check2 = zt_flag.loc[_date].astype(int).values[:, None] * zt_flag.loc[_date].astype(int).values[:, None].T
    _w = np.exp(max(interval_month_list) - interval_month + 1) / e_sum
    # print(_w)
    check_num += tmp_check1
    zt_check_num += tmp_check2
    weighted_check_num += tmp_check1 * _w
    weighted_zt_check_num += tmp_check2 * _w

for _date in tqdm(date_list_1year):
    interval_month = -tradeDate.get_trade_date_interval(_date, base_date=end_date) // 21 + 1
    tmp_check1 = up714_flag.loc[_date].astype(int).values[:, None] * up714_flag.loc[_date].astype(int).values[:, None].T
    tmp_check2 = zt_flag.loc[_date].astype(int).values[:, None] * zt_flag.loc[_date].astype(int).values[:, None].T
    _w = np.exp(max(interval_month_list) - interval_month + 1) / e_sum
    # print(_w)
    weighted_check_pct += (tmp_check1 * _w / np.array([check_num[i][i] for i in range(len(check_num))]))    # 第一行作为除以AA、BB、CC、DD的比例
    weighted_zt_check_pct += (tmp_check2 * _w / np.array([zt_check_num[i][i] for i in range(len(zt_check_num))]))

check_pct = (check_num / np.array([check_num[i][i] for i in range(len(check_num))]))
zt_check_pct = (zt_check_num / np.array([zt_check_num[i][i] for i in range(len(zt_check_num))]))

for idx in range(len(check_num)):
    check_num[idx, idx] = np.nan
    check_pct[idx, idx] = np.nan
    zt_check_num[idx, idx] = np.nan
    weighted_check_num[idx, idx] = np.nan
    weighted_check_pct[idx, idx] = np.nan
    weighted_zt_check_num[idx, idx] = np.nan
    weighted_zt_check_pct[idx, idx] = np.nan

# 转换成带index的，然后开始排序
check_num = pd.DataFrame(check_num, index=up714_flag.columns, columns=up714_flag.columns)
weighted_check_num = pd.DataFrame(weighted_check_num, index=up714_flag.columns, columns=up714_flag.columns)
zt_check_num = pd.DataFrame(zt_check_num, index=up714_flag.columns, columns=up714_flag.columns)
check_pct = pd.DataFrame(check_pct, index=up714_flag.columns, columns=up714_flag.columns)
weighted_check_pct = pd.DataFrame(weighted_check_pct, index=up714_flag.columns, columns=up714_flag.columns)
weighted_zt_check_num = pd.DataFrame(weighted_zt_check_num, index=up714_flag.columns, columns=up714_flag.columns)
weighted_zt_check_pct = pd.DataFrame(weighted_zt_check_pct, index=up714_flag.columns, columns=up714_flag.columns)

end_sw1 = sw1.loc[end_date]

res_df = pd.DataFrame(index=up714_flag.columns, columns=['res', 'ind', 'num'])
for stk_id in tqdm(res_df.index):
    df = pd.DataFrame(columns=['num', 'pct'])
    df['num'] = weighted_check_num.loc[stk_id]
    df['pct'] = weighted_check_pct.loc[stk_id]
    df['zt_num'] = weighted_zt_check_num.loc[stk_id]
    df['zt_pct'] = weighted_zt_check_pct.loc[stk_id]

    tmp_res = df.fillna(0).sort_values(['num', 'pct', 'zt_num', 'zt_pct'], ascending=False)
    same_ind_stk_list = end_sw1[end_sw1 == end_sw1[stk_id]].index.tolist()
    if stk_id in same_ind_stk_list:
        same_ind_stk_list.remove(stk_id)
    tmp_res = tmp_res.loc[[x for x in tmp_res.index.tolist() if x in same_ind_stk_list]]

    # 同行业
    tmp_res = tmp_res.reset_index()
    rank20_num = tmp_res.loc[19, 'num'] if len(tmp_res) >= 20 else (tmp_res.iloc[-1]['num'] if len(tmp_res) > 0 else 0)

    if rank20_num > 0:
        tmp_res = tmp_res.query(f'num >= {rank20_num}')

    tmp_res = tmp_res[['index', 'num']].apply(lambda x: str(int(x['index'])) + '(' + str(round(x['num'] * 100, 2)) + ')', axis=1)
    res_df.loc[stk_id, 'res'] = ', '.join(map(str, tmp_res.tolist())) if len(tmp_res) > 0 else ''
    res_df.loc[stk_id, 'num'] = len(res_df.loc[stk_id, 'res'].split(', '))  if res_df.loc[stk_id, 'res'] != '' else 0

    res_df.loc[stk_id, 'ind'] = end_sw1[stk_id]

# test
# stk_id = 585
# df = pd.DataFrame(columns=['num', 'pct', 'zt_num'])
# df['num'] = check_num.loc[stk_id]
# df['pct'] = check_pct.loc[stk_id]
# df['zt_num'] = zt_check_num.loc[stk_id]
# df[df == 0] = np.nan
# tmp_res = df.dropna(how='all', axis=0).sort_values(['num', 'pct', 'zt_num'],ascending=False)

res_df['ind'] = res_df['ind'].apply(lambda x: sw2021_level1[x] if np.isfinite(x) else '')
res_df = res_df.dropna()
stk_pool = stk_pool[up714_flag.columns]
save_stk_list = stk_pool.loc[20220301:20230228].sum(axis=0)[stk_pool.loc[20220301:20230228].sum(axis=0) > 0].index.tolist()
res_df = res_df.loc[save_stk_list]

old_res_df = pd.read_excel('/data/user/015614/shared/for_wys/20220301-20230228个股按规则筛选前20个V5_20230309.xlsx', index_col=0)
diff_index = list()
for idx in range(len(old_res_df)):
    if old_res_df.iloc[idx]['关联股票列表'] == res_df.iloc[idx]['res']:
        print(True)
    else:
        diff_index.append(old_res_df.iloc[idx].name)
res_df.to_excel('/data/user/015614/shared/for_wys/20220301-20230228个股按规则筛选前20个V6_20230311.xlsx')