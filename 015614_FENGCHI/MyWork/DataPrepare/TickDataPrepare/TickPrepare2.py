from StrategyResearch.TickDataPrepare2 import open_ticks, trade_ticks, close_ticks, trade_items, format_dict
from multiprocessing import Pool
from dataApi.getData import get_daily_1factor
from dataApi.stockList import trans_int2windcode, trans_windcode2int
from dataApi.tradeDate import get_date_range, trans_datetime2int
from xquant.marketdata import MarketData
from tqdm import tqdm
import pandas as pd
import numpy as np
import gc
import os
import shutil

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

# 1 重建文件夹
_trade_items = list((set(trade_items) - {'ReceiveDateTime', 'MDTime'}) | {'RawMDTime', 'ReceiveDelay'})
# for item in _trade_items:
#     # shutil.rmtree('/data/group/800442/800319/LimitTickData/%s' % item)
#     os.makedirs('/arch1/group/800442/800319/LimitTickData3/%s' % item)

# 2 取数据
date_list = get_date_range(20210725, 20210923)

high = get_daily_1factor('high', date_list)
low = get_daily_1factor('low', date_list)
limit_max = get_daily_1factor('limit_max', date_list).reindex(columns=high.columns)
limit_pool = (high == limit_max) & (low < limit_max)
limit_pool = limit_pool.stack()[limit_pool.stack()].reset_index().iloc[:, :-1]
limit_pool.columns = ['date', 'code']
limit_pool['date'] = limit_pool['date'].map(str)
limit_pool['code'] = limit_pool['code'].map(trans_int2windcode)
limit_pool = limit_pool.set_index(['date', 'code']).index.values.tolist()
del date_list, high, low, limit_max
gc.collect()

