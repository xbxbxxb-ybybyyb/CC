import datetime
import os
import numpy as np
import pandas as pd
import shutil
# import xquant_data
import importlib
import multiprocessing
import sys
import json
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from xquant.factordata import FactorData
s = FactorData()
from arrow.naming_config import *

import logging
import concurrent.futures
from skimage.util import view_as_windows
from multifactor.utility import dt as udt

from xquant.marketdata import MarketData

config_dict = {
#     'arrow_universe_root': '/data/user/000072/share/for_wsc/arrow/trade_sample/',
    'arrow_universe_root': '/data/user/000072/LYM_STOCKS/arrow_prod/data/',
    'daily_data_root': '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5',
} 


def format_datetime(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')


def get_minute_data_helper(ticker, date):
    mdp = MarketData()
    df = mdp.get_data_by_date("Kline1M4ZT", ticker, date, ["2", "3"], sort_by_receive_time=True)
    del(mdp)
    df['dt'] = df.apply(lambda x: format_datetime(x.MDDate, x.MDTime), axis=1)
    df = df[['dt', 'HTSCSecurityID', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'TotalVolumeTrade', 'TotalValueTrade']]
    df.columns = ['dt', 'Ticker', 'open', 'close', 'high', 'low', 'volume', 'amount']
    df = df.set_index('dt')
    return df


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    else:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding


class VoidLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    lazy_mode=False, void_flag=False):
    if void_flag:  # multiprocessing dummy
        return VoidLogger()
    logger = logging.getLogger(name)
    if lazy_mode:
        return logger
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.DEBUG)
    if file_name is not None:
        if not logger.hasHandlers():
            _dirname = os.path.dirname(file_name)
            if len(_dirname) != 0 and not os.path.exists(_dirname):
                os.makedirs(_dirname)
            file_handler = logging.FileHandler(file_name, mode=mode)
            file_handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(file_handler)
    else:
        if not logger.hasHandlers():
            # default to screen
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(stream_handler)
    return logger


def concurrent_apply_func(func, input_list, max_workers, logger=None, debug_mode=False,
                          process_type='multiprocess', logger_callback=None,
                          collect_results=True, void_log_flag=False, **kwargs):
    # apply func to input list as first argument in a concurrent way
    assert callable(func)
    assert isinstance(max_workers, int)
    assert isinstance(input_list, list) or isinstance(input_list, tuple)
    total_jobs = len(input_list)
    result_collector = dict()
    if process_type == 'multithread':
        _executor = concurrent.futures.ThreadPoolExecutor
    elif process_type == 'multiprocess':
        _executor = concurrent.futures.ProcessPoolExecutor
    else:
        raise NotImplementedError
    if logger is None:
        logger = add_file_logger('concurrent', void_flag=void_log_flag)  # dummy logger to stream to screen
    if debug_mode:
        # pdb into func source code should work
        for _file in input_list:
            data = func(_file, **kwargs)
            if data is not None and collect_results:
                result_collector[_file] = data
    else:
        with _executor(max_workers=max_workers) as executor:
            future_dict = {executor.submit(func, _file, **kwargs): _file for _file in input_list}
            logger.info('executor submit finish')
            for _future in concurrent.futures.as_completed(future_dict):
                _file = future_dict[_future]
                current_job = input_list.index(_file) + 1
                try:
                    data = _future.result()
                except Exception as _exp:
                    logger.warning(f'worker raised {_exp}, the input is {_file}')
                    data = None
                del future_dict[_future]
                del _future
                # load results into collector
                if data is not None and collect_results:
                    try:
                        result_collector[_file] = data
                    except TypeError:
                        result_collector[pd.Timestamp.now()] = data
                if logger_callback is not None:
                    assert callable(logger_callback)
                    msg = logger_callback(_file, data)
                    if data is not None:
                        logger.info('%d/%d - %s' % (current_job, total_jobs, msg))
                    else:
                        logger.warning('%d/%d - %s' % (current_job, total_jobs, msg))
                else:
                    # logger.info('%d/%d - processed' % (current_job, total_jobs))
                    pass
        logger.info('executor finished')
    if collect_results:
        return result_collector


# 盘中任意n分钟出现幅度超过m的急跌
def func_1(data, rolling_window=60, amplitude_threshold=1.08):
    data_close = data['close'].fillna(method='ffill').fillna(method='bfill').fillna(0).values
    temp_array_exp = rolling_window_upgrade(data_close, rolling_window)
    con_1 = (np.nanmax(temp_array_exp, axis=-1) / np.nanmin(temp_array_exp, axis=-1) > amplitude_threshold)
    con_2 = (np.nanargmax(temp_array_exp, axis=-1) - np.nanargmin(temp_array_exp, axis=-1) < 0)
    result = {data['Ticker'][0]: np.nansum(con_1 & con_2, axis=0)}
    return result


