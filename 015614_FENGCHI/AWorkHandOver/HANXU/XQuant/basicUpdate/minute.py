import sys
sys.path.append('/data/group/800442/800319/')

import os
import pandas as pd
import numpy as np
import datetime as dt
import multiprocessing
from tqdm import tqdm
from xquant.thirdpartydata.marketdata import MarketData as Market3Data
from xquant.marketdata import MarketData
from xquant.factordata import FactorData
from dataApi.tradeDate import get_recent_trade_date, trade_minutes, get_date_range, get_desample_minute_panel, get_trade_date_interval
from dataApi.stockList import trans_int2windcode, trans_windcode2int, _update_log
from basicUpdate.daily import update_morning_data
from xquant.xqutils.helper import multicore_init

multicore_init()
fd = FactorData()
m3d = Market3Data()

benchmarks = {'000300.SH': 'HS300', '000905.SH': 'ZZ500', '000906.SH': 'ZZ800','000001.SH': 'SZZZ', '399001.SZ': 'SZCZ',
              '000852.SH': 'ZZ1000', '000016.SH': 'SZ50', '399101.SZ': 'ZXBZ', '399102.SZ': 'CYBZ'}

minute_base_data_list = ['open', 'high', 'low', 'close', 'vol', 'amt', 'deal']

def _forward_fill(arr, axis, zero_fill=True):

    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None, ) * x + (slice(None), ) + (None, ) * (idx.ndim - x - 1)]
                    for x in range(idx.ndim - 1)) + (idx, )]
    out = out.swapaxes(axis, -1)
    return out

def multiprocess(lines, func, iterable, *args):

    pool = multiprocessing.Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // lines
    remainder = len(iterable) % lines
    iter_start = 0
    for j in range(lines):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder -= 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter, ) + args)
        iter_start = iter_end
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

def _error_check(new, old, factor_type, factor, accept_error=0., file='/data/group/800442/800319/junkData/updateLog.txt'):

    _new = new.iloc[0].dropna().sort_index()
    _old = old.iloc[-1].dropna().sort_index()
    if _new.name != _old.name:
        _update_log('ERROR', factor_type, factor, 'update', 'Time confusion')
        return 2
    else:
        error_ratio = abs(len(_new) - len(_old)) / len(_new)
        _old = _old.reindex(_new.index)
        try:
            close_num = np.isclose(_old, _new).sum()
        except TypeError:
            close_num = (_old == _new).sum()
        error_ratio += abs(len(_new) - close_num) / len(_new)
        if error_ratio > accept_error:
            _update_log('ERROR', factor_type, factor, 'update',
                        'Error ratio %.4f%% exceeds accept level %.4f%%' % (error_ratio * 100, accept_error * 100),
                        file=file)
            return 1
        else:
            _update_log('SUCCEED', factor_type, factor, 'update', file=file)
            return 0

def _clean_kline(df):

    start_date = df['date'].min()
    end_date = df['date'].max()
    trade_dates = sorted(list(set(get_date_range(start_date, end_date)) & set(df['date'].drop_duplicates())))
    index = pd.merge(pd.Series(1, index=trade_dates, name='key').reset_index().rename(columns={'index':'date'}),
                     pd.Series(1, index=trade_minutes, name='key').reset_index().rename(columns={'index':'time'}),
                     on='key', how='outer').set_index(['date', 'time']).index
    _df = df.set_index(['date', 'time']).reindex(index)
    _df.loc[_df['close'] == 0, :] = np.nan
    _df = _df.reset_index()
    return _df

def _get_short_kline(code, start_date, end_date):

    md = MarketData()
    end_date = str(int(end_date))
    start_date = str(int(start_date))
    df = md.get_data_by_time_frame(
        table_type='KLINE1M4ZT',
        security_id=code,
        start_time_str=start_date + ' 090000000',
        end_time_str=end_date + ' 160000000',
        trading_phase_code = [],
        sort_by_receive_time=False,
    )
    if len(df) == 0:
        return pd.DataFrame(columns=['date', 'time', 'open', 'high', 'low', 'close', 'deal', 'vol', 'amt'])
    else:
        df = df[['MDDate', 'MDTime', 'OpenPx', 'HighPx', 'LowPx', 'ClosePx',
                 'NumTrades', 'TotalVolumeTrade', 'TotalValueTrade']]
        df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'deal', 'vol', 'amt']
        return df