def prepare_tick_data(date_code, md):

    date = date_code[0]
    code = date_code[1]
    # 1 开盘集合竞价
    df0 = md.get_data_by_date('Stock', code, date, trading_phase_code=['0', '1'])
    if not len(df0.columns):
        return
    df0 = df0[trade_items]
    df0['MDTime'] = df0['MDTime'].map(int)
    df0['ReceiveDateTime'] = df0['ReceiveDateTime'] % (10 ** 9) - df0['MDTime']
    df0['MDTime'] = df0['MDTime'] // 1000
    df0 = df0.set_index('MDTime', drop=False)
    df0 = df0.rename(columns={'ReceiveDateTime': 'ReceiveDelay', 'MDTime': 'RawMDTime'})
    _open_ticks = sorted(list(set(df0.index) | set(open_ticks)))
    df0 = df0[~ df0.index.duplicated(keep='last')]
    df0 = df0.reindex(_open_ticks).ffill().reindex(open_ticks)
    df0.iloc[-2] = df0.iloc[-1]
    df0 = df0.iloc[:-1]

    # 2 连续竞价+收盘集合竞价
    df1 = md.get_data_by_date('Stock', code, date, trading_phase_code=['2', '3', '5', '6'])
    df1 = df1[df1['MDTime'] != '093000000']
    df1 = df1[trade_items]
    df1['MDTime'] = df1['MDTime'].map(int)
    df1['ReceiveDateTime'] = df1['ReceiveDateTime'] % (10 ** 9) - df1['MDTime']
    df1['MDTime'] = df1['MDTime'] // 1000
    df1 = df1.set_index('MDTime', drop=False)
    df1 = df1.rename(columns={'ReceiveDateTime': 'ReceiveDelay', 'MDTime': 'RawMDTime'})
    df1 = df1[~ df1.index.duplicated(keep='last')]
    _trade_ticks = sorted(list(set(df1.index) | set(trade_ticks) | set(close_ticks)))
    df1 = df1.reindex(_trade_ticks).ffill().reindex(trade_ticks + close_ticks + _trade_ticks[-1:])
    df1.iloc[-2] = df1.iloc[-1]
    df1 = df1.iloc[:-1]

    # 3 汇总共5000条 开200(91503-93000) 连4740(93003-145700) 收60(145703-150000)
    df = pd.concat([df0, df1]).fillna(0)
    ReceiveDelay = df['ReceiveDelay'].values.astype(np.int16)
    RawMDTime = df['RawMDTime'].values.astype(np.int32)
    NumTrades = df['NumTrades'].values.astype(np.int32)
    TotalVolumeTrade = df['TotalVolumeTrade'].values.astype(np.int64)
    TotalValueTrade = df['TotalValueTrade'].values.astype(np.float64)
    LastPx = df['LastPx'].values.astype(np.float32)
    HighPx = df['HighPx'].values.astype(np.float32)
    LowPx = df['LowPx'].values.astype(np.float32)
    TotalBidQty = df['TotalBidQty'].values.astype(np.int32)
    TotalOfferQty = df['TotalOfferQty'].values.astype(np.int32)
    WeightedAvgBidPx = df['WeightedAvgBidPx'].values.astype(np.float32)
    WeightedAvgOfferPx = df['WeightedAvgOfferPx'].values.astype(np.float32)
    WithdrawBuyNumber = df['WithdrawBuyNumber'].values.astype(np.int32)
    WithdrawBuyAmount = df['WithdrawBuyAmount'].values.astype(np.int64)
    WithdrawBuyMoney = df['WithdrawBuyMoney'].values.astype(np.float64)
    WithdrawSellNumber = df['WithdrawSellNumber'].values.astype(np.int32)
    WithdrawSellAmount = df['WithdrawSellAmount'].values.astype(np.int64)
    WithdrawSellMoney = df['WithdrawSellMoney'].values.astype(np.float64)
    TotalBidNumber = df['TotalBidNumber'].values.astype(np.int32)
    TotalOfferNumber = df['TotalOfferNumber'].values.astype(np.int32)
    BidTradeMaxDuration = df['BidTradeMaxDuration'].values.astype(np.int16)
    OfferTradeMaxDuration = df['OfferTradeMaxDuration'].values.astype(np.int16)
    NumBidOrders = df['NumBidOrders'].values.astype(np.int16)
    NumOfferOrders = df['NumOfferOrders'].values.astype(np.int16)
    Buy1Price = df['Buy1Price'].values.astype(np.float32)
    Buy2Price = df['Buy2Price'].values.astype(np.float32)
    Buy3Price = df['Buy3Price'].values.astype(np.float32)
    Buy4Price = df['Buy4Price'].values.astype(np.float32)
    Buy5Price = df['Buy5Price'].values.astype(np.float32)
    Buy6Price = df['Buy6Price'].values.astype(np.float32)
    Buy7Price = df['Buy7Price'].values.astype(np.float32)
    Buy8Price = df['Buy8Price'].values.astype(np.float32)
    Buy9Price = df['Buy9Price'].values.astype(np.float32)
    Buy10Price = df['Buy10Price'].values.astype(np.float32)
    Sell1Price = df['Sell1Price'].values.astype(np.float32)
    Sell2Price = df['Sell2Price'].values.astype(np.float32)
    Sell3Price = df['Sell3Price'].values.astype(np.float32)
    Sell4Price = df['Sell4Price'].values.astype(np.float32)
    Sell5Price = df['Sell5Price'].values.astype(np.float32)
    Sell6Price = df['Sell6Price'].values.astype(np.float32)
    Sell7Price = df['Sell7Price'].values.astype(np.float32)
    Sell8Price = df['Sell8Price'].values.astype(np.float32)
    Sell9Price = df['Sell9Price'].values.astype(np.float32)
    Sell10Price = df['Sell10Price'].values.astype(np.float32)
    DiffPx1 = df['DiffPx1'].values.astype(np.float32)
    DiffPx2 = df['DiffPx2'].values.astype(np.float32)
    Buy1OrderQty = df['Buy1OrderQty'].values.astype(np.int32)
    Buy2OrderQty = df['Buy2OrderQty'].values.astype(np.int32)
    Buy3OrderQty = df['Buy3OrderQty'].values.astype(np.int32)
    Buy4OrderQty = df['Buy4OrderQty'].values.astype(np.int32)
    Buy5OrderQty = df['Buy5OrderQty'].values.astype(np.int32)
    Buy6OrderQty = df['Buy6OrderQty'].values.astype(np.int32)
    Buy7OrderQty = df['Buy7OrderQty'].values.astype(np.int32)
    Buy8OrderQty = df['Buy8OrderQty'].values.astype(np.int32)
    Buy9OrderQty = df['Buy9OrderQty'].values.astype(np.int32)
    Buy10OrderQty = df['Buy10OrderQty'].values.astype(np.int32)
    Sell1OrderQty = df['Sell1OrderQty'].values.astype(np.int32)
    Sell2OrderQty = df['Sell2OrderQty'].values.astype(np.int32)
    Sell3OrderQty = df['Sell3OrderQty'].values.astype(np.int32)
    Sell4OrderQty = df['Sell4OrderQty'].values.astype(np.int32)
    Sell5OrderQty = df['Sell5OrderQty'].values.astype(np.int32)
    Sell6OrderQty = df['Sell6OrderQty'].values.astype(np.int32)
    Sell7OrderQty = df['Sell7OrderQty'].values.astype(np.int32)
    Sell8OrderQty = df['Sell8OrderQty'].values.astype(np.int32)
    Sell9OrderQty = df['Sell9OrderQty'].values.astype(np.int32)
    Sell10OrderQty = df['Sell10OrderQty'].values.astype(np.int32)
    Buy1NumOrders = df['Buy1NumOrders'].values.astype(np.int32)
    Buy2NumOrders = df['Buy2NumOrders'].values.astype(np.int32)
    Buy3NumOrders = df['Buy3NumOrders'].values.astype(np.int32)
    Buy4NumOrders = df['Buy4NumOrders'].values.astype(np.int32)
    Buy5NumOrders = df['Buy5NumOrders'].values.astype(np.int32)
    Buy6NumOrders = df['Buy6NumOrders'].values.astype(np.int32)
    Buy7NumOrders = df['Buy7NumOrders'].values.astype(np.int32)
    Buy8NumOrders = df['Buy8NumOrders'].values.astype(np.int32)
    Buy9NumOrders = df['Buy9NumOrders'].values.astype(np.int32)
    Buy10NumOrders = df['Buy10NumOrders'].values.astype(np.int32)
    Sell1NumOrders = df['Sell1NumOrders'].values.astype(np.int32)
    Sell2NumOrders = df['Sell2NumOrders'].values.astype(np.int32)
    Sell3NumOrders = df['Sell3NumOrders'].values.astype(np.int32)
    Sell4NumOrders = df['Sell4NumOrders'].values.astype(np.int32)
    Sell5NumOrders = df['Sell5NumOrders'].values.astype(np.int32)
    Sell6NumOrders = df['Sell6NumOrders'].values.astype(np.int32)
    Sell7NumOrders = df['Sell7NumOrders'].values.astype(np.int32)
    Sell8NumOrders = df['Sell8NumOrders'].values.astype(np.int32)
    Sell9NumOrders = df['Sell9NumOrders'].values.astype(np.int32)
    Sell10NumOrders = df['Sell10NumOrders'].values.astype(np.int32)

    for item in df.columns:
        np.save('/arch1/group/800442/800319/LimitTickData3/%s/%s%s' % (item, code, date), eval(item))

