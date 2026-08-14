import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import time
from multiprocessing import Pool

import os
import gc
import numpy as np
import pandas as pd
from xquant.marketdata import MarketData
from xquant.xqutils.helper import multicore_init

from dataApi.getData import get_daily_1factor
from dataApi.stockList import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range
from dataApi import aimr
from decimal import Decimal

multicore_init()

open_ticks = [
    91500, 91503, 91506, 91509, 91512, 91515, 91518, 91521, 91524, 91527, 91530, 91533, 91536, 91539, 91542, 91545,
    91548, 91551, 91554, 91557, 91600, 91603, 91606, 91609, 91612, 91615, 91618, 91621, 91624, 91627, 91630, 91633,
    91636, 91639, 91642, 91645, 91648, 91651, 91654, 91657, 91700, 91703, 91706, 91709, 91712, 91715, 91718, 91721,
    91724, 91727, 91730, 91733, 91736, 91739, 91742, 91745, 91748, 91751, 91754, 91757, 91800, 91803, 91806, 91809,
    91812, 91815, 91818, 91821, 91824, 91827, 91830, 91833, 91836, 91839, 91842, 91845, 91848, 91851, 91854, 91857,
    91900, 91903, 91906, 91909, 91912, 91915, 91918, 91921, 91924, 91927, 91930, 91933, 91936, 91939, 91942, 91945,
    91948, 91951, 91954, 91957, 92000, 92003, 92006, 92009, 92012, 92015, 92018, 92021, 92024, 92027, 92030, 92033,
    92036, 92039, 92042, 92045, 92048, 92051, 92054, 92057, 92100, 92103, 92106, 92109, 92112, 92115, 92118, 92121,
    92124, 92127, 92130, 92133, 92136, 92139, 92142, 92145, 92148, 92151, 92154, 92157, 92200, 92203, 92206, 92209,
    92212, 92215, 92218, 92221, 92224, 92227, 92230, 92233, 92236, 92239, 92242, 92245, 92248, 92251, 92254, 92257,
    92300, 92303, 92306, 92309, 92312, 92315, 92318, 92321, 92324, 92327, 92330, 92333, 92336, 92339, 92342, 92345,
    92348, 92351, 92354, 92357, 92400, 92403, 92406, 92409, 92412, 92415, 92418, 92421, 92424, 92427, 92430, 92433,
    92436, 92439, 92442, 92445, 92448, 92451, 92454, 92457, 92500]


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


def store_date_code(path):
    stock_list = get_daily_1factor('stock_list').loc[20130101:].replace(
        False, np.nan).stack().reset_index().groupby('level_0')['level_1'].apply(list).to_dict()
    for date in stock_list.keys():
        pd.to_pickle(stock_list[date], f'{path}/{date}.pkl')


def prepare_auction_folds(root_path):
    sub_folds = ['date', 'tick', 'tick1', 'tick2', 'finish_tag', 'error', 'factor']
    for s in sub_folds:
        if not os.path.exists(f'{root_path}/{s}/'):
            os.makedirs(f'{root_path}/{s}/')
            if s == 'date':
                store_date_code(f'{root_path}/{s}/')


def get_numpy_head(shape, dtype='float32'):
    head = [
        147, 78, 85, 77, 80, 89, 1, 0, 118, 0, 123, 39, 100, 101, 115, 99, 114, 39, 58, 32,
        39, 60, 102, 56, 39, 44, 32, 39, 102, 111, 114, 116, 114, 97, 110, 95, 111, 114, 100, 101,
        114, 39, 58, 32, 70, 97, 108, 115, 101, 44, 32, 39, 115, 104, 97, 112, 101, 39, 58, 32,
        40, 41, 44, 32, 125, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 10
    ]
    dtype_dict = {
        'bool': [124, 98, 49],
        'int8': [124, 105, 49],
        'int16': [60, 105, 50],
        'int32': [60, 105, 52],
        'int64': [60, 105, 56],
        'float32': [60, 102, 52],
        'float64': [60, 102, 56]
    }
    shape_map = {
        '0': 48,
        '1': 49,
        '2': 50,
        '3': 51,
        '4': 52,
        '5': 53,
        '6': 54,
        '7': 55,
        '8': 56,
        '9': 57,
        ',': 44,
        ' ': 32
    }
    shape_value = [shape_map[x] for x in str(shape)[1: -1]] + [41, 44, 32, 125]
    head[21: 24] = dtype_dict[dtype]
    head[61: 61 + len(shape_value)] = shape_value
    return head


