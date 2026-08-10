import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from diamond_vk.naming_config import *
import functools
import dill
import re
import bottleneck as bk
import json
import sched, time
import logging
import sys
from skimage.util import view_as_windows


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

def ts_skew(data, d):
    # moving time-series skew over the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = np.full_like(data, np.nan)
            temp = rolling_window_upgrade(data, d)
            output[d - 1:] = scipy.stats.skew(temp, axis=-1, bias=False)
        else:
            output = data.rolling(d, min_periods=int(d / 2)).skew()
            output.iloc[:d - 1] = np.nan
    return output
    
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

def ts_std(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=data.index, name=data.name)
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

def ts_cov(data1, data2, d):
    # data1, data2过去d条数据的时序协方差
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized*data2_expanding_centralized, axis=-1) * flag2 / (
                d - 1 - flag1)
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).cov(data2)
        output.iloc[:d - 1] = np.nan
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

def MIN(A,B):
    # 返回A,B中对应位置最小值
    if isinstance(A,pd.Series):
        A = A.to_frame()
    if isinstance(B,pd.Series):
        B = B.to_frame()
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy()
        output[A>B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy()
        output[A>B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy()
        output[B>A] = A
    else:
        output = A if A<B else B
    return output

def MAX(A,B):
    # 返回A,B中对应位置最大值
    if isinstance(A,pd.Series):
        A = A.to_frame()
    if isinstance(B,pd.Series):
        B = B.to_frame()
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy()
        output[A<B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy()
        output[A<B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy()
        output[B<A] = A
    else:
        output = A if A>B else B
    return output


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    elif data.ndim == 2:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding
    
def ts_pred(data, d, reg_x=None):
    """
    use rolling linear regression to predict value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe or series
        the predicted value of rolling linear regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    return reg_pred


def ts_pred_delta(data, d, reg_x=None):
    """
    the difference of the predicted value of rolling linear regression and real value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe, series or ndarray
        the difference of the predicted value of rolling linear regression and real value
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    reg_delta = data - reg_pred
    return reg_delta

def ts_reg_alpha(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到截距项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        intercept term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)
    reg_beta = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1)
    output_need = (np.nanmean(data_expanding, axis=-1) - reg_beta * np.nanmean(reg_x_expanding, axis=-1)) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output


def ts_reg_beta(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到斜率项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        slope term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)   
    output_need = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output


def ts_reg_residual(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到的残差项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        residual term of regression
    """
    if reg_x is None:  # or (len(reg_x) == d):
        reg_x_expanding = np.full_like(data, d)
    elif len(reg_x) == d:
        reg_x_expanding = np.full_like(data, reg_x[-1])
    elif len(reg_x) == data.shape[0]:
        reg_x_expanding = reg_x
    reg_slope = ts_reg_beta(data, d, reg_x)
    reg_intercept = ts_reg_alpha(data, d, reg_x)
    output = data - reg_slope * reg_x_expanding - reg_intercept
    return output

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.array(np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides))
    return rolling_table
    
def ts_truncated_ema(df1, d, alpha):
    # truncated ema
    if isinstance(df1, pd.DataFrame):
        assert df1.shape[1] == 1
        df1 = df1[df1.columns[0]]
            
    assert isinstance(df1, pd.Series), 'the data structure of input is illegal, must be series'
    assert 0 < alpha <1
    df1_copy = df1.copy()
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    output = pd.Series(np.nan, index=df1_copy.index, name=df1_copy.name)
    temp_y = rolling_window(df1_copy, d)
    temp_x = np.tile(weight, (temp_y.shape[0], 1))
    flag = np.isnan(temp_x) | np.isnan(temp_y)
    flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
    flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
    temp_x[flag] = np.nan
    temp_y[flag] = np.nan
    output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output

def norm_winsor(factor_pd, bound=3, winsor=False):
    factor_pd = factor_pd.copy()
    factor_pd = median_filter(factor_pd, mad=bound, winsor=winsor, inplace=True)
    std_ts = factor_pd.std(axis=1, ddof=0)
    std_ts.loc[std_ts == 0] = 1
    factor_pd = factor_pd.subtract(factor_pd.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_pd


def median_filter(factor_pd, mad=3, winsor=False, inplace=False):
    if not inplace:
        factor_pd = factor_pd.copy()
    dm = factor_pd.median(axis=1)
    # caution of symmetric uppper & lower bounds
    dist_dm = (factor_pd.subtract(dm, axis=0)).abs().median(axis=1)
    date_num, stock_num = factor_pd.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    if winsor:
        factor_pd[factor_pd > fac_ub] = np.nan
        factor_pd[factor_pd < fac_lb] = np.nan
    else:
        factor_pd[factor_pd > fac_ub] = fac_ub
        factor_pd[factor_pd < fac_lb] = fac_lb
    return factor_pd
    
def factor_to_signal(df, in_t = 0.8, out_t = 0.5):
    factorname = df.columns[0]

    condition1 = df[factorname] >= in_t
    condition2 = df[factorname].shift(1) < in_t
    df.loc[condition1 & condition2, 'signal_long'] = 1

    condition1 = df[factorname] < out_t
    condition2 = df[factorname].shift(1) >= out_t
    df.loc[condition1 & condition2, 'signal_long'] = 0

    condition1 = df[factorname] <= (-1 * in_t)
    condition2 = df[factorname].shift(1) > (-1 * in_t)
    df.loc[condition1 & condition2, 'signal_short'] = -1

    condition1 = df[factorname] > (-1 * out_t)
    condition2 = df[factorname].shift(1) <= (-1 * out_t)
    df.loc[condition1 & condition2, 'signal_short'] = 0

    df['signal'] = df[['signal_long', 'signal_short']].sum(axis = 1, min_count = 1, skipna = True)
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]

    df['signal'] = temp['signal']
    df['signal'] = df['signal'].fillna(method = 'ffill')
    df['signal'] = df['signal'].fillna(value = 0)

    df = df[['signal']]
    df.columns = [factorname]
    return df
    
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(cache=None)
def retrieve_st_stocks(date):
    date = IO.str_date_parser(date)
    if retrieve_st_stocks.cache is None:
        cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT'], dtable=DTable.AShareST).reset_index('dt', drop=True)
        cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
        cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
        cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
        retrieve_st_stocks.cache = cache
    else:
        cache = retrieve_st_stocks.cache
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()