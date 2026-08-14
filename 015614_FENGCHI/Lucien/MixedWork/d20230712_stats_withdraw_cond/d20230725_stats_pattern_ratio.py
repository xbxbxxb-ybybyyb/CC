# coding: utf-8
# Author：fengchi863
# Date ：2023/7/25 10:20

# 统计transaction中形态2、形态3、形态4的比例

import pandas as pd
from tqdm import tqdm
from xquant.marketdata import MarketData
import os
mdp = MarketData()


def cal_time_delta(start, end):
    """计算相差毫秒数"""
    start_str = str(start)
    end_str = str(end)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta

test_path = '/data/user/015614/TEST/'
trans_path = '/arch1/user/015614/TEST/及时撤单/trans_data/'
profit_data_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
label_data_fpath = '/data/user/018107/share_file/for_fc/europa/20230329_new/factor_df_all_20160101_20230331.pkl'

zb_info_fpath = '/data/user/018107/share_file/for_fc/europa_ul_time_20220518_20230528.pkl'
zb_info = pd.read_pickle(zb_info_fpath)
zb_info = zb_info.dropna(axis=0)

profit_data = pd.read_hdf(profit_data_fpath)
label_data = pd.read_pickle(label_data_fpath)

# for idx in tqdm(range(len(zb_info))):
#     row = zb_info.iloc[idx]
#     index = row.name
#     stock_code = index[1]
#     buy_date_dt = index[0]
#     buy_date_str = index[0].strftime('%Y%m%d')
#     print(buy_date_str, stock_code)
#
#     if not os.path.exists(trans_path + f'{buy_date_str}_{stock_code}.pkl'):
#         trans_df = mdp.get_data_by_date("Transaction", stock_code, buy_date_str, ["2", "3"])
#         trans_df.to_pickle(trans_path + f'{buy_date_str}_{stock_code}.pkl')
#     else:
#         trans_df = pd.read_pickle(trans_path + f'{buy_date_str}_{stock_code}.pkl')
#
#     trans_df = trans_df.query('TradePrice != 0')
#     ul_price = trans_df['TradePrice'].max()
#     ul_trans_df = trans_df.query(f'TradePrice == {ul_price}')
#
#     label_touch_ul_time = row['label_touch_ul_time']
#     label_firstUL_end_time = row['label_firstUL_end_Time']
#     label_touch_ul_dt = int(label_touch_ul_time)
#     label_firstUL_end_dt = int(label_firstUL_end_time)
#     time_delta = cal_time_delta(label_touch_ul_dt, label_firstUL_end_dt) / 1000
#     index = (buy_date_dt, stock_code)
#     zb_info.loc[index, '第一次涨停板上时间'] = time_delta
#     if index in label_data.index:
#         zb_info.loc[index, 'pattern'] = label_data.loc[index]['label_pattern']
#
# zb_info.to_pickle(test_path + '不同形态下第一次涨停板上时间.pkl')
zb_info = pd.read_pickle(test_path + '不同形态下第一次涨停板上时间.pkl')

profit_data['profit'] = profit_data['buy_amt'] * profit_data['pct']
zb_info_ = pd.concat([zb_info, profit_data[['profit']]], axis=1)
zb_info = zb_info_.loc[zb_info.index]
# zb_info['datelist'] = zb_info.index.get_level_values(0).strftime('%Y%m%d').map(int).tolist()
# zb_info.query('20220518 <= datelist <= 20230518')

paramA = [2, 3]
paramB = [0, 1, 5, 10, 15, 30, 60, 120, 180, 240, 300, 360, 420, 600, 1200, 1800, 3600]

from itertools import product
param_tuple_list = list(product(paramA, paramB))

res_df = pd.DataFrame(index=pd.MultiIndex.from_product([paramA, paramB]))
for param_tuple in param_tuple_list:
    param1, param2 = param_tuple
    res_df.loc[(param1, param2), 'count'] = zb_info.query(f'pattern == {param1} & 第一次涨停板上时间 >= {param2}').shape[0]
    res_df.loc[(param1, param2), 'ratio'] = zb_info.query(f'pattern == {param1} & 第一次涨停板上时间 >= {param2}').shape[0] / zb_info.query(f'pattern == {param1}').shape[0]
    res_df.loc[(param1, param2), 'profit'] = zb_info.query(f'pattern == {param1} & 第一次涨停板上时间 >= {param2}')['profit'].sum()
    res_df.loc[(param1, param2), 'win_rate'] = (zb_info.query(f'pattern == {param1} & 第一次涨停板上时间 >= {param2}')['profit'] > 0).mean()

from dataApi.sendInfo import send_file
send_file(res_df)

zb_info.query('pattern == 2 & 第一次涨停板上时间 >= 60').shape[0] / zb_info.query('pattern == 2').shape[0]
zb_info.query('pattern == 3 & 第一次涨停板上时间 >= 60').shape[0] / zb_info.query('pattern == 3').shape[0]


