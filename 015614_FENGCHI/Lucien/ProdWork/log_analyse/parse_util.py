# coding: utf-8
# Author：fengchi863
# Date ：2024/3/21 17:17

from LucienUtil import IO
import numpy as np

def get_TN_o2ul(start_date, end_date):
    md_data = IO.read_data([start_date, end_date], columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_data['new_300'] = (md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (md_data.reset_index()['dt'] >= '20200824')).values
    md_data.loc[md_data['new_300'], 'ul_price'] = np.floor(md_data.loc[md_data['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
    md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
    md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
    md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
    md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
    md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
    md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
    md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
    md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
    return md_data

def cal_sell_start_time(df):
    if 'PENDING_NEW' in list(df['ordStatus']):
        sell_start_time = df[df['ordStatus'] == 'PENDING_NEW']['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values[0]
    else:
        sell_start_time = df['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.min()
    return sell_start_time

def cal_sell_end_time(df):
    if 'FILLED' in list(df['ordStatus']):
        sell_end_time = df[df['ordStatus'] == 'FILLED']['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.max()
    else:
        sell_end_time = df['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.max()
    return sell_end_time