def _get_short_kline2(code, start_date, end_date):

    end_date = str(int(end_date))
    start_date = str(int(start_date))
    df = m3d.getKLine4ZTDataFrame(
        htscSecurityID=code,
        startDateTime=start_date + '090000000',
        endDateTime=end_date + '160000000',
        ePlaybackExrightsType = 10,
        eMarketDataType=20,
    )
    if len(df) == 0:
        return pd.DataFrame(columns=['date', 'time', 'open', 'high', 'low', 'close', 'vol', 'amt', 'deal'])
    else:
        df = df[['MDDate', 'MDTime', 'OpenPx', 'HighPx', 'LowPx', 'ClosePx',
                 'TotalVolumeTrade', 'TotalValueTrade', 'NumTrades']]
        df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'vol', 'amt', 'deal']
        return df

def _get_short_bench_kline(code, start_date, end_date):

    end_date = str(int(end_date))
    start_date = str(int(start_date))
    df = m3d.getKLine4ZTDataFrame(
        htscSecurityID=code,
        startDateTime=start_date + '090000000',
        endDateTime=end_date + '160000000',
        ePlaybackExrightsType = 10,
        eMarketDataType=20,
    )
    if len(df) == 0:
        return pd.DataFrame(columns=['date', 'time', 'open', 'high', 'low', 'close', 'vol', 'amt'])
    else:
        df = df[['MDDate', 'MDTime', 'OpenPx', 'HighPx', 'LowPx', 'ClosePx', 'TotalVolumeTrade', 'TotalValueTrade']]
        df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'vol', 'amt']
        return df

def _get_long_kline(code, start_date=20130101, end_date=None):

    if end_date is None:
        end_date = get_recent_trade_date(dividing_point=15)

    _temp_start = start_date
    _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(start_date), '%Y%m%d') + dt.timedelta(60), '%Y%m%d'))

    df = pd.DataFrame()
    while _temp_end < end_date:
        temp_df = _get_short_kline(code, _temp_start, _temp_end)
        df = df.append(temp_df, ignore_index=True)
        _temp_start = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_end), '%Y%m%d')
                                               + dt.timedelta(1), '%Y%m%d'))
        _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_start), '%Y%m%d')
                                               + dt.timedelta(60), '%Y%m%d'))
    temp_df = _get_short_kline(code, _temp_start, end_date)
    df = df.append(temp_df, ignore_index=True)
    if len(df) != 0:
        df['time'] = df['time'].map(lambda x: int(x[:4]))
        df['date'] = df['date'].map(int)
        df[['open', 'high', 'low', 'close', 'deal', 'vol', 'amt']] = \
            df[['open', 'high', 'low', 'close', 'deal', 'vol', 'amt']].applymap(float)
        df = _clean_kline(df).convert_objects()
    return df

def _get_long_kline2(code, start_date=20130101, end_date=None):

    if end_date is None:
        end_date = get_recent_trade_date(dividing_point=15)

    _temp_start = start_date
    _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(start_date), '%Y%m%d') + dt.timedelta(30), '%Y%m%d'))

    df = pd.DataFrame()
    while _temp_end < end_date:
        temp_df = _get_short_bench_kline(code, _temp_start, _temp_end)
        df = df.append(temp_df, ignore_index=True)
        _temp_start = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_end), '%Y%m%d')
                                               + dt.timedelta(1), '%Y%m%d'))
        _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_start), '%Y%m%d')
                                               + dt.timedelta(30), '%Y%m%d'))
    temp_df = _get_short_kline(code, _temp_start, end_date)
    df = df.append(temp_df, ignore_index=True)
    df['time'] = df['time'].map(lambda x: int(x[:4]))
    df['date'] = df['date'].map(int)
    df[['open', 'high', 'low', 'close', 'vol', 'amt', 'deal']] = \
        df[['open', 'high', 'low', 'close', 'vol', 'amt', 'deal']].applymap(float)
    df = _clean_kline(df).convert_objects()
    return df

