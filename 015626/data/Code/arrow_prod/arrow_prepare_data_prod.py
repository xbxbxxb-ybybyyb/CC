import datetime
import time
import os
import numpy as np
import pandas as pd
import shutil
import xquant_data
import importlib
import multiprocessing
import sys
import json
import os

import requests
from loguru import logger
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from xquant.factordata import FactorData
s = FactorData()


import logging
import concurrent.futures
from skimage.util import view_as_windows
from multifactor.utility import dt as udt

from xquant.marketdata import MarketData
mdp = MarketData()


money_per_stock = 2500000
model_version = '20230331'
threshold = 0.16
daily_max_num = 50
daily_min_num = 3
blacklist = list(pd.read_csv('/data/user/000072/LYM_STOCKS/blacklist/blacklist.csv', header = None)[0].values)
blacklist_str = ''
for i in blacklist:
    blacklist_str += i + ','
blacklist_str = blacklist_str[:-1]

# today = datetime.datetime.today().strftime('%Y%m%d')
today = s.tradingday(datetime.datetime.today().strftime('%Y%m%d'), (datetime.datetime.today() + datetime.timedelta(days = 60)).strftime('%Y%m%d'))[1]
#today = '20230417'
root_path = '/data/user/000072/LYM_STOCKS/arrow_prod/data/'

user_ids = [
    '019689',
    # '012872',  # 胡俊鹏
    # '015612',  # 陈俊男
#    '018083',  # 郭晨
#    '012129',  # 汪振
    # '015518',  # 陈家强
    # '018728',  # 王楠
]


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


def retrieve_st_stocks_range(start_date, end_date):
    collector = list()
    for trading_day in tdt.get_trading_date_range(start_date, end_date):
        st_stocks = retrieve_st_stocks(trading_day)
        collector.append(pd.Series(True, index=pd.MultiIndex.from_product([[trading_day], st_stocks], names=['dt', 'Ticker'])))
    return pd.concat(collector)


# 新版铃客配置
corpid = 'wwd53282142c96185d'
corpsecret = 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI'
agentid = 1000033
token_url = " http://168.7.124.15:1080/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret)
send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"


class LinkMessage:
    def __init__(self):
        self.__count_limit_new = 20  # 一次实例化后剩余调用的次数

    @staticmethod
    def __get_access_token():
        con = requests.get(token_url)
        json_text = json.loads(con.text)
        access_token = json_text["access_token"]
        return access_token

    def __sendMessage_new(self, msg):
        if not os.environ.get('ENV_VERSION', False):
            raise Exception("Exception: Spark程序不支持发送铃客消息！")
        access_token = self.__get_access_token()
        post_url = send_url.format(access_token)

        success_user_ids = []

        for user_id in user_ids:
            data = {"touser": user_id,
                    "msgtype": "text",
                    "agentid": agentid,
                    "text": {
                        "content": msg
                    }}
            json_data = json.dumps(data)
            if self.__count_limit_new > 0:
                res = requests.post(post_url, json_data)
                self.__count_limit_new = self.__count_limit_new - 1
                if res.status_code != 200:
                    logger.error("Exception: 铃客发送消息失败：消息发送异常！")
                else:
                    success_user_ids.append(user_id)
            else:
                logger.error("Exception: 铃客发送消息失败：已达到最大发送次数！")
        if len(success_user_ids) != len(user_ids):
            logger.error(
                "铃客漏发消息：expect_user_list={}, actual_user_list={}, msg={}".format(user_ids, success_user_ids, msg))
        else:
            logger.info(
                "铃客成功发送消息：msg={}, users={}".format(msg, success_user_ids))

    def sendMessage(self, msg):
        try:
            self.__sendMessage_new(msg)
        except Exception as e:
            logger.error("铃客发送消息失败：msg={}, e={}".format(msg, e))

#blacklist = list(pd.read_csv('/data/user/000072/LYM_STOCKS/blacklist/blacklist.csv', header = None)[0].values)

##############基础文件##############
source_path = '/data/user/000072/LYM_STOCKS/arrow_prod/code/'
target_path = root_path + today + '/'
shutil.copytree(source_path, target_path)
###################################