def _func(sub_list, line=0):
    md = MarketData()
    for date_code in tqdm(sub_list):
        prepare_tick_data(date_code, md)

# multiprocess(48, _func, limit_pool)

# 整理数据

address = '/arch1/group/800442/800319/LimitTickData3/'
_trade_items = list((set(trade_items) - {'ReceiveDateTime', 'MDTime'}) | {'RawMDTime', 'ReceiveDelay'})
date_code = [x[:-4] for x in os.listdir(address + _trade_items[0])]
date_code = sorted([x[-8:] + x[:9] for x in date_code])
date_code1 = [x[-9:] + x[:8] + '.npy' for x in date_code]

def restore_tick_data(address, _trade_items, date_code1):
    for item in _trade_items:
        arr = np.empty((len(date_code1), 5000), dtype=format_dict[item])
        for j, dc in tqdm(enumerate(date_code1)):
            arr[j] = np.load('%s/%s/%s' % (address, item, dc))
        np.save('/%s/%s.npy' % (address, item), arr)
        del arr
        gc.collect()

def _func2(sub_list, line=0):
    restore_tick_data(address, sub_list, date_code1)

# multiprocess(24, _func2, _trade_items)

def _get_tick_1factor(item, dc_idx, time_idx,
                      address='/arch1/group/800442/800319/LimitTickData3/'):

    dtype = format_dict[item]
    dc_idx = sorted(list(dc_idx))
    time_idx = sorted(list(time_idx))
    dc_max = dc_idx[-1]

    if dc_idx[-1] - dc_idx[0] + 1 == len(dc_idx):
        dc_idx = slice(dc_idx[0], dc_idx[-1] + 1)
    if time_idx[-1] - time_idx[0] + 1 == len(time_idx):
        time_idx = slice(time_idx[0], time_idx[-1] + 1)

    factor = np.memmap('%s/%s.npy' % (address, item),
                  dtype=dtype, mode='r', shape=(dc_max, 5000), offset=128)
    factor = factor[dc_idx, time_idx]
    return factor

