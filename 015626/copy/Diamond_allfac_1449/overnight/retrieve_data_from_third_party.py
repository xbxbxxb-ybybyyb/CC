import re
import numpy as np
import pandas as pd
from overnight.naming_config import *
from xquant.thirdpartydata.marketdata import MarketData
from overnight.utility import add_file_logger, scheduler
from overnight.utility import concurrent_apply_func, get_future_codes, replace_zero
from xquant.xqutils.helper import link
lm = link.LinkMessage()

ma = MarketData()


def prepare_tickers(ref_date=None):
    index_tickers = ['000905.SH', '000300.SH', '000016.SH', '000906.SH']
    futures_tickers = get_future_codes(ref_date)
    misc_tickers = ['204001.SH']
    return index_tickers + futures_tickers + misc_tickers
    

def retrieve_single_stock(ticker, date, start_time, stop_time):
    date_str = date.strftime('%Y%m%d')
    df_raw = ma.getMDSecurityKLineDataFrame(ticker, date_str + start_time.strftime("%H%M%S"), date_str + stop_time.strftime("%H%M%S"), 10, 20)
    df_raw['dt'] = pd.to_datetime(df_raw['MDDate'] + df_raw['MDTime'], format='%Y%m%d%H%M%S%f')
    df_raw['Ticker'] = ticker
    df_result = df_raw[['dt', 'Ticker', 'OpenPx', 'HighPx', 'LowPx', 'ClosePx', 'TotalVolumeTrade',
                        'TotalValueTrade']].set_index(['dt', 'Ticker'])
    df_result.columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
    return df_result
    
    
def retrieve_single_misc(ticker, date, start_time, stop_time):
    date_str = date.strftime('%Y%m%d')
    df_raw = ma.getMDSecurityKLineDataFrame(ticker, date_str + start_time.strftime("%H%M%S"), 
                                            date_str + stop_time.strftime("%H%M%S"), 10, 20)
    df_raw['dt'] = pd.to_datetime(df_raw['MDDate'] + df_raw['MDTime'], format='%Y%m%d%H%M%S%f')
    df_raw['Ticker'] = ticker.replace('.CF', '.CFE')
    df_result = df_raw[['dt', 'Ticker', 'OpenPx', 'HighPx', 'LowPx', 'ClosePx', 'TotalVolumeTrade',
                        'TotalValueTrade', 'OpenInterest']].set_index(['dt', 'Ticker'])
    df_result.columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 'position']
    
    if ticker.endswith('.CF'):
        future_multiplier = price_per_point[re.sub('\d+', '', df_raw['Ticker'].iloc[0])]
        df_result['vwap'] = df_result['amount'] / replace_zero(df_result['volume']) / future_multiplier
    else:
        df_result['vwap'] = np.nan
    return df_result
    

def retrieve_alla_helper(start_time, stop_time, date=None, stock_list=None):
    if date is None:
        date = pd.Timestamp.now()
    date_str = date.strftime('%Y%m%d')
    if stock_list is None:
        stock_list = pd.read_pickle(os.path.join(hisdata_path, date_str, 'alla_stock_list.pkl'))
    result_dict = concurrent_apply_func(retrieve_single_stock, stock_list, getdata_parallel_count, date=date, start_time=start_time, stop_time=stop_time, void_log_flag=True)
    result_df = pd.concat(result_dict.values()).sort_index()
    out_path = os.path.join(trade_root, 'hot', date_str, f'alla_kline_1min_{start_time.strftime("%H%M%S")}_{stop_time.strftime("%H%M%S")}.h5')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result_df.to_hdf(out_path, 'alla_kline_1min', mode='w')
    
    
def retrieve_misc_helper(start_time, stop_time, date=None):
    if date is None:
        date = pd.Timestamp.now()
    date_str = date.strftime('%Y%m%d')
    ticker_list = prepare_tickers(date_str)
    result_dict = concurrent_apply_func(retrieve_single_misc, ticker_list, getdata_parallel_count, date=date, start_time=start_time, stop_time=stop_time, void_log_flag=True)
    result_df = pd.concat(result_dict.values()).sort_index()
    out_path = os.path.join(trade_root, 'hot', date_str, f'misc_minute_{stop_time.strftime("%H%M")}.h5')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result_df.to_hdf(out_path, 'misc_minute', mode='w')
    
    
def retrieve_mdconstant_helper(date=None, stock_list=None):
    if date is None:
        date = pd.Timestamp.now()
    date_str = date.strftime('%Y%m%d')
    if stock_list is None:
        stock_list = pd.read_pickle(os.path.join(hisdata_path, date_str, 'alla_stock_list.pkl'))
    mdc = ma.get_am_mdc_constant(stock_list).reset_index('mddate', drop=True)
    mdc = mdc[['mdc_adjfactor', 'mdc_pre_close', 'mdc_maxpx', 'mdc_minpx']].sort_index()
    mdc.columns = ['adjfactor', 'preclose', 'limit', 'stopping']
    out_path = os.path.join(trade_root, 'hot', date_str, 'mdconstant.h5')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    mdc.to_hdf(out_path, 'mdconstant', mode='w')

def retrieve_helper():
    lm.sendMessage(str(dt.datetime.now()) + " start alla and misc data!" )
    retrieve_alla_helper(trade_mid_time, trade_stop_time)
    lm.sendMessage(str(dt.datetime.now()) + " alla data done!" )
    retrieve_misc_helper(trade_start_time, trade_stop_time)

if __name__ == '__main__':
#    retrieve_misc_helper(trade_start_time, trade_stop_time, pd.Timestamp(2024, 4, 16))
    # retrieve_mdconstant_helper()
    date_str = pd.Timestamp.now().strftime('%Y%m%d')
    flag_path_success = os.path.join(trade_root, 'hot', date_str, 'alla_misc_done.success')
    if os.path.exists(flag_path_success):
        os.remove(flag_path_success)

    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
    scheduler(retrieve_helper, target_trigger_time, delay=2000)

    with open(flag_path_success,'w') as file:
        pass

    lm.sendMessage(str(dt.datetime.now()) + " misc data done!" )