##############参数文件##############
#params = {
#    "algo": "tvol", 
#    "daily_max_num": 20,
#    "daily_min_num": 3,
#    "end_time": "93500",
#    "order_interval": "1",
#    "order_price": "1",
#    "reorder_price": "99",
#    "start_time": "93000",
#    "stop_time": "93500",
#    "threshold": 0.15,
#    "tvol_ratio": "1",
#    "withdraw_time": "5",
#    "money_per_stock": 100000,
#    "blacklist":blacklist
#}

#out_file = open(root_path + today + '/setting/params.json', 'w')
#json.dump(params, out_file, indent = 4)
#out_file.close()
###################################



##############池子##############
dates = s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 60)).strftime('%Y%m%d'), today)

date_bgn = dates[0]
date_end = dates[-2]

data = IO.read_data([date_bgn, date_end], alt = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
filt = IO.read_data([date_bgn, date_end], dtype=DType.STOCK, ftype=FType.UNIV, dsource=DSource.OPTM)
data = data.join(filt)
data.Listing_date = data.Listing_date.groupby('Ticker').fillna(method = 'ffill').fillna(0).astype('int')

data = data[data.Listing_date > 0]

data['listing_days'] = [x.days for x in np.array([x[0] for x in data.index]) - np.array([pd.Timestamp(str(x)) for x in data.Listing_date.values])]
data['filter_subnew'] = ((data.listing_days > 1) & (data.S_DQ_LOW < data.S_DQ_LIMIT)).groupby('Ticker').expanding().sum().reset_index(level = 0, drop = True) > 1
data['filter_SHSZ'] = data.reset_index()['Ticker'].str.contains('SH|SZ').values


data['filter_1'] = (data.S_DQ_HIGH == data.S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

data['filter_2'] = (data.S_DQ_HIGH > 1.04 * data.S_DQ_OPEN) & (data.S_DQ_CLOSE < data.S_DQ_OPEN)

data['filter_3'] = (data.groupby('Ticker').shift(1).S_DQ_CLOSE == data.groupby('Ticker').shift(1).S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

data['filter_4'] = data.S_DQ_CLOSE > data.S_DQ_STOPPING

daily_universe = data[data.filter_subnew & \
                      data.filter_SHSZ & \
                      data.filter_4 & \
                      (data.filter_1 | data.filter_2 | data.filter_3)]


##############次新股加入blacklist##############
#daily_universe = daily_universe.loc[pd.Timestamp(date_end)].reset_index()['Ticker']
daily_universe = daily_universe.loc[pd.Timestamp(date_end)]
subnew_list = daily_universe[daily_universe.listing_days<90].reset_index()['Ticker'].to_list()
for i in subnew_list:
    blacklist_str += ',' + i
##############次新股加入blacklist##############

daily_universe = list(daily_universe.reset_index()['Ticker'])
st_stocks = retrieve_st_stocks(date_end)
stocklist = [x for x in daily_universe if x not in st_stocks]
#stocklist = list(s.stock_filter(list(daily_universe), date_end, 'STSPEND').stock)
#stocklist = [x for x in stocklist if x not in blacklist]

stocklist = pd.DataFrame({'dt':[pd.Timestamp(today)] * len(stocklist), 'Ticker':stocklist}).set_index(['dt', 'Ticker'])
stocklist = stocklist.join(data.loc[pd.Timestamp(date_end)][['filter_1', 'filter_2', 'filter_3']])
    
stocklist.to_pickle(root_path + today + '/universe/stock_universe.pkl')
################################


##############数据##############
dc = pd.read_pickle(root_path + today + '/universe/stock_universe.pkl')
yesterday = s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 60)).strftime('%Y%m%d'), today)[-2]
dc_1 = pd.DataFrame({'dt':[pd.Timestamp(yesterday)] * len(dc), 'Ticker':dc.reset_index().Ticker}).set_index(['dt','Ticker'])

# pa = root_path + today + '/data/'
# xquant_data.retrieve_level2_by_h5(dc, pa, 'Stock', 24, force_override = False)
# xquant_data.retrieve_level2_by_h5(dc, pa, 'Transaction', 24, force_override = False)
# xquant_data.retrieve_level2_by_h5(dc, pa, 'Order', 24, force_override = False)
# xquant_data.retrieve_level2_by_h5(dc, pa, 'Order_RAW', 24, force_override = False)

#pa = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
pa = '/data/group/800466/warehouse/prod/MD/CHINA_STOCK/'
xquant_data.retrieve_level2_by_h5(dc_1, pa, 'Stock', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc_1, pa, 'Transaction', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc_1, pa, 'Order', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc_1, pa, 'Order_RAW', 24, force_override = False)