def calc_auction_mdd(pre_close, price_arr, mup=False):
    arr = np.r_[pre_close, price_arr]
    if not mup:
        cumm = np.maximum.accumulate(arr)
        dd = 1 - arr / cumm
        mdd_len = dd.argmax()
        mdd = dd[mdd_len]
        mdd_len -= arr[:mdd_len].argmax() if mdd_len else 0
    else:
        cumm = np.minimum.accumulate(arr)
        dd = arr / cumm - 1
        mdd_len = dd.argmax()
        mdd = dd[mdd_len]
        mdd_len -= arr[:mdd_len].argmin() if mdd_len else 0
    return mdd, mdd_len


def clean_tick_auction_data(md, date, code):
    pre_close = get_daily_1factor('pre_close', [date], [code]).iloc[0, 0]
    limit_range = get_daily_1factor('limit_range', [date], [code]).iloc[0, 0]
    free_float_shares = get_daily_1factor('free_float_shares', [get_pre_trade_date(date)], [code]).iloc[0, 0] * 1e4
    limit_max = float(round(Decimal(str(pre_close * (1 + limit_range))), 2))
    limit_min = float(round(Decimal(str(pre_close * (1 - limit_range))), 2))
    code = trans_int2windcode(code)
    date = str(date)
    tick = md.get_data_by_date('Stock', code, date, trading_phase_code=['1', '2'])
    if len(tick) == 0:
        return tick, None, None
    tick['PreClosePx'] = pre_close
    tick['MaxPx'] = limit_max if np.isfinite(limit_max) | (tick['MaxPx'].iloc[-1] == 0) else tick['MaxPx'].iloc[-1]
    tick['MinPx'] = limit_min if np.isfinite(limit_min) | (tick['MinPx'].iloc[-1] == 0) else tick['MinPx'].iloc[-1]
    tick['FreeFloatShares'] = free_float_shares
    tick1 = tick.loc[(tick['TotalBidQty'] + tick['TotalOfferQty'] + tick['TotalVolumeTrade'] == 0) & (
            tick['TradingPhaseCode'] == '1') & (tick['Buy1Price'] > 0), [
                         'MDTime', 'ReceiveDateTime', 'PreClosePx', 'MaxPx', 'MinPx',
                         'Buy1Price', 'Buy1OrderQty', 'Buy2OrderQty', 'Sell2OrderQty', 'FreeFloatShares']]
    tick1_missing = len(tick1) == 0
    try:
        tick2 = tick.loc[(tick['TotalBidQty'] + tick['TotalOfferQty'] + tick['TotalVolumeTrade'] > 0)].iloc[[0]]
    except IndexError:
        return tick, None, None
    tick1['MDTime'] = tick1['MDTime'].map(int).map(lambda x: open_ticks[x] * 1000 if x in range(201) else x)
    tick1.loc[tick1['MDTime'] == 91500000, 'MDTime'] = 91500001
    tick1 = tick1[tick1['MDTime'] > 91500000]
    tick1['ReceiveDateTime'] %= 1000000000
    tick1['MDTime'] = (np.round(tick1['MDTime'] / 1000) * 1000).map(int)
    tick1['ReceiveDateTime'] = np.fmax(tick1['ReceiveDateTime'] - tick1['MDTime'], 0)
    tick1['MDTime'] //= 1000
    tick1.rename(columns={'ReceiveDateTime': 'DelayTime'}, inplace=True)
    tick1.set_index('MDTime', inplace=True)
    tick1 = tick1[~ tick1.index.duplicated(keep='last')]
    tick1.loc[tick1['Buy1Price'] == 0, 'Buy1Price'] = np.nan
    tick1 = tick1.reindex(sorted(list(set(open_ticks) | set(tick1.index)))).ffill().loc[open_ticks]
    tick1.iloc[-2] = tick1.iloc[-1]
    tick1 = tick1.iloc[1:-1]

    start_nan = np.isnan(tick1['Buy1Price'].values).sum()
    tick1.iloc[:start_nan, 1] = pre_close
    tick1.iloc[:start_nan, 2] = limit_max
    tick1.iloc[:start_nan, 3] = limit_min
    tick1.iloc[:start_nan, 8] = free_float_shares
    if ~ ((tick2['TotalVolumeTrade'].iloc[0] > 0) & tick1_missing):
        tick1.iloc[:start_nan, 0] = 0
        tick1.iloc[:start_nan, 5] = 0
        tick1.iloc[:start_nan, 6] = 0
        tick1.iloc[:start_nan, 7] = 0
        tick1.iloc[:start_nan, 4] = pre_close

    tick2['ReceiveDateTime'] = (tick2['ReceiveDateTime'] % 1000000000 - 92500000) / 1000
    tick2.rename(columns={'ReceiveDateTime': 'DelayTime'}, inplace=True)
    tick2.eval('MainBidQty = Buy1OrderQty + Buy2OrderQty + Buy3OrderQty + Buy4OrderQty + Buy5OrderQty + '
               'Buy6OrderQty + Buy7OrderQty + Buy8OrderQty + Buy9OrderQty + Buy10OrderQty', inplace=True)
    tick2.eval('MainOfferQty = Sell1OrderQty + Sell2OrderQty + Sell3OrderQty + Sell4OrderQty + Sell5OrderQty + '
               'Sell6OrderQty + Sell7OrderQty + Sell8OrderQty + Sell9OrderQty + Sell10OrderQty', inplace=True)
    tick2.eval('WeightedAvgMainBidPx = (Buy1OrderQty * Buy1Price + Buy2OrderQty * Buy2Price + '
               'Buy3OrderQty * Buy3Price + Buy4OrderQty * Buy4Price + Buy5OrderQty * Buy5Price + '
               'Buy6OrderQty * Buy6Price + Buy7OrderQty * Buy7Price + Buy8OrderQty * Buy8Price + '
               'Buy9OrderQty * Buy9Price + Buy10OrderQty * Buy10Price) / MainBidQty', inplace=True)
    tick2.eval('WeightedAvgMainOfferPx = (Sell1OrderQty * Sell1Price + Sell2OrderQty * Sell2Price + '
               'Sell3OrderQty * Sell3Price + Sell4OrderQty * Sell4Price + Sell5OrderQty * Sell5Price + '
               'Sell6OrderQty * Sell6Price + Sell7OrderQty * Sell7Price + Sell8OrderQty * Sell8Price + '
               'Sell9OrderQty * Sell9Price + Sell10OrderQty * Sell10Price) / MainOfferQty', inplace=True)
    tick2.loc[tick2['MainBidQty'] == 0, 'WeightedAvgMainBidPx'] = pre_close
    tick2.loc[tick2['MainOfferQty'] == 0, 'WeightedAvgMainOfferPx'] = pre_close
    tick2.loc[tick2['TotalBidQty'] == 0, 'WeightedAvgBidPx'] = pre_close
    tick2.loc[tick2['TotalOfferQty'] == 0, 'WeightedAvgOfferPx'] = pre_close
    tick2 = tick2.iloc[0]
    if tick2['MainBidQty'] > tick2['TotalBidQty']:
        tick2['TotalBidQty'] = np.nan
        tick2['WeightedAvgBidPx'] = np.nan
    if tick2['MainOfferQty'] > tick2['TotalOfferQty']:
        tick2['TotalOfferQty'] = np.nan
        tick2['WeightedAvgOfferPx'] = np.nan
    tick2 = tick2[[
        'MDTime',
        'DelayTime',
        'PreClosePx',
        'FreeFloatShares',
        'NumTrades',
        'TotalVolumeTrade',
        'TotalValueTrade',
        'LastPx',
        'DiffPx1',
        'DiffPx2',
        'MaxPx',
        'MinPx',
        'TotalBidQty',
        'TotalOfferQty',
        'WeightedAvgBidPx',
        'WeightedAvgOfferPx',
        'MainBidQty',
        'MainOfferQty',
        'WeightedAvgMainBidPx',
        'WeightedAvgMainOfferPx',
        'Buy1Price',
        'Buy1OrderQty',
        'Buy1NumOrders',
        'Buy1NoOrders',
        'Buy1OrderDetail',
        'Sell1Price',
        'Sell1OrderQty',
        'Sell1NumOrders',
        'Sell1NoOrders',
        'Sell1OrderDetail',
        'Buy2Price',
        'Buy2OrderQty',
        'Buy2NumOrders',
        'Sell2Price',
        'Sell2OrderQty',
        'Sell2NumOrders',
        'Buy3Price',
        'Buy3OrderQty',
        'Buy3NumOrders',
        'Sell3Price',
        'Sell3OrderQty',
        'Sell3NumOrders',
        'Buy4Price',
        'Buy4OrderQty',
        'Buy4NumOrders',
        'Sell4Price',
        'Sell4OrderQty',
        'Sell4NumOrders',
        'Buy5Price',
        'Buy5OrderQty',
        'Buy5NumOrders',
        'Sell5Price',
        'Sell5OrderQty',
        'Sell5NumOrders',
        'Buy6Price',
        'Buy6OrderQty',
        'Buy6NumOrders',
        'Sell6Price',
        'Sell6OrderQty',
        'Sell6NumOrders',
        'Buy7Price',
        'Buy7OrderQty',
        'Buy7NumOrders',
        'Sell7Price',
        'Sell7OrderQty',
        'Sell7NumOrders',
        'Buy8Price',
        'Buy8OrderQty',
        'Buy8NumOrders',
        'Sell8Price',
        'Sell8OrderQty',
        'Sell8NumOrders',
        'Buy9Price',
        'Buy9OrderQty',
        'Buy9NumOrders',
        'Sell9Price',
        'Sell9OrderQty',
        'Sell9NumOrders',
        'Buy10Price',
        'Buy10OrderQty',
        'Buy10NumOrders',
        'Sell10Price',
        'Sell10OrderQty',
        'Sell10NumOrders',
    ]]
    return tick, tick1, tick2


