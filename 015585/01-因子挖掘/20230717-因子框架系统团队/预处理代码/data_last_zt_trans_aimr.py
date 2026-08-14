# -*- coding: utf-8 -*-
# @Time    : 2021/5/31 15:34
# @Author  : wangweidi
import pandas as pd
import numpy as np
import os
from xquant.marketdata import MarketData
from xquant.compute.aimr import AIMR
import IO
from xquant.factordata import FactorData
mdp = MarketData()
s = FactorData()

param = AIMR.getParam()
#param='/data/group/800463/data/project2_prod/everyday_Data/last_zt_trans/-20230413;'
param_list = param.split('-')
result_path = param_list[0]
param = param_list[1]
tradingday_list = param[:-1].split(';')
print(tradingday_list)

def cal_ul_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.1 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.2 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']

def get_after_not_ul_len(md_df):
    ipo_data = pd.read_hdf('/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
    ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
    ipo_data = ipo_data.reset_index()
    ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00'])]  # 筛选上交所和深交所股票，不包括科创板
    ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
    ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
    ipo_data['dt'] = ipo_data['list_date']
    ipo_data['is_list_date'] = True
    ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

    md_df = md_df.join(ipo_data)
    md_df['after_list'] = md_df['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_df.loc[md_df['amt'] == 0]['after_list'] = np.nan
    md_df['list_len'] = md_df['after_list'].unstack().rolling(10000000, 1).sum().stack()
    md_df.loc[(md_df['list_len'].isnull() & (md_df['amt'] > 0)), 'list_len'] = 250
    md_df['list_len'] = md_df['list_len'].unstack().fillna(method='ffill').stack()
    md_df.loc[(md_df['list_len'] > 250), 'list_len'] = 250

    md_df['1_1_ul_price'] = (md_df['pre_close'] * 100 * 1.1 + 0.5).apply(np.floor) / 100  # 正常的涨停价
    md_df['1_44_ul_price'] = (md_df['pre_close'] * 100 * 1.44 + 0.5).apply(np.floor) / 100  # 首日的涨停价
    md_df['is_one_ul'] = np.nan
    md_df.loc[md_df['amt'] > 0, 'is_one_ul'] = 0  # 有交易的变为0
    md_df.loc[(md_df['is_list_date'] & (md_df['close'] == md_df['1_44_ul_price'])), 'is_one_ul'] = 2  # 第一天涨停变为2
    md_df.loc[(md_df['open'] == md_df['close']) & (md_df['high'] == md_df['low']) & (
                md_df['close'] == md_df['1_1_ul_price']), 'is_one_ul'] = 1  # 正常一字板变为1
    md_df['is_list_ul'] = (md_df['is_one_ul'].unstack().rolling(10000, 1).mean() > 1).stack()
    md_df['is_list_ul'] = md_df['is_list_ul'] == True
    md_df['first_not_ul'] = ((md_df['is_list_ul'].unstack().shift(1).stack() == True) & (md_df['is_list_ul'] == False) |
                             (md_df['is_list_date'] & (md_df['is_list_ul'] == False)))  # 前日是上市涨停，当日不涨停; 或者上市首日开板
    md_df.loc[md_df['first_not_ul'] != True, 'first_not_ul'] = np.nan

    md_df['after_first_not_ul'] = md_df['first_not_ul'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_df.loc[md_df['amt'] == 0]['after_first_not_ul'] = np.nan
    md_df['after_not_ul_len'] = md_df['after_first_not_ul'].unstack().rolling(10000000, 1).sum().stack()
    md_df.loc[(md_df['after_not_ul_len'].isnull() & (md_df['amt'] > 0) & (md_df['is_list_ul'] == False)), 'after_not_ul_len'] = 200
    md_df['after_not_ul_len'] = md_df['after_not_ul_len'].unstack().fillna(method='ffill').stack()
    md_df.loc[(md_df['after_not_ul_len'] > 200), 'after_not_ul_len'] = 200
    return md_df['after_not_ul_len']

def cal_pattern(x):
    if x['ul_price']!=x['close']:
        return np.nan
    elif x['low'] == x['ul_price']:
        return 1
    elif x['open'] == x['ul_price']:
        return 2
    else:
        return 3

def get_hf_pattern(md_df):
    def fun_common_time_interval(time1, time2):
        time3 = float(np.floor(time1 / 10000000) * 3600 + np.floor(np.mod(time1, 10000000) / 100000) * 60 + np.mod(time1,100000) / 1000)
        time4 = float(np.floor(time2 / 10000000) * 3600 + np.floor(np.mod(time2, 10000000) / 100000) * 60 + np.mod(time2, 100000) / 1000)
        if (time1 <= 113000000) & (time2 >= 130000000):
            seconds = (time4 - time3) - 1.5 * 3600
        elif (time1 < 93000000) & (time2 >= 93000000):
            seconds = (time4 - time3) - 4 * 60
        else:
            seconds = time4 - time3
        return round(seconds, 3) / 60
    md_df = mdp.get_data_by_date('Transaction', stock_code, tradingday)
    md_df['MDTime'] = md_df['MDTime'].astype(float)
    md_df = md_df[md_df['TradePrice']>0]
    ul_price = md_df['TradePrice'].max()

    ZT_Time = md_df[md_df['TradePrice']==ul_price]['MDTime'].iloc[0]
    last_not_zt_time = md_df[(md_df['TradePrice'] != ul_price)].iloc[-1]['MDTime']
    last_zt_start_time = md_df[(md_df['MDTime'] >= last_not_zt_time) & (md_df['TradePrice'] == ul_price)].iloc[0]['MDTime']
    not_zt_len = fun_common_time_interval(ZT_Time, last_zt_start_time)
    if not_zt_len > 10:
        return 3
    else:
        return 4

start_date, end_date = min(tradingday_list), max(tradingday_list)
md_data = IO.read_data([s.tradingday(start_date, -250)[0], end_date], columns=['pre_close', 'close', 'open', 'low', 'high', 'amt'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['float_shares'] = IO.read_data([start_date, end_date], columns=['FLOAT_A_SHR_TODAY'], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
md_data['industry'] = IO.read_data([start_date, end_date], columns=['Industry'], alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
md_data['after_not_ul_len'] = get_after_not_ul_len(md_df=md_data.copy())
md_data['ul_price'] = cal_ul_price(md_data[['pre_close']])
md_data['is_ul'] = md_data['ul_price'] == md_data['close']
md_data = md_data[md_data['is_ul']]
md_data['pattern'] = md_data[['ul_price', 'close', 'open', 'low']].apply(lambda x:cal_pattern(x), axis=1)
md_data['tradingday'] = list(pd.Series(md_data.index.get_level_values(0)).apply(lambda x:x.strftime('%Y%m%d')))

for tradingday in tradingday_list:
    print(tradingday)
    sample_df = md_data[md_data['tradingday']==tradingday]
    trans_data_list = []
    for index, inf in sample_df.iterrows():
        try:
            stock_code = index[1]
            print(tradingday, stock_code)
            trans_data = mdp.get_data_by_date('Transaction', stock_code, tradingday)
            pattern = inf['pattern'] if inf['pattern'] != 3 else get_hf_pattern(trans_data.copy())
            trans_data['MDTime'] = trans_data['MDTime'].astype(int)
            trans_data['dt'] = trans_data['MDDate'].apply(pd.Timestamp)
            trans_data['Ticker'] = stock_code
            trans_data = trans_data.set_index(['dt', 'Ticker'])

            # 处理'TradeBSFlag'全是0的情况,XTrader里应该不会遇到
            if trans_data['TradeBSFlag'].sum() == 0:
                temp_BSFlag = trans_data['TradeBSFlag'].copy()
                temp_BSFlag[trans_data['TradeBuyNo'] < trans_data['TradeSellNo']] = 2.0
                temp_BSFlag[trans_data['TradeBuyNo'] > trans_data['TradeSellNo']] = 1.0
                trans_data['TradeBSFlag'] = temp_BSFlag
                print('BSFlag fixed')
            # 清洗集合竞价期间BSFlag
            trans_data.loc[trans_data['MDTime'] < 92900000, 'TradeBSFlag'] = 0

            used_cols = ['MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney']
            trans_data = trans_data[used_cols]
            # trans_data['TradeMoney'] = trans_data['TradePrice'] * trans_data['TradeQty']#处理TradeMoney计算不对的问题，XTrader应该不会遇到
            if (trans_data['TradeMoney'] - trans_data['TradePrice'] * trans_data['TradeQty']).abs().max() > 1e-5:
                print('TradeMoney warning!!!!!',
                      (trans_data['TradeMoney'] - trans_data['TradePrice'] * trans_data['TradeQty']).abs().max())
            trans_data['pre_close'] = inf['pre_close']
            trans_data['ff_shares'] = inf['float_shares']
            trans_data['pattern'] = pattern
            trans_data['industry'] = inf['industry']
            trans_data['after_not_ul_len'] = inf['after_not_ul_len']
            trans_data_list.append(trans_data)
        except Exception as e:
            print(e, '!'*100)
    day_trans_data = pd.concat(trans_data_list)
    day_trans_data.to_pickle('%s%s.pkl'%(result_path, tradingday))