target_pa = '/data/user/000072/LYM_STOCKS/data/Transaction/'
for i in dc_1.reset_index().values:
    try:
        print (i[0].strftime('%Y%m%d'), datetime.datetime.now())
        data_txn = pd.read_csv(pa + 'Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
#        data = data.loc[data.dt < i[0].strftime('%Y-%m-%d') + ' 09:26:00']
        data_txn.loc[(data_txn.TradeBuyNo > data_txn.TradeSellNo) & (data_txn.TradeType == 0), 'TradeBSFlag'] = 1
        data_txn.loc[(data_txn.TradeBuyNo < data_txn.TradeSellNo) & (data_txn.TradeType == 0), 'TradeBSFlag'] = 2
        if not os.path.exists(target_pa + i[1]):
            os.makedirs(target_pa + i[1])
        data_txn.to_csv(target_pa + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv', index = False)
    except:
        print(i[0].strftime('%Y%m%d %H:%M:%S'), i[1], 'cannot find arch0 file')
################################


##############factor_dummy##############
univ = pd.read_pickle(root_path + today + '/universe/stock_universe.pkl').reset_index()
trading_days = [pd.Timestamp(x) for x in s.tradingday(today, (pd.Timestamp(today) + datetime.timedelta(days = 60)).strftime('%Y%m%d'))]
next_day_gap = np.array([(trading_days[x+1] - trading_days[x]).days for x in range(len(trading_days) - 1)])

long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 4) & (next_day_gap <= 5)]
long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
univ['long_vacation_3'] = [1 * (x in long_vacation) for x in univ.dt]

long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 6) & (next_day_gap <= 7)]
long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
univ['long_vacation_5'] = [1 * (x in long_vacation) for x in univ.dt]

long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 8) & (next_day_gap <= 100)]
long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
univ['long_vacation_7'] = [1 * (x in long_vacation) for x in univ.dt]

pd.get_dummies(univ.set_index(['dt', 'Ticker'])).to_pickle(root_path + today + '/factors/factor_dummy.pkl')
########################################


##############factor_hist##############
factor_path = '/data/user/000072/LYM_STOCKS/stock_factors_prod/'
factor_list = [x for x in os.listdir(factor_path) if x.endswith('.pkl')]

# factors = []
# for f in factor_list:
#     factors.append(pd.read_pickle(factor_path + f))
# factors = pd.concat(factors, axis = 1)

# trading_dates = [pd.Timestamp(x) for x in s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 100)).strftime('%Y%m%d'), today)]
# factors.loc[trading_dates[-61]:trading_dates[-1]].to_pickle(root_path + today + '/factors/factor_hist.pkl')

trading_dates = [pd.Timestamp(x) for x in s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 100)).strftime('%Y%m%d'), today)]

factors = []
for f in factor_list:
    factors.append(pd.read_pickle(factor_path + f).loc[trading_dates[-61]:trading_dates[-2]])
factors = pd.concat(factors, axis = 1)

factors.to_pickle(root_path + today + '/factors/factor_hist.pkl')
#######################################


##############factor_new##############
os.makedirs('/data/user/000072/LYM_STOCKS/stock_factors_T_1/' + today + '/')
pa = '/data/user/000072/LYM_STOCKS/factor_list_prod_positive_T_1/'
#pa = '/data/user/000072/LYM_STOCKS/factor_list_prod_positive_T_1_late/'
sys.path.insert(0, pa)
def calc(i):
    importlib.import_module(i)
    print (i, ' done ', datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))


factors = [x[:-3] for x in os.listdir(pa) if x.endswith('.py')]

while len(factors) > 0:
    pool = multiprocessing.Pool(processes = 12)
    print(datetime.datetime.now(), "Sub-process(es) start.")
    for i in factors:
        pool.apply_async(calc, (i, ))
        
    pool.close()
    pool.join()
    print(datetime.datetime.now(), "Sub-process(es) done.")

    factors_done = [x[:-4] for x in os.listdir('/data/user/000072/LYM_STOCKS/stock_factors_T_1/' + today + '/') if x.endswith('.pkl')]
    factors = [x for x in factors if x not in factors_done]