# 尾盘异动
def func_2(data):
    close_price = data['close'].iloc[-1]
    low_tail = data['low'].between_time('14:50', '15:00').min()
    result = {data['Ticker'][0]: close_price / low_tail - 1}
    return result


# 尾盘开板
def func_3(data):
    # 该函数仅限于universe_1，因为只有该universe满足全天的high==limit
    limit_price = data['high'].max()
    high_tail = data['high'].between_time('14:50', '15:00').max()
    result = {data['Ticker'][0]: limit_price == high_tail}
    return result

def get_final_data_lastday(date, max_workers=24):
    date = udt.str_date_parser(date)
    last_date = udt.get_trading_day_offset(date, -1)[0]
    day_before_yesterday = udt.get_trading_day_offset(date, -2)[0]
    last_date_60 = udt.get_trading_day_offset(date, -60)[0]
    arrow_universe = pd.DataFrame(pd.read_pickle(os.path.join(
        config_dict['arrow_universe_root'], date.strftime('%Y%m%d'), 'universe/stock_universe.pkl'))).loc[date]
    daily_data_ld = IO.read_data(last_date, alt=config_dict['daily_data_root']).loc[last_date]
    daily_data_dby = IO.read_data(day_before_yesterday, alt=config_dict['daily_data_root']).loc[day_before_yesterday]
    daily_data_for_risk = IO.read_data([last_date_60, last_date], alt=config_dict['daily_data_root'])
    daily_data_for_risk_close = daily_data_for_risk['S_DQ_CLOSE'].unstack()
    daily_data_for_risk_open = daily_data_for_risk['S_DQ_OPEN'].unstack()
    daily_data_for_risk_adjfactor = daily_data_for_risk['S_DQ_ADJFACTOR'].unstack()
    daily_data_amount_60 = daily_data_for_risk['S_DQ_AMOUNT'].unstack()
    tickers_used = arrow_universe.index.intersection(daily_data_ld.index).intersection(daily_data_dby.index).intersection(daily_data_for_risk_close.columns)
    daily_data_ld = daily_data_ld.loc[tickers_used]
    daily_data_dby = daily_data_dby.loc[tickers_used]
    daily_data_for_risk_close = daily_data_for_risk_close[tickers_used]
    daily_data_for_risk_open = daily_data_for_risk_open[tickers_used]
    daily_data_for_risk_adjfactor = daily_data_for_risk_adjfactor[tickers_used]
    daily_data_amount_60 = daily_data_amount_60[tickers_used]
    daily_data_for_risk_adjclose = daily_data_for_risk_close * daily_data_for_risk_adjfactor
    # minute_data_dict = concurrent_apply_func(get_minute_data_helper, tickers_used.tolist(), max_workers,
    #                                          date=last_date.strftime('%Y%m%d'))
    if max_workers > 1:
        minute_data_dict = concurrent_apply_func(get_minute_data_helper, tickers_used.tolist(), max_workers,
                                             date=last_date.strftime('%Y%m%d'))
    else:
        minute_data_dict = {}
        for kk in tickers_used.tolist():
            minute_data_dict[kk] = get_minute_data_helper(kk, date=last_date.strftime('%Y%m%d'))
    result_df = arrow_universe.loc[tickers_used]
    result_df['last_day_amount_ratio'] = daily_data_ld['S_DQ_AMOUNT'] / daily_data_dby['S_DQ_AMOUNT']
    result_df['last_day_close_to_open'] = daily_data_ld['S_DQ_CLOSE'] / daily_data_ld['S_DQ_OPEN'] - 1
    result_df['last_day_close_to_preclose'] = daily_data_ld['S_DQ_CLOSE'] / daily_data_ld['S_DQ_PRECLOSE'] - 1
    result_df['last_day_open_to_preclose'] = daily_data_ld['S_DQ_OPEN'] / daily_data_ld['S_DQ_PRECLOSE'] - 1
    result_df['last_day_high_to_open'] = daily_data_ld['S_DQ_HIGH'] / daily_data_ld['S_DQ_OPEN'] - 1
    result_df['last_day_high_to_close'] = daily_data_ld['S_DQ_HIGH'] / daily_data_ld['S_DQ_CLOSE'] - 1
    result_df['last_day_xyx'] = np.minimum(daily_data_ld['S_DQ_OPEN'], daily_data_ld['S_DQ_CLOSE']) / daily_data_ld[
        'S_DQ_LOW'] - 1
    result_df['last_day_tail5_ll'] = pd.Series(
        {k: v for d in [func_3(i) for i in minute_data_dict.values()] for k, v in d.items()})
    result_df['dby_high_to_low'] = daily_data_dby['S_DQ_HIGH'] / daily_data_dby['S_DQ_LOW'] - 1
    result_df['amount'] = daily_data_ld['S_DQ_AMOUNT'] * 1000  # 这份日频数据的成交额有个乘数
    result_df['last_day_rolling_60min_drawdown'] = pd.Series(
        {k: v for d in [func_1(i) for i in minute_data_dict.values()] for k, v in d.items()})
    result_df['last_day_tail10_close_to_low'] = pd.Series(
        {k: v for d in [func_2(i) for i in minute_data_dict.values()] for k, v in d.items()})
    result_df['adjclose_dby'] = (daily_data_for_risk_adjclose).iloc[-2]
    result_df['adjclose_ma10'] = daily_data_for_risk_adjclose.tail(10).mean()
    result_df['adjclose_ma20'] = daily_data_for_risk_adjclose.tail(20).mean()
    result_df['adjclose_ma60'] = daily_data_for_risk_adjclose.tail(60).mean()
    result_df['adjfactor'] = daily_data_for_risk_adjfactor.iloc[-1]
    result_df['last_day_close'] = daily_data_for_risk_close.iloc[-1]
    result_df['amount_5_to_20'] = daily_data_amount_60.iloc[-7:-2].mean() / daily_data_amount_60.iloc[-27:-7].mean()
    result_df['amount_1_to_5'] = daily_data_amount_60.iloc[-1] / daily_data_amount_60.iloc[-7:-2].mean()
    result_df['close_to_open_5d'] = (daily_data_for_risk_close.iloc[-5:] < daily_data_for_risk_open.iloc[-5:]).sum()

    return result_df

