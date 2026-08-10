import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from overnight.naming_config import *
import functools
import dill
import re
import bottleneck as bk
import json
import sched, time
import logging
import sys
from multifactor.data.utils import *

def scheduler(func, target_trigger_time, delay=0):
    # init func at given time with delay as in milliseconds
    assert isinstance(target_trigger_time, pd.Timedelta)
    assert callable(func)
    target_trigger_time = (pd.Timestamp(pd.Timestamp.now().date()) + target_trigger_time).to_pydatetime().timestamp() + delay / 1000
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(target_trigger_time, 0, func)
    s.run(blocking=True)


def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data


def dump_json(path, value):
    with open(path, 'w') as fout:
        json.dump(value, fout, indent=4)


def get_constituent_stock_list(date):
    wdf = IO.read_data(date, ftype=FType.INDEXWEIGHT, dsource=DSource.CSI)
    zz500_stock_list = wdf[wdf['index_weight_zz500'] > 0].index.get_level_values(1).tolist()
    hs300_stock_list = wdf[wdf['index_weight_hs300'] > 0].index.get_level_values(1).tolist()
    sh50_stock_list = wdf[wdf['index_weight_sh50'] > 0].index.get_level_values(1).tolist()
    zz800_stock_list = zz500_stock_list + hs300_stock_list
    zz800_stock_list.sort()
    return zz500_stock_list, hs300_stock_list, zz800_stock_list, sh50_stock_list


@functools.lru_cache(maxsize=None)
def ticker_match(ticker_num):
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

@functools.lru_cache(maxsize=None)
def get_stock_data_per_date(ref_date):
    ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')
    stk_full_mins_data = pd.read_pickle(os.path.join(stock_minute_per_date_path, ref_date + '.pkl'), compression='gzip').reset_index()
    stk_full_mins_data['Ticker'] = stk_full_mins_data.Ticker.map(ticker_match)
    stk_full_mins_data['dt'] = stk_full_mins_data['dt'] * 1E6 + stk_full_mins_data['minute'] * 100
    stk_full_mins_data['dt'] = pd.to_datetime(stk_full_mins_data['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    stk_full_mins_data = stk_full_mins_data.drop(['minute'], axis = 1)
    stk_full_mins_data = stk_full_mins_data.rename(columns = {'amt':'amount'}).set_index(['dt','Ticker']).sort_index()
    return stk_full_mins_data

def update_stock_multitime_data(ref_date = None):
    if ref_date is None:
        _, ref_date, _ = check_update_date()
    ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')
    stk_full_mins_data = pd.read_pickle(os.path.join(stock_minute_per_date_path, ref_date + '.pkl'), compression='gzip').reset_index()
    stk_full_mins_data = stk_full_mins_data[stk_full_mins_data.minute.isin([1449,1439,1429,1419,1409,1359])]
    stk_full_mins_data['Ticker'] = stk_full_mins_data.Ticker.map(ticker_match)
    stk_full_mins_data['dt'] = stk_full_mins_data['dt'] * 1E6 + stk_full_mins_data['minute'] * 100
    stk_full_mins_data['dt'] = pd.to_datetime(stk_full_mins_data['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    stk_full_mins_data = stk_full_mins_data[['dt','Ticker','close']].set_index(['dt','Ticker']).sort_index()
    IO.pd_hdf5_writer(stk_full_mins_data, stock_close_multitime_path, dataset='stock_close_multitime', append = True)

def get_trade_contract(start_date, end_date, prod_id, exp_day_num=2):
    pd_data_daily = IO.read_data([start_date, end_date], dtype=DType.FUTURES, h5root=private_root)
    IC_daily = pd_data_daily[pd_data_daily.PROD_ID == prod_id]
    df00 = IC_daily.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
    df01 = IC_daily.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
    df00 = df00.rename(columns = {x:x+'_00' for x in df00.columns.tolist()})
    df01 = df01.rename(columns = {x:x+'_01' for x in df01.columns.tolist()})
    df = df00.join(df01)
    df.loc[df.EXPIRATION_DAYS_00 <= exp_day_num, 'Ticker_00'] = np.nan
    df['Ticker_00'].fillna(df['Ticker_01'], inplace = True)
    df['contract'] = df['Ticker_00'].apply(lambda x:re.sub("\D", "", x))
    df = df[['contract']]
    return df

# return recent_contract and season_contract
def get_current_futures_contract(prod_id, trade_date=None, exp_cut_num=3, mode='recent'):
    assert mode in ['recent', 'season']
    if trade_date is None:
        trade_date = pd.Timestamp.now()
    else:
        trade_date = IO.str_date_parser(trade_date)
    last_trading_day = udt.get_trading_day_offset(trade_date.strftime('%Y%m%d'), -1)[0]
    data = IO.read_data(last_trading_day, columns=['PROD_ID', 'EXPIRATION_DAYS'], ftype=FType.MD, dtype=DType.FUTURES,
                                          dfreq=DFreq.DAILY, h5root=private_root).loc[last_trading_day]
    data = data.loc[data.PROD_ID == prod_id]
    # assert len(data) >= 4
    data = data.sort_values(by='EXPIRATION_DAYS')
    if data.EXPIRATION_DAYS[0] <= exp_cut_num:
        recent_index = 1
    else:
        recent_index = 0
    recent_contract = data.index[recent_index]
    if mode == 'recent':
        return recent_contract
    elif mode == 'season':
        for i in range(recent_index + 1, len(data)):
            contract = data.index[i]
            if int(re.sub("\D", "", contract)) % 100 in [3,6,9,12]:
                season_contract = contract
                return season_contract
        raise AssertionError


def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)


def pd_writer(sig, savepath):
    sig_name = sig.columns[0]
    file_name = os.path.join(savepath, sig_name + '.h5')
    if os.path.exists(file_name):
        #sigold = IO.read_data(alt = file_name)
        sigold = pd.read_hdf(file_name)
        sig = sig[~sig.index.isin(sigold.index)]
        signew = pd.concat([sigold,sig],axis=0).sort_index()
    else:
        signew = sig
    signew.to_hdf(file_name,key=sig_name)


def rolling_norm(sig, window):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if isinstance(sig, pd.DataFrame):
            sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, columns=sig.columns)
            sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, columns=sig.columns)
        elif isinstance(sig, pd.Series):
            sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=sig.name)
            sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=sig.name)
        temp = sig_max - sig_min
        temp[abs(temp) < 1e-8] = np.nan
        signal = (sig - sig_min) / temp
        return 2 * signal - 1


