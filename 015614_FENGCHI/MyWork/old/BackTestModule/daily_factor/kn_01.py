# coding: utf-8
# Author：fengchi863
# Date ：2020/3/19 22:48

from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from dataApi.indName import *
import numpy as np
import datetime as dt

# stock_list = get_stock_list()
start_date = 20170101
end_date = 20191231
trade_date = get_date_range(get_pre_trade_date(start_date, 10), end_date)

stock_pool_all = clean_stock_list(
    no_ST=True,
    stock_list='COMMON',
    least_live_days=120,
    no_pause=True,
    least_recover_days=5,
    no_limit_up=False,
    no_limit_down=False,
    address='/data/group/800319/junkData/daily',
).reindex(index=trade_date)
stock_list = stock_pool_all.columns.tolist()

df_close_min = get_minute_1factor('close_badj_5m', get_pre_trade_date(start_date, 10), end_date, minute_interval=5, code_list=stock_list)
df_high_min = get_minute_1factor('high_badj_5m', get_pre_trade_date(start_date, 10), end_date, minute_interval=5, code_list=stock_list)
df_low_min = get_minute_1factor('low_badj_5m', get_pre_trade_date(start_date, 10), end_date, minute_interval=5, code_list=stock_list)
df_pch_min = df_close_min / df_close_min.shift(1) - 1.0
df_amt_min = get_minute_1factor('amt_5m', get_pre_trade_date(start_date, 10), end_date, minute_interval=5, code_list=stock_list)
df_atr_min = (df_high_min - df_low_min) / df_close_min.shift(1)
df_atr_rolling = df_atr_min.rolling(window=4840).mean()
df_atr_ratio = df_atr_min / df_atr_rolling
df_major_buy = pd.DataFrame(0, index=trade_date, columns=stock_list)
df_major_sell = pd.DataFrame(0, index=trade_date, columns=stock_list)

for i_code in stock_list:
    print(i_code)
    df_close_unstack = df_close_min.loc[:, i_code].unstack()
    df_pct_unstack = df_pch_min.loc[:, i_code].unstack()
    df_atr_ratio_unstack = df_atr_ratio.loc[:, i_code].unstack()
    df_amt_unstack = df_amt_min.loc[:, i_code].unstack()
    for i_date in trade_date:
        # print(i_date)
        major_buy = 0
        major_sell = 0
        atr_ratio_temp = df_atr_ratio_unstack.loc[i_date]
        min_temp = atr_ratio_temp[atr_ratio_temp >= 3.0].index.tolist()
        if min_temp.__len__() > 0:
            for i_min in min_temp:
                if df_pct_unstack.loc[i_date, i_min] > 0:
                    major_buy += df_amt_unstack.loc[i_date, i_min]
                else:
                    major_sell += df_amt_unstack.loc[i_date, i_min]
        df_major_buy.loc[i_date, i_code] = major_buy / 10000
        df_major_sell.loc[i_date, i_code] = major_sell / 10000

# address = '/data/user/011670/StrategyResearch/' + str(end_date) + '/'
# if not os.path.exists(address):
#     os.makedirs(address)
# full_file_name = address + 'major_money_flow_' + str(end_date) + '.xlsx'
df_diff = df_major_buy - df_major_sell
df_diff_rolling = df_diff.rolling(window=5).sum().loc[get_date_range(start_date, end_date)]

root_path =  '/data/group/800319/junkData/temp_factor_by_fc/'
df_diff_rolling.to_hdf(root_path + 'kn_01.h5', 'factor')