def _get_long_bench_kline(code, start_date=20100101, end_date=None):

    if end_date is None:
        end_date = get_recent_trade_date(dividing_point=15)

    _temp_start = start_date
    _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(start_date), '%Y%m%d') + dt.timedelta(30), '%Y%m%d'))

    df = pd.DataFrame()
    while _temp_end < end_date:
        temp_df = _get_short_bench_kline(code, _temp_start, _temp_end)
        df = df.append(temp_df, ignore_index=True)
        _temp_start = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_end), '%Y%m%d')
                                               + dt.timedelta(1), '%Y%m%d'))
        _temp_end = int(dt.datetime.strftime(dt.datetime.strptime(str(_temp_start), '%Y%m%d')
                                               + dt.timedelta(30), '%Y%m%d'))
    temp_df = _get_short_bench_kline(code, _temp_start, end_date)
    df = df.append(temp_df, ignore_index=True)
    df['time'] = df['time'].map(lambda x: int(x[:4]))
    df['date'] = df['date'].map(int)
    df[['open', 'high', 'low', 'close', 'vol', 'amt']] = \
        df[['open', 'high', 'low', 'close', 'vol', 'amt']].applymap(float)
    df = _clean_kline(df).convert_objects()
    return df

def _prepare_store_kline_by_stock(code_list, start_date=20130101, end_date=None,
                                  store_address='/data/group/800442/800319/junkData/minuteByStock'):


    for code in tqdm(code_list):
        df = _get_long_kline(code, start_date, end_date)
        df = df.drop_duplicates(subset=['date', 'time'], keep='last')
        if len(df) == 0:
            continue
        _code = trans_windcode2int(code)
        try:
            os.remove('%s/%s.h5' % (store_address, _code))
        except:
            pass
        df.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t')

def _prepare_store_kline_by_factor(code_list, factor, data_address='/data/group/800442/800319/junkData/minuteByStock'):

    df = pd.DataFrame()
    for code in tqdm(code_list):
        temp = pd.read_hdf('%s/%s.h5' % (data_address, code), code,
                           columns=['date', 'time', factor]).set_index(['date', 'time'])
        temp.columns = [int(code) if code.isdigit() else code]
        df = pd.concat([df, temp], axis=1)
    return df

def _store_kline_by_stock(code_list=None, line=8, start_date=20130101, end_date=None,
                          stock_list_address='/data/group/800442/800319/junkData/daily',
                          store_address='/data/group/800442/800319/junkData/minuteByStock'):

    if code_list == None:
        _code_list = pd.read_hdf('%s/stock_list.h5' % stock_list_address, 'stock_list', start=-1).columns.to_list()
    elif isinstance(code_list, int):
        _code_list = [code_list]
    elif isinstance(code_list, list):
        _code_list = code_list
    else:
        raise TypeError("code_list type must be int, list or None")
    _code_list = [trans_int2windcode(x) for x in _code_list]

    if line <= 1:
        _prepare_store_kline_by_stock(_code_list, start_date, end_date, store_address)
    else:
        multiprocess(line, _prepare_store_kline_by_stock, _code_list, start_date, end_date, store_address)

def _store_kline_by_stock_bench(bench_dict=benchmarks, start_date=20100101, end_date=None,
                                  store_address='/data/group/800442/800319/junkData/minuteByStockBench'):

    for code in tqdm(bench_dict.keys()):
        df = _get_long_bench_kline(code, start_date, end_date)
        if len(df) == 0:
            continue
        _code = bench_dict[code]
        df.to_hdf('%s/%s.h5' % (store_address, _code), _code, format='t')

def _store_kline_by_factor_bench(line=8, factors=minute_base_data_list,
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):

    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum', 'deal':'sum'}

    code_list = [x[:-3] for x in os.listdir(data_address)]
    for factor in factors:
        if line <= 1:
            df = _prepare_store_kline_by_factor(code_list, factor, data_address)
            df = df.convert_objects()
        else:
            df = multiprocess(line, _prepare_store_kline_by_factor, code_list, factor, data_address)
            df = pd.concat([df[x].get() for x in df.keys()], axis=1)
            df = df.convert_objects()

        for period in [5, 15, 30]:
            _df = get_desample_minute_panel(df, period, factor_desample_method_dict[factor])
            _df.to_hdf('%s/%s_%sm.h5' % (desample_address, factor, period), '%s_%sm' % (factor, period), format='t')

        df.to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t')
        _update_log('SUCCEED', 'minuteByFactor', factor, 'store')