def _get_tick_1dc(date, code, address='/arch1/group/800442/800319/LimitTickData3/'):

    date = str(trans_datetime2int(date))
    code = trans_int2windcode(code)
    tick_data = {}
    items = {
        'RawMDTime': 'TimeStamp',
        'Buy1Price': 'BidPrice1',
        'Buy2Price': 'BidPrice2',
        'Buy3Price': 'BidPrice3',
        'Buy4Price': 'BidPrice4',
        'Buy5Price': 'BidPrice5',
        'Buy6Price': 'BidPrice6',
        'Buy7Price': 'BidPrice7',
        'Buy8Price': 'BidPrice8',
        'Buy9Price': 'BidPrice9',
        'Buy10Price': 'BidPrice10',
        'Sell1Price': 'AskPrice1',
        'Sell2Price': 'AskPrice2',
        'Sell3Price': 'AskPrice3',
        'Sell4Price': 'AskPrice4',
        'Sell5Price': 'AskPrice5',
        'Sell6Price': 'AskPrice6',
        'Sell7Price': 'AskPrice7',
        'Sell8Price': 'AskPrice8',
        'Sell9Price': 'AskPrice9',
        'Sell10Price': 'AskPrice10',
        'Buy1OrderQty': 'BidVolume1',
        'Buy2OrderQty': 'BidVolume2',
        'Buy3OrderQty': 'BidVolume3',
        'Buy4OrderQty': 'BidVolume4',
        'Buy5OrderQty': 'BidVolume5',
        'Buy6OrderQty': 'BidVolume6',
        'Buy7OrderQty': 'BidVolume7',
        'Buy8OrderQty': 'BidVolume8',
        'Buy9OrderQty': 'BidVolume9',
        'Buy10OrderQty': 'BidVolume10',
        'Sell1OrderQty': 'AskVolume1',
        'Sell2OrderQty': 'AskVolume2',
        'Sell3OrderQty': 'AskVolume3',
        'Sell4OrderQty': 'AskVolume4',
        'Sell5OrderQty': 'AskVolume5',
        'Sell6OrderQty': 'AskVolume6',
        'Sell7OrderQty': 'AskVolume7',
        'Sell8OrderQty': 'AskVolume8',
        'Sell9OrderQty': 'AskVolume9',
        'Sell10OrderQty': 'AskVolume10',
    }
    for item in items:
        tick_data[items[item]] = np.load(f'{address}/{item}/{code}{date}.npy')
    return tick_data