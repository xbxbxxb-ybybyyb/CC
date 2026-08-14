# coding: utf-8
# Author：fengchi863
# Date ：2021/3/18 17:02

'''
韩旭代码：用来生成transData数据，写因子以及模拟撮合使用
'''

from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_int2windcode, trans_windcode2int
from xquant.marketdata import MarketData
from multiprocessing import Pool
from tqdm import tqdm

import numpy as np
import os

def multiprocess(lines, func, iterable, *args):
    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    for j in range(lines):
        sub_iter = iterable[j::lines]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args + (j,))
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

date_code = [x[:-4] for x in os.listdir('/data/group/800319/LimitTickData2/ReceiveDelay/')]
date_code_list = sorted([x[-8:] + x[:9] for x in date_code])
date_code_list = date_code_list[9761:]
_trade_items = ['date', 'code', 'MDTime', 'ReceiveDelay', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo',
                'TradeType', 'TradeBSFlag', 'TradeQty', 'TradeMoney', 'TradePrice']

# for item in _trade_items:
#     os.makedirs('/data/group/800319/LimitTradeData/%s' % item)

def prepare_trade_data(date_code, md):

    _date = date_code[:8]
    _code = date_code[8:]
    df = md.get_data_by_date('Transaction', _code, _date)
    if not len(df.columns):
        return
    df = df.loc[:, ['MDTime','ReceiveDateTime','TradeIndex','TradeBuyNo','TradeSellNo','TradeType','TradeBSFlag',
                    'TradeQty','TradeMoney','TradePrice']]
    df[['MDTime','TradeIndex','TradeBuyNo','TradeSellNo','TradeType','TradeBSFlag','TradeQty']] = \
        df[['MDTime','TradeIndex','TradeBuyNo','TradeSellNo','TradeType','TradeBSFlag','TradeQty']].applymap(int)
    df = df.loc[df['TradeQty'] > 0]
    df['ReceiveDateTime'] = df['ReceiveDateTime'].map(lambda x: int(str(x)[8:]) if x > 0 else x)
    df[['TradePrice','TradeMoney']] = df[['TradePrice','TradeMoney']].applymap(lambda x: round(float(x), 2))
    df.insert(2, 'ReceiveDelay', df['ReceiveDateTime'] - df['MDTime'])
    df['ReceiveDelay'] = np.fmax(0, df['ReceiveDelay'])
    df.drop('ReceiveDateTime', axis=1, inplace=True)
    df = df.fillna(0)

    MDTime = df['MDTime'].values.astype(np.int32)
    ReceiveDelay = df['ReceiveDelay'].values.astype(np.int32)
    TradeIndex = df['TradeIndex'].values.astype(np.int32)
    TradeBuyNo = df['TradeBuyNo'].values.astype(np.int32)
    TradeSellNo = df['TradeSellNo'].values.astype(np.int32)
    TradeType = df['TradeType'].values.astype(np.int8)
    TradeBSFlag = df['TradeBSFlag'].values.astype(np.int8)
    TradeQty = df['TradeQty'].values.astype(np.int32)
    TradeMoney = df['TradeMoney'].values.astype(np.float32)
    TradePrice = df['TradePrice'].values.astype(np.float32)
    date = np.full_like(MDTime, int(_date), np.int32)
    code = np.full_like(MDTime, trans_windcode2int(_code), np.int32)


    for item in _trade_items:
        np.save('/data/group/800319/LimitTradeData/%s/%s%s' % (item, _code, _date), eval(item))


def _func(sub_list, line=0):
    md = MarketData()
    for date_code in tqdm(sub_list):
        prepare_trade_data(date_code, md)

multiprocess(48, _func, date_code_list)


trade_format_dict = {
    'MDTime': np.int32,
    'ReceiveDelay': np.int32,
    'TradeIndex': np.int32,
    'TradeBuyNo': np.int32,
    'TradeSellNo': np.int32,
    'TradeType': np.int8,
    'TradeBSFlag': np.int8,
    'TradeQty': np.int32,
    'TradeMoney': np.float32,
    'TradePrice': np.float32,
    'date': np.int32,
    'code': np.int32,
}

def _get_trade_1dc(date, code, address='/data/group/800319/LimitTradeData/'):

    date = str(trans_datetime2int(date))
    code = trans_int2windcode(code)
    trade_data = {}
    items = {
        'MDTime': 'TimeStamp',
        'TradePrice': 'Price',
        'TradeQty': 'Volume',
        'TradeType': 'TradeType',
    }
    for item in items:
        trade_data[items[item]] = np.load(f'{address}/{item}/{code}{date}.npy')
    return trade_data

def get_transaction_data(code, date, address='/data/group/800319/LimitTradeData/'):

    date = str(trans_datetime2int(date))
    code = trans_int2windcode(code)
    trade_data = {}
    items = {
        'MDTime': 'TimeStamp',
        'TradePrice': 'Price',
        'TradeQty': 'Volume',
        'TradeType': 'TradeType',
    }
    for item in items:
        trade_data[items[item]] = np.load(f'{address}/{item}/{code}{date}.npy')
    return trade_data