def calc_auction_factor(date, code, tick1, tick2):
    PreClosePx = tick1['PreClosePx'].iloc[0]
    free_float_shares = tick1['FreeFloatShares'].iloc[0]
    MaxPx = tick1['MaxPx'].iloc[0]
    MinPx = tick1['MinPx'].iloc[0]
    Buy1Price = tick1['Buy1Price'].values
    Buy1OrderQty = tick1['Buy1OrderQty'].values
    Buy2OrderQty = tick1['Buy2OrderQty'].values
    Sell2OrderQty = tick1['Sell2OrderQty'].values
    delay_sec = tick1.iloc[-1, 0] / 1000
    TenderPct = Buy1Price / PreClosePx - 1
    BuyVol = Buy1OrderQty + Buy2OrderQty
    BuyAmt = Buy1Price * BuyVol
    SellVol = Buy1OrderQty + Sell2OrderQty
    SellAmt = Buy1Price * SellVol
    DiffVol = Buy2OrderQty - Sell2OrderQty
    DiffAmt = Buy1Price * DiffVol

    T_tender_pct_mean = TenderPct.mean()
    T_tender_pct_std = TenderPct.std(ddof=1)
    T_tender_max_up = Buy1Price.max() / PreClosePx - 1
    T_tender_max_down = 1 - Buy1Price.min() / PreClosePx

    T_tender_mup, T_tender_mup_len = calc_auction_mdd(PreClosePx, Buy1Price, True)
    T_tender_mdd, T_tender_mdd_len = calc_auction_mdd(PreClosePx, Buy1Price, False)
    T_tender_bid_amt_max_down = (np.maximum.accumulate(BuyAmt) - BuyAmt).max()
    T_tender_ask_amt_max_down = (np.maximum.accumulate(SellAmt) - SellAmt).max()
    T_tender_bid_ff_rate_down = (np.maximum.accumulate(BuyVol) - BuyVol).max() / free_float_shares
    T_tender_ask_ff_rate_down = (np.maximum.accumulate(SellVol) - SellVol).max() / free_float_shares

    T_tender_bidask_amt_mean = DiffAmt.mean()
    T_tender_bidask_amt_std = DiffAmt.std(ddof=1)
    T_tender_bidask_ff_rate_mean = DiffVol.mean() / free_float_shares
    T_tender_bidask_ff_rate_std = DiffVol.std(ddof=1) / free_float_shares
    T_tender_bidupask_rate = (Buy2OrderQty > Sell2OrderQty).mean()

    delay_sec2 = tick2['DelayTime']
    T_tender_bid_ff_rate = (tick2['TotalVolumeTrade'] + (tick2['Buy1Price'] == tick2['LastPx']) *
                            tick2['Buy1OrderQty']) / free_float_shares
    T_tender_ask_ff_rate = (tick2['TotalVolumeTrade'] + (tick2['Sell1Price'] == tick2['LastPx']) *
                            tick2['Sell1OrderQty']) / free_float_shares
    T_tender_bidmask_ff_rate = T_tender_bid_ff_rate - T_tender_ask_ff_rate
    T_tender_bidmask_amt = ((tick2['Buy1Price'] == tick2['LastPx']) * tick2['Buy1OrderQty'] - (
            tick2['Sell1Price'] == tick2['LastPx']) * tick2['Sell1OrderQty']) * tick2['LastPx']

    T_open_bid_amt = tick2['TotalBidQty'] * tick2['WeightedAvgBidPx']
    T_open_ask_amt = tick2['TotalOfferQty'] * tick2['WeightedAvgOfferPx']
    T_open_bidask_amt = T_open_bid_amt - T_open_ask_amt
    T_open_bid_ff_rate = tick2['TotalBidQty'] / free_float_shares
    T_open_ask_ff_rate = tick2['TotalOfferQty'] / free_float_shares
    T_open_bidask_ff_rate = T_open_bid_ff_rate - T_open_ask_ff_rate
    T_open_bidivask = T_open_bid_ff_rate / T_open_ask_ff_rate
    T_open_pct_bid2c = tick2['WeightedAvgBidPx'] / tick2['PreClosePx'] - 1
    T_open_pct_ask2c = tick2['WeightedAvgOfferPx'] / tick2['PreClosePx'] - 1
    T_open_pct_bidask = T_open_pct_bid2c - T_open_pct_ask2c

    T_open_main_bid_amt = tick2['MainBidQty'] * tick2['WeightedAvgMainBidPx']
    T_open_main_ask_amt = tick2['MainOfferQty'] * tick2['WeightedAvgMainOfferPx']
    T_open_main_bidask_amt = T_open_main_bid_amt - T_open_main_ask_amt
    T_open_main_bid_ff_rate = tick2['MainBidQty'] / free_float_shares
    T_open_main_ask_ff_rate = tick2['MainOfferQty'] / free_float_shares
    T_open_main_bidask_ff_rate = T_open_main_bid_ff_rate - T_open_main_ask_ff_rate
    T_open_main_bidivask = T_open_main_bid_ff_rate / T_open_main_ask_ff_rate
    T_open_main_pct_bid2c = tick2['WeightedAvgMainBidPx'] / tick2['PreClosePx'] - 1
    T_open_main_pct_ask2c = tick2['WeightedAvgMainOfferPx'] / tick2['PreClosePx'] - 1
    T_open_main_pct_bidask = T_open_main_pct_bid2c - T_open_main_pct_ask2c

    # 海通证券-短周期交易策略研究之一：基于集合竞价分时走势的A股T+0策略-190714
    T_open_pct = tick2['LastPx'] / tick2['PreClosePx'] - 1 if tick2['LastPx'] else 0
    T_open_amt = tick2['TotalValueTrade']
    T_auc1_pct = Buy1Price[99] / PreClosePx - 1
    T_auc2_pct = tick2['LastPx'] / Buy1Price[99] - 1 if tick2['LastPx'] else 0
    T_auc1_climitup = np.cumprod(Buy1Price[:100][::-1] == MaxPx).mean()
    T_auc1_climitdown = np.cumprod(Buy1Price[:100][::-1] == MinPx).mean()
    T_auc1_limitup = (Buy1Price[:100] == MaxPx).mean()
    T_auc1_limitdown = (Buy1Price[:100] == MinPx).mean()

    T_auc2_climitup = np.cumprod(Buy1Price[100:][::-1] == MaxPx).mean()
    T_auc2_climitdown = np.cumprod(Buy1Price[100:][::-1] == MinPx).mean()
    T_auc2_limitup = (Buy1Price[100:] == MaxPx).mean()
    T_auc2_limitdown = (Buy1Price[100:] == MinPx).mean()

    T_auc_climitup = np.cumprod(Buy1Price[::-1] == MaxPx).mean()
    T_auc_climitdown = np.cumprod(Buy1Price[::-1] == MinPx).mean()
    T_auc_limitup = (Buy1Price == MaxPx).mean()
    T_auc_limitdown = (Buy1Price == MinPx).mean()

    T_auc1_upnum = (Buy1Price[1:100] > Buy1Price[:99]).mean()
    T_auc1_downnum = (Buy1Price[1:100] < Buy1Price[:99]).mean()
    T_auc1_updownnum = (T_auc1_upnum - T_auc1_downnum) / (T_auc1_upnum + T_auc1_downnum)
    T_auc1_updownnum = 0 if np.isnan(T_auc1_updownnum) else T_auc1_updownnum

    T_auc2_upnum = (Buy1Price[100:] > Buy1Price[99:-1]).mean()
    T_auc2_downnum = (Buy1Price[100:] < Buy1Price[99:-1]).mean()
    T_auc2_updownnum = (T_auc2_upnum - T_auc2_downnum) / (T_auc2_upnum + T_auc2_downnum)
    T_auc2_updownnum = 0 if np.isnan(T_auc2_updownnum) else T_auc2_updownnum

    T_auc_upnum = (Buy1Price[1:] > Buy1Price[:-1]).mean()
    T_auc_downnum = (Buy1Price[1:] < Buy1Price[:-1]).mean()
    T_auc_updownnum = (T_auc_upnum - T_auc_downnum) / (T_auc_upnum + T_auc_downnum)
    T_auc_updownnum = 0 if np.isnan(T_auc_updownnum) else T_auc_updownnum

    factor = np.array([
        date, code, delay_sec, T_tender_pct_mean, T_tender_pct_std, T_tender_max_up, T_tender_max_down, T_tender_mup,
        T_tender_mup_len, T_tender_mdd, T_tender_mdd_len, T_tender_bid_amt_max_down, T_tender_ask_amt_max_down,
        T_tender_bid_ff_rate_down, T_tender_ask_ff_rate_down, T_tender_bidask_amt_mean, T_tender_bidask_amt_std,
        T_tender_bidask_ff_rate_mean, T_tender_bidask_ff_rate_std, T_tender_bidupask_rate, delay_sec2,
        T_tender_bid_ff_rate, T_tender_ask_ff_rate, T_tender_bidmask_ff_rate, T_tender_bidmask_amt, T_open_bid_amt,
        T_open_ask_amt, T_open_bidask_amt, T_open_bid_ff_rate, T_open_ask_ff_rate, T_open_bidask_ff_rate,
        T_open_bidivask, T_open_pct_bid2c, T_open_pct_ask2c, T_open_pct_bidask, T_open_main_bid_amt,
        T_open_main_ask_amt, T_open_main_bidask_amt, T_open_main_bid_ff_rate, T_open_main_ask_ff_rate,
        T_open_main_bidask_ff_rate, T_open_main_bidivask, T_open_main_pct_bid2c, T_open_main_pct_ask2c,
        T_open_main_pct_bidask, T_open_pct, T_open_amt, T_auc1_pct, T_auc2_pct, T_auc1_climitup, T_auc1_climitdown,
        T_auc1_limitup, T_auc1_limitdown, T_auc2_climitup, T_auc2_climitdown, T_auc2_limitup, T_auc2_limitdown,
        T_auc_climitup, T_auc_climitdown, T_auc_limitup, T_auc_limitdown, T_auc1_upnum, T_auc1_downnum,
        T_auc1_updownnum,
        T_auc2_upnum, T_auc2_downnum, T_auc2_updownnum, T_auc_upnum, T_auc_downnum, T_auc_updownnum
    ], dtype='float64')
    return factor


