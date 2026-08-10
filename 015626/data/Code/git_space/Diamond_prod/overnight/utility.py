import os
import re
import sys
import dill
import json
import time
import sched
import pickle
import logging
import functools
import numpy as np
import pandas as pd
import bottleneck as bk
import concurrent.futures
from multifactor.IO import IO
import multifactor.utility.dt as udt
from overnight.naming_config import *
from multifactor.IO.IO_enums import *
from xquant.futuredata import FutureData
from multifactor.data.utils import check_update_date

fd = FutureData()


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


def get_st_stock_list(date):
    date = IO.str_date_parser(date)
    cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT'], dtable=DTable.AShareST).reset_index('dt', drop=True)
    cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
    cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
    cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()
    

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


#def get_trade_contract(start_date, end_date, prod_id, exp_day_num=2):
#    pd_data_daily = IO.read_data([start_date, end_date], dtype=DType.FUTURES, h5root=private_root)
#    IC_daily = pd_data_daily[pd_data_daily.PROD_ID == prod_id]
#    df00 = IC_daily.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
#    df01 = IC_daily.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
#    df00 = df00.rename(columns = {x:x+'_00' for x in df00.columns.tolist()})
#    df01 = df01.rename(columns = {x:x+'_01' for x in df01.columns.tolist()})
#    df = df00.join(df01)
#    df.loc[df.EXPIRATION_DAYS_00 <= exp_day_num, 'Ticker_00'] = np.nan
#    df['Ticker_00'].fillna(df['Ticker_01'], inplace = True)
#    df['contract'] = df['Ticker_00'].apply(lambda x:re.sub("\D", "", x))
#    df = df[['contract']]
#    return df
    
    
def get_trade_contract(start_date, end_date, prod_id):
    temp_data = IO.read_data([start_date, end_date], alt=universe_root)
    temp_data = temp_data.xs(prod_id, level=1)['contract_00'].apply(lambda x:re.sub("\D", "", x)).to_frame()
    temp_data.columns = ['contract']
    return temp_data

# return recent_contract and season_contract
#def get_current_futures_contract(prod_id, trade_date=None, exp_cut_num=3, mode='recent'):
#    assert mode in ['recent', 'season']
#    if trade_date is None:
#        trade_date = pd.Timestamp.now()
#    else:
#        trade_date = IO.str_date_parser(trade_date)
#    last_trading_day = udt.get_trading_day_offset(trade_date.strftime('%Y%m%d'), -1)[0]
#    data = IO.read_data(last_trading_day, columns=['PROD_ID', 'EXPIRATION_DAYS'], ftype=FType.MD, dtype=DType.FUTURES,
#                                          dfreq=DFreq.DAILY, h5root=private_root).loc[last_trading_day]
#    data = data.loc[data.PROD_ID == prod_id]
#    # assert len(data) >= 4
#    data = data.sort_values(by='EXPIRATION_DAYS')
#    if data.EXPIRATION_DAYS[0] <= exp_cut_num:
#        recent_index = 1
#    else:
#        recent_index = 0
#    recent_contract = data.index[recent_index]
#    if mode == 'recent':
#        return recent_contract
#    elif mode == 'season':
#        for i in range(recent_index + 1, len(data)):
#            contract = data.index[i]
#            if int(re.sub("\D", "", contract)) % 100 in [3,6,9,12]:
#                season_contract = contract
#                return season_contract
#        raise AssertionError
#def get_current_futures_contract(prod_id, trade_date=None, exp_cut_num=3, mode='recent'):
#    assert mode in ['recent', 'season']
#    if trade_date is None:
#        trade_date = pd.Timestamp.now()
#    else:
#        trade_date = IO.str_date_parser(trade_date)
#    last_trading_day = udt.get_trading_day_offset(trade_date.strftime('%Y%m%d'), -1)[0]
#    data = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
#    data_recent_month_mask = data['recent_month_mask'].loc[last_trading_day:].iloc[0]
#    assert data_recent_month_mask.name.date() == last_trading_day.date()
#    recent_contract = data_recent_month_mask[data_recent_month_mask==1].index[0]
#    contract_list = data_recent_month_mask.loc[recent_contract:].index
#    for contract in contract_list[1:]:
#        if int(re.sub("\D", "", contract)) % 100 in [3,6,9,12]:
#            season_contract = contract
#            break
#    if mode == 'recent':
#        return prod_id.split('.')[0] + recent_contract
#    elif mode == 'season':
#        return prod_id.split('.')[0] + season_contract
def get_current_futures_contract(prod_id, trade_date=None, exp_cut_num=3, mode='recent'):
    assert mode in ['recent', 'season']
    if trade_date is None:
        trade_date = pd.Timestamp.now()
    else:
        trade_date = IO.str_date_parser(trade_date)
    last_trading_day = udt.get_trading_day_offset(trade_date.strftime('%Y%m%d'), -1)[0]
    data = IO.read_data(last_trading_day, columns=['prod_id', 'expiration_days'], 
                        alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5').loc[last_trading_day]
    data = data.loc[data.prod_id == prod_id]
    # assert len(data) >= 4
    data = data.sort_values(by='expiration_days')
    if data.expiration_days[0] <= exp_cut_num:
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
    
    
def get_single_minute_data(data, time):
    data_single_minute = data.iloc[data.index.indexer_at_time(time)]
    data_single_minute.index = pd.to_datetime(data_single_minute.index.date)
    data_single_minute.index.name = 'dt'
    return data_single_minute


    
    
def get_future_codes(date=None, ticker_list=('IC', 'IF', 'IH')):
    if date is None:
        date = int(pd.Timestamp.now().strftime('%Y%m%d'))
    result_list = list()
    for ticker in ticker_list:
        result_list += fd.get_instrument_all(ticker, date, date)
    return result_list
    
    
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
                    logger.info('%d/%d - processed' % (current_job, total_jobs))
        logger.info('executor finished')
    if collect_results:
        return result_collector


def save_pickle(save_dict, save_path, protocol=pickle.HIGHEST_PROTOCOL):
    with open(save_path, 'wb') as temp_input:
        pickle.dump(save_dict, temp_input, protocol=protocol)
    return

    