factor_path = '/data/user/000072/LYM_STOCKS/stock_factors_T_1/' + today + '/'
factor_list = os.listdir(factor_path)
factor_list.sort()
factors = []
for f in factor_list:
    factors.append(pd.read_pickle(factor_path + f))
factors = pd.concat(factors, axis = 1)
factors.to_pickle(root_path + today + '/factors/factor_new.pkl')
######################################

###########blacklist_df###########################
def format_datetime(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')


def get_minute_data_helper(ticker, date):
    df = mdp.get_data_by_date("Kline1M4ZT", ticker, date, ["2", "3"], sort_by_receive_time=True)
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
                    logger.info('%d/%d - processed' % (current_job, total_jobs))
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


def get_final_data_lastday(date, max_workers=12):
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
    daily_data_for_risk_adjfactor = daily_data_for_risk['S_DQ_ADJFACTOR'].unstack()
    tickers_used = arrow_universe.index.intersection(daily_data_ld.index).intersection(daily_data_dby.index).intersection(daily_data_for_risk_close.columns)
    daily_data_ld = daily_data_ld.loc[tickers_used]
    daily_data_dby = daily_data_dby.loc[tickers_used]
    daily_data_for_risk_close = daily_data_for_risk_close[tickers_used]
    daily_data_for_risk_adjfactor = daily_data_for_risk_adjfactor[tickers_used]
    daily_data_for_risk_adjclose = daily_data_for_risk_close * daily_data_for_risk_adjfactor
    minute_data_dict = concurrent_apply_func(get_minute_data_helper, tickers_used.tolist(), max_workers,
                                             date=last_date.strftime('%Y%m%d'))
    result_df = arrow_universe.loc[tickers_used]
    result_df['last_day_amount_ratio'] = daily_data_ld['S_DQ_AMOUNT'] / daily_data_dby['S_DQ_AMOUNT']
    result_df['last_day_close_to_open'] = daily_data_ld['S_DQ_CLOSE'] / daily_data_ld['S_DQ_OPEN'] - 1
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

    return result_df

config_dict = {
#     'arrow_universe_root': '/data/user/000072/share/for_wsc/arrow/trade_sample/',
    'arrow_universe_root': '/data/user/000072/LYM_STOCKS/arrow_prod/data/',
    'daily_data_root': '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5',
}    
final_data_lastday = get_final_data_lastday(pd.Timestamp(today), max_workers=24)
final_data_lastday.to_pickle(config_dict['arrow_universe_root'] + today + '/rule_blacklist_df.pkl')
##################################################


shutil.copytree(root_path + today, '/data/group/800466/trade/Arrow/trade_files/data_files/' + today)




##############参数文件##################
params_dir = '/data/user/000072/LYM_STOCKS/arrow_prod/params/'
os.makedirs(params_dir + today)

while True:
    if (os.path.exists('/data/user/011477/order/O32/afternoon/组合证券' + yesterday + '.xlsx')) and (os.path.exists('/data/user/011477/order/Trade/委托流水' + yesterday + '_arrow.xlsx')):
        break
    else:
        print (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'), 'no position file yet')
        time.sleep(60)

position = pd.read_excel('/data/user/011477/order/O32/afternoon/组合证券' + yesterday + '.xlsx', dtype = {'证券代码':str})
position = position.loc[position.组合编号 == 2100][['证券代码', '当前数量', '交易市场']]
position.loc[position.交易市场 == '上海', '证券代码'] += '.SH'
position.loc[position.交易市场 == '深圳', '证券代码'] += '.SZ'
position = position[position.当前数量 > 0]
if len(position) > 0:
    arrow_portfolio_sell = pd.DataFrame({'证券代码':position.证券代码, 
                                    '买入交易账户':['2100'] * len(position), 
                                    '卖出交易账户':['2100'] * len(position), 
                                    '买入证券数量':[0] * len(position),
                                    '卖出证券数量':position.当前数量.astype('int')})
    arrow_portfolio_sell.to_excel(params_dir + today + '/arrow_portfolio_sell_' + today + '.xlsx', index = False)


arrow_portfolio_buy = round(money_per_stock / data.loc[pd.Timestamp(yesterday)].reindex(stocklist.index.get_level_values(level = 1)).S_DQ_CLOSE, -2).to_frame().reset_index()
arrow_portfolio_buy = pd.DataFrame({'证券代码':arrow_portfolio_buy.Ticker, 
                                '买入交易账户':['2100'] * len(arrow_portfolio_buy), 
                                '卖出交易账户':['2100'] * len(arrow_portfolio_buy), 
                                '买入证券数量': 2 * arrow_portfolio_buy.S_DQ_CLOSE.astype('int'),
                                '卖出证券数量':[0] * len(arrow_portfolio_buy)})
arrow_portfolio_buy.to_excel(params_dir + today + '/arrow_portfolio_buy_' + today + '.xlsx', index = False)


if len(position) > 0:
    txn = pd.read_excel('/data/user/011477/order/Trade/委托流水' + yesterday + '_arrow.xlsx', dtype = {'证券代码':str}).dropna(subset = ['证券代码'])[['证券代码', '委托方向', '成交金额', '成交数量']]
    txn.loc[txn.证券代码.str.startswith('6'), '证券代码'] += '.SH'
    txn.loc[txn.证券代码.str.startswith('3') | txn.证券代码.str.startswith('0'), '证券代码'] += '.SZ'

    txn_summary_buy = txn.loc[txn.委托方向 == '买入'].groupby('证券代码').sum().reset_index()
    txn_summary_buy = txn_summary_buy.loc[txn_summary_buy.成交数量 > 0]
    #txn_summary_sell = txn.loc[txn.委托方向 == '卖出'].groupby('证券代码').sum()
    #txn_summary_buy['成交均价'] = txn_summary_buy.成交金额 / txn_summary_buy.累计成交数量
    #txn_summary_buy['成交均价'] = txn_summary_buy.成交金额 / txn_summary_buy.累计成交数量

    trading_params_sell = []
    for i in txn_summary_buy.values:
        trading_params_sell.append({
                                "股票代码": i[0],
                                "买卖方向": "S",
                                "交易数量": str(i[2]),
                                "买入金额": "0",
                                "交易开始时间": "133000",
                                "交易结束时间": "140000",
                                "停止下单时间": "145600",
                                "交易算法": "twap",
                                "跟单比例(%)": "0",
                                "下单间隔(s)": "30",
                                "撤单时间(s)": "30",
                                "补单价格": "1",
                                "下单价格": "1"
                                })


    position = position.set_index('证券代码')
    txn_summary_buy = txn_summary_buy.set_index('证券代码')
    sell_AM = (position.当前数量 - txn_summary_buy.reindex(position.index).fillna(0).成交数量).astype('int').rename('qty').to_frame()
    sell_AM = sell_AM.loc[sell_AM.qty > 0].reset_index()
    if len(sell_AM) >= 0:
        for i in sell_AM.values:
            trading_params_sell.append({
                                    "股票代码": i[0],
                                    "买卖方向": "S",
                                    "交易数量": str(i[1]),
                                    "买入金额": "0",
                                    "交易开始时间": "93000",
                                    "交易结束时间": "93500",
                                    "停止下单时间": "145600",
                                    "交易算法": "twap",
                                    "跟单比例(%)": "0",
                                    "下单间隔(s)": "5",
                                    "撤单时间(s)": "10",
                                    "补单价格": "1",
                                    "下单价格": "1"
                                    }) 

    sell_list = {
        "交易日期": pd.Timestamp(today).strftime('%Y-%m-%d'),
    #     "交易账户": "5161205",
    #     "上海证券账户": "D890272174",
    #     "深圳证券账户": "0899014413",
        "数据文件存放目录": "/home/appadmin/EQuant/localdata",
        "Python代码目录": "/home/appadmin/ATS-Quant-prod/strategy/arrow-python",
        "业务数据存放目录": "/data/group/800466/trade/Arrow/trade_files/data_files/" + today,
        "模型存放目录": "/data/group/800466/trade/Arrow/trade_files/model/model_" + model_version,
        "触发计算时间": "09:26:30",
        "Python解释器": "/home/appadmin/anaconda3/bin/python3",
        "跳过Python": "true",
        "决策结果文件": "score.csv",
        "mock测试": "true",
        "预测阈值": str(threshold),
        "最大买入股票数量": str(daily_max_num),
        "最小买入股票数量": str(daily_min_num),
        "买入交易黑名单":blacklist_str,
        "卖出交易黑名单":blacklist_str,
        "交易参数":trading_params_sell
    }

    out_file = open(params_dir + today + '/sell_' + today + '#304301.json', 'w')
    json.dump(sell_list, out_file, indent = 4, ensure_ascii = False)
    out_file.close()



trading_params_buy = []
for s in arrow_portfolio_buy.证券代码.values:
    trading_params_buy.append({
                            "股票代码": s,
                            "买卖方向": "B",
                            "交易数量": "0",
                            "买入金额": str(money_per_stock),
                            "交易开始时间": "93000",
                            "交易结束时间": "93500",
                            "停止下单时间": "93500",
                            "交易算法": "tvol",
                            "跟单比例(%)": "10",
                            "下单间隔(s)": "1",
                            "撤单时间(s)": "1",
                            "补单价格": "99",
                            "下单价格": "1"
                            })

buy_list = {
    "交易日期": pd.Timestamp(today).strftime('%Y-%m-%d'),
#     "交易账户": "5161205",
#     "上海证券账户": "D890272174",
#     "深圳证券账户": "0899014413",
    "数据文件存放目录": "/home/appadmin/EQuant/localdata",
    "Python代码目录": "/home/appadmin/ATS-Quant-prod/strategy/arrow-python",
    "业务数据存放目录": "/data/group/800466/trade/Arrow/trade_files/data_files/" + today,
    "模型存放目录": "/data/group/800466/trade/Arrow/trade_files/model/model_" + model_version,
    "触发计算时间": "09:26:30",
    "Python解释器": "/home/appadmin/anaconda3/bin/python3",
    "跳过Python": "false",
    "决策结果文件": "score.csv",
    "mock测试": "false",
    "预测阈值": str(threshold),
    "最大买入股票数量": str(daily_max_num),
    "最小买入股票数量": str(daily_min_num),
    "买入交易黑名单":blacklist_str,
    "卖出交易黑名单":blacklist_str,
    '交易参数':trading_params_buy
}

out_file = open(params_dir + today + '/buy_' + today + '#304301.json', 'w')
json.dump(buy_list, out_file, indent = 4, ensure_ascii = False)
out_file.close()


shutil.copytree(params_dir + today, '/data/user/000072/share/arrow_prod_params/' + today)


lm = LinkMessage()
lm.sendMessage("Arrow Prod Data Ready " + today + "\nnumber of stocks:" + str(len(arrow_portfolio_buy)))

#shutil.copytree(params_dir + today, '/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today)

#if len(position) > 0:
#    arrow_portfolio_sell_sim = pd.read_excel(params_dir + today + '/arrow_portfolio_sell_' + today + '.xlsx')
#    arrow_portfolio_sell_sim['买入交易账户'] = '5160803'
#    arrow_portfolio_sell_sim['卖出交易账户'] = '5160803'
#    arrow_portfolio_sell_sim.to_excel('/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today + '/arrow_portfolio_sell_' + today + '.xlsx', index = False)

#    with open('/data/user/000072/LYM_STOCKS/arrow_prod/params/' + today + '/sell_' + today + '.json', 'r') as f:
#        sell_list_sim = json.load(f)
#    sell_list_sim['Python代码目录'] = "/home/appadmin/ATS-Quant-sim/strategy/arrow-python"
#    out_file = open('/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today + '/sell_' + today + '.json', 'w')
#    json.dump(sell_list_sim, out_file, indent = 4, ensure_ascii = False)
#    out_file.close()


#arrow_portfolio_buy_sim = pd.read_excel(params_dir + today + '/arrow_portfolio_buy_' + today + '.xlsx')
#arrow_portfolio_buy_sim['买入交易账户'] = '5160803'
#arrow_portfolio_buy_sim['卖出交易账户'] = '5160803'
#arrow_portfolio_buy_sim.to_excel('/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today + '/arrow_portfolio_buy_' + today + '.xlsx', index = False)

#with open('/data/user/000072/LYM_STOCKS/arrow_prod/params/' + today + '/buy_' + today + '.json', 'r') as f:
#    buy_list_sim = json.load(f)
#buy_list_sim['Python代码目录'] = "/home/appadmin/ATS-Quant-sim/strategy/arrow-python"
#out_file = open('/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today + '/buy_' + today + '.json', 'w')
#json.dump(buy_list_sim, out_file, indent = 4, ensure_ascii = False)
#out_file.close()


#shutil.copytree('/data/user/000072/LYM_STOCKS/arrow_sim/params/' + today, '/data/user/000072/share/arrow_sim_params/' + today)