def _func2(date_idx):
    date = date_list[date_idx]
    # if os.path.exists(f'{root_path}/finish_tag/{date}.pkl'):
    #     return
    code_list = pd.read_pickle(f'{root_path}/date/{date}.pkl')
    head = get_numpy_head((len(code_list), 70), dtype='float64')
    fp = np.memmap(f'{root_path}/factor/{date}.npy',
                   dtype='uint8', mode='w+', offset=0, shape=128)
    fp[:] = head
    del fp
    md = MarketData()
    for j, code in enumerate(code_list):
        # print(time.strftime('%Y-%m-%d %H:%M:%S'), j, date, code)
        try:
            tick, tick1, tick2 = clean_tick_auction_data(md, date, code)
            if tick1 is None:
                continue
            factor = calc_auction_factor(date, code, tick1, tick2)
        except:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), 'error', date, code)
            pd.to_pickle(0, f'{root_path}/error/{date}_{code}.pkl')
            continue
        pd.to_pickle(tick, f'{root_path}/tick/{date}_{code}.pkl')
        pd.to_pickle(tick1, f'{root_path}/tick1/{date}_{code}.pkl')
        pd.to_pickle(tick2, f'{root_path}/tick2/{date}_{code}.pkl')
        fp = np.memmap(f'{root_path}/factor/{date}.npy',
                       dtype='float64', mode='r+', offset=128 + j * 70 * 8, shape=70)
        fp[:] = factor
        del fp
        del tick1, tick2, factor
        gc.collect()
    pd.to_pickle(0, f'{root_path}/finish_tag/{date}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), date)


if __name__ == '__main__':
    from dataApi.sendInfo import send_message

    root_path = '/arch1/user/015614/LimitUpStrategy/'
    prepare_auction_folds(root_path)
    date_list = get_date_range(20130104, 20211123)  # 2160
    # error_list1 = sorted(list(set(int(x[:-4].split('_')[0]) for x in os.listdir(f'{root_path}/error/'))))
    error_list1 = [20160721,
 20160812,
 20160908,
 20160913,
 20160930,
 20170306,
 20170320,
 20170323,
 20170329,
 20170517,
 20170922,
 20190104,
 20190107,
 20190109,
 20190114,
 20190115,
 20190116,
 20190117,
 20190118,
 20190122,
 20190123,
 20190124,
 20190125,
 20190128,
 20190130,
 20190131,
 20190212,
 20190213,
 20190214,
 20190215,
 20190219,
 20190220,
 20190221,
 20190222,
 20190225,
 20190226,
 20190227,
 20190228,
 20190301,
 20190304,
 20190306,
 20190307,
 20190308,
 20190311,
 20190314,
 20190315,
 20190320,
 20190321,
 20190325,
 20190326,
 20190329,
 20190401,
 20190402,
 20190403,
 20190404,
 20190408,
 20190409,
 20190411,
 20190415,
 20190416,
 20190417,
 20190419,
 20190424,
 20190426,
 20190429,
 20190430,
 20190506,
 20190507,
 20190508,
 20190509,
 20190514,
 20190515,
 20190516,
 20190517,
 20190520,
 20190521,
 20190522,
 20190524,
 20190527,
 20190528,
 20190530,
 20190531,
 20190605,
 20210729] #84
    # finish_date_list = sorted([int(x[:-4]) for x in os.listdir('/arch1/user/015836/LimitUpStrategy/finish_tag/')])
    # unfinished_date_list = sorted(list(set(date_list) - set(finish_date_list)))
    idx = int(aimr.getParam())  # 2156
    _func2(date_list.index(error_list1[idx]))
