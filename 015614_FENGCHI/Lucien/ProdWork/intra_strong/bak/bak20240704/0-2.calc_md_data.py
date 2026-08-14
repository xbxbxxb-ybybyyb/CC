# coding: utf-8
# Author：fengchi863
# Date ：2024/3/5 9:07

# 准备当天的md_data，同时计算一些基础指标，供后续直接读取，不再重复计算
import pandas as pd
import numpy as np
import os
from xquant.marketdata import MarketData
mdp = MarketData()
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
import sys
import time

if len(sys.argv) > 1:
    today_date = sys.argv[1]
else:
    today_date = dt.datetime.today().strftime('%Y%m%d')
    # today_date = '20240305'

print('0-2.开始准备md_data数据')
output_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/md_data_wind/'

def get_big_data(start_date=20200301, end_date=20240306):
    date_list = s.tradingday(start_date, end_date)
    fold_num = 20
    per_num = len(date_list) // fold_num
    md_data_list = list()
    for idx in range(fold_num + 1):
        start = idx * per_num
        end = (idx + 1) * per_num
        if end >= len(date_list):
            end = len(date_list) - 1
        sd, ed = date_list[start], date_list[end]
        md_data = s.get_factor_value('WIND_AShareEODPrices',
                                     factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_PCTCHANGE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AVGPRICE', 'S_DQ_ADJFACTOR'],
                                     TRADE_DT=s.tradingday(sd, ed)).rename(
            columns={'S_INFO_WINDCODE': 'Ticker', 'TRADE_DT': 'dt', 'S_DQ_PCTCHANGE': 'pct_chg', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_OPEN': 'open',
                     'S_DQ_HIGH': 'high', 'S_DQ_LOW': 'low', 'S_DQ_CLOSE': 'close', 'S_DQ_AVGPRICE': 'vwap', 'S_DQ_ADJFACTOR': 'adjfactor'})
        md_data_list.append(md_data)
    md_data = pd.concat(md_data_list, axis=0)
    return md_data

# 首先检测当天WIND数据是否完备
while True:
    if today_date != dt.datetime.today().strftime('%Y%m%d'):
        break
    md_data = s.get_factor_value('WIND_AShareEODPrices',
                                 factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_CLOSE'],
                                 TRADE_DT=today_date).rename(
        columns={'S_INFO_WINDCODE': 'Ticker', 'TRADE_DT': 'dt', 'S_DQ_CLOSE': 'close'})
    md_data['dt'] = md_data['dt'].apply(lambda x: pd.to_datetime(x))
    md_data = md_data.set_index(['dt', 'Ticker']).sort_values(['dt', 'Ticker'])

    if md_data.iloc[-1].name[0].strftime('%Y%m%d') >= today_date:  # 当日有数据
        break
    else:
        print(f'{today_date}_WIND数据未完备')
        time.sleep(60)

t1 = time.time()
start_date = s.tradingday(today_date, -20)[0]
if not os.path.exists(output_path + f'{start_date}-{today_date}.pkl'):
    md_data = s.get_factor_value('WIND_AShareEODPrices',
                                 factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_PCTCHANGE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AVGPRICE', 'S_DQ_ADJFACTOR'],
                                 TRADE_DT=s.tradingday(start_date, today_date)).rename(
        columns={'S_INFO_WINDCODE': 'Ticker', 'TRADE_DT': 'dt', 'S_DQ_PCTCHANGE': 'pct_chg', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_OPEN': 'open',
                 'S_DQ_HIGH': 'high', 'S_DQ_LOW': 'low', 'S_DQ_CLOSE': 'close', 'S_DQ_AVGPRICE': 'vwap', 'S_DQ_ADJFACTOR': 'adjfactor'})
    # md_data = get_big_data(20200301, today_date)
    md_data['dt'] = md_data['dt'].apply(lambda x: pd.to_datetime(x))
    md_data = md_data.set_index(['dt', 'Ticker']).sort_values(['dt', 'Ticker'])

    md_data['new_300'] = ((md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (md_data.reset_index()['dt'] >= '20200824')) | \
                          (md_data.reset_index()['Ticker'].apply(lambda x: x[:2] == '68') & (md_data.reset_index()['dt'] >= '20100824'))).values
    md_data['zcz'] = md_data['new_300']
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_deal_temp = md_data.reset_index()
    md_deal_temp = md_deal_temp[(md_deal_temp['Ticker'].apply(lambda x: x[0] == '3') & (md_deal_temp['dt'] >= '20200824')) |
                                (md_deal_temp['Ticker'].apply(lambda x: x[:2] == '68') & (md_deal_temp['dt'] >= '20100824')) ].set_index(['dt', 'Ticker'])
    md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['next_ul_price'] = np.floor(md_data['close'] * 100 * 1.1 + 0.5) / 100
    md_data.loc[md_data['new_300'], 'next_ul_price'] = np.floor(md_data.loc[md_data['new_300'], 'close'] * 100 * 1.2 + 0.5) / 100
    md_data['label_T_zt'] = (md_data['close'] == md_data['ul_price']).astype(int)
    md_data['raw_close'], md_data['raw_high'], md_data['raw_low'], md_data['raw_open'], md_data['raw_pre_close'], md_data['raw_vwap'] = \
        md_data['close'], md_data['high'], md_data['low'], md_data['open'], md_data['pre_close'], md_data['vwap']

    md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
    md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
    md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
    md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
    md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
    md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
    md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
    md_data['next_close'] = md_data['close'].unstack().shift(-1).stack()
    md_data['next_raw_close'] = md_data['raw_close'].unstack().shift(-1).stack()
    md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
    md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
    md_data['next_close'] = md_data['next_close'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['next_raw_close'] = md_data['next_raw_close'].unstack().fillna(method='bfill', axis=0).stack()

    md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
    md_data['label_Tc2Tul'] = md_data['close'] / md_data['ul_price'] - 1
    md_data['label_T1o2Tc'] = md_data['next_open'] / md_data['close'] - 1
    md_data['label_T1c2Tc'] = md_data['next_close'] / md_data['close'] - 1
    md_data['label_T1_zt'] = (md_data['next_raw_close'] == md_data['next_ul_price']).astype(int)
    md_data['pct_t'] = md_data['close'] / md_data['high'] - 1   # 用于当日收益率计算
    md_data['is_zt'] = md_data['close'] == md_data['ul_price']
    md_data['last_is_zt'] = md_data['is_zt'] .unstack().shift().stack()

    last_is_zt = pd.read_pickle('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/last_is_zt/updating.pkl')
    if today_date == dt.datetime.today().strftime('%Y%m%d'):
        last_is_zt = pd.concat([last_is_zt, md_data.loc[pd.to_datetime(today_date):]['last_is_zt']], axis=0)
        last_is_zt = last_is_zt.reset_index().drop_duplicates(['dt', 'Ticker']).set_index(['dt', 'Ticker']).sort_index()
        last_is_zt.to_pickle(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/last_is_zt/updating.pkl')
    md_data.to_pickle(output_path + f'{start_date}-{today_date}.pkl')

    print('已生成' + output_path + f'{start_date}-{today_date}.pkl！！！！')
    print('已生成/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/last_is_zt/updating.pkl')
else:
    # md_data = pd.read_pickle(output_path + f'{start_date}-{today_date}.pkl')
    print(output_path + f'{start_date}-{today_date}.pkl' + '数据已存在！！！！')

print(f'0-2.calc_md_data耗时{round(time.time() - t1, 6)}秒')