def _store_kline_by_factor(line=24, pre_close_address='/data/group/800442/800319/junkData/daily',
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):

    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum', 'deal':'sum'}
    factors = ['vol', 'amt', 'deal', 'open', 'high', 'low', 'close']

    code_list = [x[:-3] for x in os.listdir(data_address)]
    pre_close = pd.read_hdf('%s/pre_close.h5' % pre_close_address, 'pre_close')
    if pre_close.index[-1] != get_recent_trade_date():
        _update_log('ERROR', 'daily', 'pre_close', 'store', 'New data has not arrived')
        raise Exception("New data has not arrived")

    for factor in factors:
        if line <= 1:
            df = _prepare_store_kline_by_factor(code_list, factor, data_address)

        else:
            df = multiprocess(line, _prepare_store_kline_by_factor, code_list, factor, data_address)
            df = pd.concat([df[x].get() for x in df.keys()], axis=1)

        df = df.sort_index(axis=1)
        index = df.index
        columns = df.columns
        df = df.values.reshape(df.shape[0] // 242, 242, df.shape[1])

        if factor == 'vol':
            pre_close = pre_close.reindex(index=sorted(set(index.get_level_values(0))), columns=columns)
            pre_close = pre_close.values[:, None, :].repeat(242, axis=1)

        if factor in ['vol', 'amt', 'deal']:
            df[np.isfinite(pre_close) & ~ np.isfinite(df)] = 0

        if factor == 'vol':
            zero_opn = df[:, 0, :] == 0

        if factor in ['open', 'high', 'low', 'close']:
            df.transpose(1, 0, 2)[0, zero_opn] = pre_close.transpose(1, 0, 2)[0, zero_opn]
            df = _forward_fill(df, axis=1, zero_fill=False)

        df = pd.DataFrame(df.reshape(df.shape[0] * 242, df.shape[2]), index=index, columns=columns).convert_objects()

        for period in [5, 15, 30]:
            _df = get_desample_minute_panel(df, period, factor_desample_method_dict[factor])
            _df.to_hdf('%s/%s_%sm.h5' % (desample_address, factor, period), '%s_%sm' % (factor, period), format='t')

        df.to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t')
        _update_log('SUCCEED', 'minuteByFactor', factor, 'store')

def update_adjfactor_kline_by_factor2(factors=minute_base_data_list[:4],
                           data_address='/data/group/800442/800319/junkData/minuteByFactor',
                           adjfactor_address='/data/group/800442/800319/junkData/daily',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):

    adjfactor = pd.read_hdf('%s/adjfactor.h5' % adjfactor_address, 'adjfactor').loc[20130104:]
    if adjfactor.index[-1] != get_recent_trade_date():
        _update_log('ERROR', 'daily', 'adjfactor', 'update', 'New data has not arrived')
        raise Exception("New data has not arrived")
    factor_desample_method_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    for factor in factors:
        df = pd.read_hdf('%s/%s.h5' % (data_address, factor), factor)
        if df.index[-1][0] != get_recent_trade_date():
            _update_log('ERROR', 'minute', factor, 'update', 'New data has not arrived')
            raise Exception("New data has not arrived")
        adjfactor1 = adjfactor.reindex(columns=df.columns)
        df1 = df.values.reshape(df.shape[0] // 242, 242, df.shape[1]).swapaxes(0, 1) * adjfactor1.values
        df1 = df1.swapaxes(0, 1).reshape(df1.shape[1] * 242, df1.shape[2])
        df1 = pd.DataFrame(df1, index=df.index, columns=df.columns)
        df1.to_hdf('%s/%s_badj.h5' % (data_address, factor), '%s_badj' % factor, format='t')
        for period in [5, 15, 30]:
            df2 = get_desample_minute_panel(df1, period, factor_desample_method_dict[factor])
            df2.to_hdf('%s/%s_badj_%sm.h5' % (desample_address, factor, period), '%s_badj_%sm' %
                       (factor, period), format='t')
        _update_log('SUCCEED', 'minuteByAdjFactor', factor, 'update')

def update_adjfactor_kline_by_factor(factors=minute_base_data_list[:4],
                           data_address='/data/group/800442/800319/junkData/minuteByFactor',
                           adjfactor_address='/data/group/800442/800319/junkData/daily',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):

    adjfactor = pd.read_hdf('%s/adjfactor.h5' % adjfactor_address, 'adjfactor')
    if adjfactor.index[-1] != get_recent_trade_date():
        _update_log('ERROR', 'daily', 'adjfactor', 'update', 'New data has not arrived')
        raise Exception("New data has not arrived")
    factor_desample_method_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    for factor in factors:
        df1 = pd.read_hdf('%s/%s_badj.h5' % (data_address, factor), '%s_badj' % factor, start=-1)
        days = len(get_date_range(df1.index[0][0], get_recent_trade_date())) - 1
        if days <= 0:
            continue
        df = pd.read_hdf('%s/%s.h5' % (data_address, factor), factor, start=-242 * days)
        adjfactor1 = adjfactor.iloc[-days:].reindex(columns=df.columns)
        if df.index[-1][0] != get_recent_trade_date():
            _update_log('ERROR', 'minute', factor, 'update', 'New data has not arrived')
            raise Exception("New data has not arrived")
        df1 = df.values.reshape(df.shape[0] // 242, 242, df.shape[1]).swapaxes(0, 1) * adjfactor1.values
        df1 = df1.swapaxes(0, 1).reshape(df1.shape[1] * 242, df1.shape[2])
        df1 = pd.DataFrame(df1, index=df.index, columns=df.columns)
        df1.to_hdf('%s/%s_badj.h5' % (data_address, factor), '%s_badj' % factor, format='t', append=True)
        for period in [5, 15, 30]:
            df2 = get_desample_minute_panel(df1, period, factor_desample_method_dict[factor])
            df2.to_hdf('%s/%s_badj_%sm.h5' % (desample_address, factor, period),
                       '%s_badj_%sm' % (factor, period), format='t', append=True)
        _update_log('SUCCEED', 'minuteByAdjFactor', factor, 'update')

def _prepare_update_kline_by_stock(code_list, end_date, store_address='/data/group/800442/800319/junkData/minuteByStock'):

    for code in tqdm(code_list):
        _code = trans_windcode2int(code)
        try:
            old = pd.read_hdf('%s/%s.h5' % (store_address, _code), str(_code), start=-242)
        except FileNotFoundError:
            start_date = end_date
            old_found = False
        else:
            start_date = old.iloc[-1, 0]
            old_found = True

        new = _get_long_kline(code, start_date, end_date)

        if len(new) == 0:
            continue

        if start_date < new.iloc[-1, 0] < end_date:
            _update_log('ERROR', 'minuteByStock', code, 'update', 'New data has not arrived Or PAUSE')

        if old_found:
            error_ratio = 1 - np.isclose(new.iloc[:242], old, equal_nan=True).sum().sum() / 2178
            if error_ratio >= 1 / 2178:
                _update_log('ERROR', 'minuteByStock', code, 'update',
                            'Error ratio %.4f%% exceeds accept level 0.0000%%' % (error_ratio * 100))
                old = pd.read_hdf('%s/%s.h5' % (store_address, _code), str(_code))
                df = pd.concat([old.iloc[:-242], new]).convert_objects()
                df.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t')
            else:
                df = new.iloc[242:]
                if len(df) != 0:
                    df.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t', append=True)
        else:
            new.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t')

def _prepare_update_kline_by_factor(code_list, factor, update_minutes, update_date_list,
                                    data_address='/data/group/800442/800319/junkData/minuteByStock'):


    df = pd.DataFrame()

    for code in tqdm(code_list):
        try:
            temp = pd.read_hdf('%s/%s.h5' % (data_address, code), code,
                               columns=['date', 'time', factor], start=-update_minutes)
            temp = temp.loc[temp['date'].isin(update_date_list)].set_index(['date', 'time'])
            temp.columns = [int(code) if code.isdigit() else code]
            df = pd.concat([df, temp], axis=1)
        except:
            print(code)
    return df

def update_kline_by_stock(line=8, stock_list_address='/data/group/800442/800319/junkData/daily',
                          store_address='/data/group/800442/800319/junkData/minuteByStock'):

    end_date = get_recent_trade_date(dividing_point=15)

    _code_list = pd.read_hdf('%s/stock_list.h5' % stock_list_address, 'stock_list', start=-1).columns.to_list()
    _code_list = [trans_int2windcode(x) for x in _code_list]

    if line <= 1:
        _prepare_update_kline_by_stock(_code_list, end_date, store_address)
    else:
        multiprocess(line, _prepare_update_kline_by_stock, _code_list, end_date, store_address)

def update_kline_by_stock_bench(bench_dict=benchmarks, store_address='/data/group/800442/800319/junkData/minuteByStockBench'):

    end_date = get_recent_trade_date()
    for code in tqdm(bench_dict.keys()):

        _code = bench_dict[code]
        old = pd.read_hdf('%s/%s.h5' % (store_address, _code), str(_code), start=-242)
        start_date = old.iloc[-1, 0]
        new = _get_long_bench_kline(code, start_date, end_date)

        if new.iloc[-1, 0] < end_date:
            _update_log('ERROR', 'minuteByStockBench', _code, 'update', 'New data has not arrived')

        error_ratio = 1 - np.isclose(new.iloc[:242], old, equal_nan=True).sum().sum() / 1936
        if error_ratio >= 1 / 2178:
            _update_log('ERROR', 'minuteByStockBench', _code, 'update',
                        'Error ratio %.4f%% exceeds accept level 0.0000%%' % (error_ratio * 100))
            old = pd.read_hdf('%s/%s.h5' % (store_address, _code), str(_code))
            df = pd.concat([old.iloc[:-242], new.iloc[242:]]).convert_objects()
            df.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t')
        else:
            df = new.iloc[242:]
            if len(df) != 0:
                df.to_hdf('%s/%s.h5' % (store_address, _code), str(_code), format='t', append=True)


def update_kline_by_factor3(line=8, factors=minute_base_data_list,
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):


    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum', 'deal':'sum'}
    code_list = [x[:-3] for x in os.listdir(data_address)]
    for factor in factors:
        old = pd.read_hdf('%s/%s.h5' % (store_address, factor), factor)
        start_date = old.index.get_level_values(0)[-1]
        end_date = get_recent_trade_date()
        update_date_list = get_date_range(start_date, end_date)
        update_minutes = len(update_date_list) * 242
        if line <= 1:
            new = _prepare_update_kline_by_factor(code_list, factor, update_minutes, update_date_list, data_address)
        else:
            new = multiprocess(line, _prepare_update_kline_by_factor,
                              code_list, factor, update_minutes, update_date_list, data_address)
            new = pd.concat([new[x].get() for x in new.keys()], axis=1)
        new = new.convert_objects()

        _old = old.iloc[-242:].sort_index(axis=1).reset_index().dropna(how='all', axis=1)
        _new = new.iloc[:242].sort_index(axis=1).reset_index().dropna(how='all', axis=1)
        _old = _old.reindex_like(_new)
        error_ratio = 1 - np.isclose(_old, _new, equal_nan=True).sum().sum() / (len(_old) * len(_old.T))

        if error_ratio >= 1e-6:
            _update_log('ERROR', 'minuteByFactor', factor, 'update',
                        'Error ratio %.4f%% exceeds accept level 0.0000%%' % (error_ratio * 100))

        df = pd.concat([old.iloc[:-242], new]).convert_objects()
        df.to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t')

        for period in [5, 15, 30]:
            _df = get_desample_minute_panel(df, period, factor_desample_method_dict[factor])
            _df.to_hdf('%s/%s_%sm.h5' % (desample_address, factor, period), '%s_%sm' % (factor, period), format='t')
        _update_log('SUCCEED', 'minuteDesample', 'All', 'update')

def update_kline_by_factor_bench(line=8, factors=minute_base_data_list,
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):


    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum', 'deal':'sum'}
    code_list = [x[:-3] for x in os.listdir(data_address)]
    for factor in factors:
        old = pd.read_hdf('%s/%s.h5' % (store_address, factor), factor, start=-1)
        start_date = old.index.get_level_values(0)[-1]
        end_date = get_recent_trade_date()
        update_date_list = get_date_range(start_date, end_date)
        update_minutes = len(update_date_list) * 242
        if line <= 1:
            new = _prepare_update_kline_by_factor(code_list, factor, update_minutes, update_date_list, data_address)
        else:
            new = multiprocess(line, _prepare_update_kline_by_factor,
                              code_list, factor, update_minutes, update_date_list, data_address)
            new = pd.concat([new[x].get() for x in new.keys()], axis=1)
        new = new.reindex(columns=old.columns).convert_objects()

        new.iloc[242:].to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t', append=True)

        for period in [5, 15, 30]:
            _df = get_desample_minute_panel(new.iloc[242:], period, factor_desample_method_dict[factor])
            _df.to_hdf('%s/%s_%sm.h5' % (desample_address, factor, period),
                       '%s_%sm' % (factor, period), format='t', append=True)
        _update_log('SUCCEED', 'minuteDesample', 'All', 'update')

def update_kline_by_factor(line=24, pre_close_address='/data/group/800442/800319/junkData/daily',
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor'):


    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum', 'deal':'sum'}
    code_list = [x[:-3] for x in os.listdir(data_address)]
    pre_close = pd.read_hdf('%s/pre_close.h5' % pre_close_address, 'pre_close')
    if pre_close.index[-1] != get_recent_trade_date():
        _update_log('ERROR', 'daily', 'pre_close', 'update', 'New data has not arrived')
        raise Exception("New data has not arrived")

    factors = ['vol', 'amt', 'deal', 'open', 'high', 'low', 'close']

    for factor in factors:
        old = pd.read_hdf('%s/%s.h5' % (store_address, factor), factor, start=-1)
        start_date = old.index.get_level_values(0)[-1]
        end_date = get_recent_trade_date()
        update_date_list = get_date_range(start_date, end_date)
        update_date_num = len(update_date_list)
        update_minutes = update_date_num * 242
        update_code_num = len(old.columns)
        pre_close1 = pre_close.loc[update_date_list].reindex(columns=old.columns).values
        pre_close1 = pre_close1[:, None, :].repeat(242, axis=1)

        if line <= 1:
            new = _prepare_update_kline_by_factor(code_list, factor, update_minutes, update_date_list, data_address)
        else:
            new = multiprocess(line, _prepare_update_kline_by_factor,
                               code_list, factor, update_minutes, update_date_list, data_address)
            new = pd.concat([new[x].get() for x in new.keys()], axis=1)

        new = new.reindex(columns=old.columns)

        if factor in ['vol', 'amt', 'deal']:
            new = new.fillna(0)

        arr = new.values.reshape(update_date_num, 242, update_code_num)

        if factor == 'vol':
            zero_opn = arr[:, 0, :] == 0

        if factor in ['open', 'high', 'low', 'close']:
            arr.transpose(1, 0, 2)[0, zero_opn] = pre_close1.transpose(1, 0, 2)[0, zero_opn]
            arr = _forward_fill(arr, axis=1, zero_fill=False)
        else:
            arr[~ np.isfinite(pre_close1)] = np.nan

        new = pd.DataFrame(arr.reshape(new.shape), index=new.index, columns=new.columns)
        new = new.convert_objects()
        new.iloc[242:].to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t', append=True)

        for period in [5, 15, 30]:
            _df = get_desample_minute_panel(new.iloc[242:], period, factor_desample_method_dict[factor])
            _df.to_hdf('%s/%s_%sm.h5' % (desample_address, factor, period),
                       '%s_%sm' % (factor, period), format='t', append=True)
        _update_log('SUCCEED', 'minuteDesample', 'All', 'update')

def get_bench_daily_data(data_address='/data/group/800442/800319/junkData/minuteByFactorBench',
                         store_address='/data/group/800442/800319/junkData/dailyBench'):

    factor_desample_method_dict = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                                   'amt':'sum', 'vol':'sum'}
    factor_list = [x[:-3] for x in os.listdir(data_address)]
    for factor in factor_list:
        df = pd.read_hdf('%s/%s.h5' % (data_address, factor), factor)
        _df = get_desample_minute_panel(df, 240, factor_desample_method_dict[factor])
        _df.index = _df.index.droplevel(-1)
        _df.to_hdf('%s/%s.h5' % (store_address, factor), factor, format='t')
    _update_log('SUCCEED', 'dailyBench', 'All', 'update')

def store_twap(data_address='/data/group/800442/800319/junkData/minuteByFactor',
               store_address='/data/group/800442/800319/junkData/daily'):

    df = pd.read_hdf('%s/close.h5' % data_address, 'close').reset_index()
    df = df[~df['time'].isin((925, 1457, 1458, 1459, 1500))].drop('time', axis=1)
    df = df.groupby('date').mean()
    df.to_hdf('%s/twap.h5' % store_address, 'twap', format='t')
    _update_log('SUCCEED', 'daily', 'twap', 'update')

def update_twap(base_date=20130101, data_address='/data/group/800442/800319/junkData/minuteByFactor',
                store_address='/data/group/800442/800319/junkData/daily'):

    twap = pd.read_hdf('%s/twap.h5' % store_address, 'twap', start=-1)
    df = pd.read_hdf('%s/close.h5' % data_address, 'close', start=get_trade_date_interval(
        twap.index[0], base_date=base_date) * 242).reset_index()
    df = df[~df['time'].isin((925, 1457, 1458, 1459, 1500))].drop('time', axis=1)
    df = df.groupby('date').mean()
    check = _error_check(df, twap, 'daily', 'twap')
    if check == 0:
        df.iloc[1:].to_hdf('%s/twap.h5' % store_address, 'twap', format='t', append='True')
    elif check == 1:
        store_twap(data_address, store_address)
    elif check == 2:
        raise Exception("New data has not arrived.")

if __name__ == '__main__':
    '''
    _store_kline_by_stock(line=16, end_date=20200120, store_address='/data/group/800442/800319/junkData/minuteByStock')
    _store_kline_by_stock_bench(store_address='/data/group/800442/800319/junkData/minuteByStockBench')
    _store_kline_by_factor(line=24, factors=minute_base_data_list,
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor')
    _store_kline_by_factor(factors=minute_base_data_list[:-1],
                           data_address='/data/group/800442/800319/junkData/minuteByStockBench',
                           store_address='/data/group/800442/800319/junkData/minuteByFactorBench')
    '''
    update_kline_by_stock(line=48, store_address='/data/group/800442/800319/junkData/minuteByStock')
    update_kline_by_stock_bench(store_address='/data/group/800442/800319/junkData/minuteByStockBench')
    update_kline_by_factor(line=48, pre_close_address='/data/group/800442/800319/junkData/daily',
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor')
    update_kline_by_factor_bench(line=1, factors=minute_base_data_list[:-1],
                           data_address='/data/group/800442/800319/junkData/minuteByStockBench',
                           store_address='/data/group/800442/800319/junkData/minuteByFactorBench',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactorBench')
    get_bench_daily_data()
    update_twap(base_date=20100101, data_address='/data/group/800442/800319/junkData/minuteByFactorBench',
                store_address='/data/group/800442/800319/junkData/dailyBench')
    update_twap(base_date=20130101, data_address='/data/group/800442/800319/junkData/minuteByFactor',
                store_address='/data/group/800442/800319/junkData/daily')
    update_adjfactor_kline_by_factor()

    _store_kline_by_factor(line=30)
    #_store_kline_by_factor(factors=minute_base_data_list[:-1],
    #                       data_address='/data/group/800442/800319/junkData/minuteByStockBench',
    #                       store_address='/data/group/800442/800319/junkData/minuteByFactorBench')


    #update_kline_by_factor2(line=30)

    ###
    _store_kline_by_stock(line=48)
    _store_kline_by_stock_bench()
    _store_kline_by_factor(line=30, pre_close_address='/data/group/800442/800319/junkData',
                           data_address='/data/group/800442/800319/junkData/minuteByStock',
                           store_address='/data/group/800442/800319/junkData/minuteByFactor',
                           desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactor')
    get_bench_daily_data()

    update_adjfactor_kline_by_factor2()
    store_twap()


    _store_kline_by_stock_bench(bench_dict=benchmarks, start_date=20100101, end_date=None,
                                store_address='/data/group/800442/800319/junkData/minuteByStockBench')
    _store_kline_by_factor_bench(line=8, factors=minute_base_data_list[:-1],
                                 data_address='/data/group/800442/800319/junkData/minuteByStockBench',
                                 store_address='/data/group/800442/800319/junkData/minuteByFactorBench',
                                 desample_address='/data/group/800442/800319/junkData/minuteDesampleByFactorBench')
    get_bench_daily_data()

    #update_kline_by_factor2(line=20)