# def get_final_data_lastday(date, max_workers=1):
#     date = udt.str_date_parser(date)
#     last_date = udt.get_trading_day_offset(date, -1)[0]
#     day_before_yesterday = udt.get_trading_day_offset(date, -2)[0]
#     arrow_universe = pd.read_pickle(universe_path).loc[date]
#     daily_data_ld = IO.read_data(last_date, alt=eod_path).loc[last_date]
#     daily_data_dby = IO.read_data(day_before_yesterday, alt=eod_path).loc[day_before_yesterday]
#     tickers_used = arrow_universe.index.intersection(daily_data_ld.index).intersection(daily_data_dby.index)
#     daily_data_ld = daily_data_ld.loc[tickers_used]
#     daily_data_dby = daily_data_dby.loc[tickers_used]
#     if max_workers > 1:
#         minute_data_dict = concurrent_apply_func(get_minute_data_helper, tickers_used.tolist(), max_workers,
#                                              date=last_date.strftime('%Y%m%d'))
#     else:
#         minute_data_dict = {}
#         for kk in tickers_used.tolist():
#             minute_data_dict[kk] = get_minute_data_helper(kk, date=last_date.strftime('%Y%m%d'))
#     result_df = arrow_universe.loc[tickers_used]
#     result_df['last_day_amount_ratio'] = daily_data_ld['S_DQ_AMOUNT'] / daily_data_dby['S_DQ_AMOUNT']
#     result_df['last_day_close_to_open'] = daily_data_ld['S_DQ_CLOSE'] / daily_data_ld['S_DQ_OPEN'] - 1
#     result_df['last_day_high_to_open'] = daily_data_ld['S_DQ_HIGH'] / daily_data_ld['S_DQ_OPEN'] - 1
#     result_df['last_day_high_to_close'] = daily_data_ld['S_DQ_HIGH'] / daily_data_ld['S_DQ_CLOSE'] - 1
#     result_df['last_day_xyx'] = np.minimum(daily_data_ld['S_DQ_OPEN'], daily_data_ld['S_DQ_CLOSE']) / daily_data_ld[
#         'S_DQ_LOW'] - 1
#     result_df['last_day_tail5_ll'] = pd.Series(
#         {k: v for d in [func_3(i) for i in minute_data_dict.values()] for k, v in d.items()})
#     result_df['dby_high_to_low'] = daily_data_dby['S_DQ_HIGH'] / daily_data_dby['S_DQ_LOW'] - 1
#     result_df['amount'] = daily_data_ld['S_DQ_AMOUNT'] * 1000  # 这份日频数据的成交额有个乘数
#     result_df['last_day_rolling_60min_drawdown'] = pd.Series(
#         {k: v for d in [func_1(i) for i in minute_data_dict.values()] for k, v in d.items()})
#     result_df['last_day_tail10_close_to_low'] = pd.Series(
#         {k: v for d in [func_2(i) for i in minute_data_dict.values()] for k, v in d.items()})
#     return result_df


   
# final_data_lastday = get_final_data_lastday(pd.Timestamp(today), max_workers=24)
# final_data_lastday.to_pickle(config_dict['arrow_universe_root'] + today + '/rule_blacklist_df.pkl')