def ts_rank(df, window):
    # moving time-series rank for the past window periods
    assert isinstance(df, pd.Series) or isinstance(df, pd.DataFrame), 'input is not a dataframe or series'
    if window == 1:
        output = df
    else:
        if isinstance(df, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df, window=window, min_count=int(window / 2), axis=0),
                                  index=df.index, columns=df.columns)
        elif isinstance(df, pd.Series):
            output = pd.Series(bk.move_rank(df, window=window, min_count=int(window / 2), axis=0),
                               index=df.index, name=df.name)
    return output


def replace_inf(data, x=np.nan):
    '''replace inf to a predefined number for the input data
    parameters
    --------------------------------------------------
    data: dataframe, series or ndarray
        the data which contains inf
    x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    --------------------------------------------------
    return
    --------------------------------------------------
    data: input data whose inf has been replaced
        the data whose inf is replaced
    --------------------------------------------------
    '''
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'the data structure of input is illegal'
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        data = data.replace([-np.inf, np.inf], x)
    elif isinstance(data, np.ndarray):
        data[np.isinf(data)] = x
    return data


def replace_zero(data, x=np.nan):
    """
    replace 0 to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains 0
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace 0
    :return: same data structure as input data
        input data whose 0 has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data


def ts_delay(data, d):
    # A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = np.empty_like(data)
        if d >= 0:
            output[d:] = data[:-d]
            output[:d] = np.nan
        else:
            output[:d] = data[-d:]
            output[d:] = np.nan

    else:
        output = data.shift(periods=d)
    return output


def ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output


def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_sum(data, d):
    # moving time-series sum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_sum(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance (data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:]-data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output


def ts_median(data, d):
    # moving time-series meidan for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_median(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


def ts_max(data, d):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=int(d / 2), axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_min(data, d):
    # moving time-series minimum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_min(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


class VoidLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
        # if not logger.hasHandlers():
        _dirname = os.path.dirname(file_name)
        if len(_dirname) != 0 and not os.path.exists(_dirname):
            os.makedirs(_dirname)
        file_handler = logging.FileHandler(file_name, mode=mode)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)
    else:
        # if not logger.hasHandlers():
            # default to screen
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(stream_handler)
    return logger
