from overnight.insight_base import *
from overnight.naming_config import *
from overnight.utility import get_future_codes
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import multiprocessing
import time
import pandas as pd
import numpy as np
import os
import re
import sys


def prepare_tickers(ref_date):
    index_tickers = ['000905.SH', '000300.SH', '000016.SH', '000906.SH']
    futures_tickers = get_future_codes(ref_date)
    misc_tickers = ['204001.SH']
    return index_tickers + futures_tickers + misc_tickers


def retrieve_misc_minute_helper(release_resource=True):
    today = pd.Timestamp.now().strftime('%Y%m%d')
#    today = '20240606'
#    contract_info = pd.read_hdf(futures_contract_info_path)
    tickers = prepare_tickers(today)
    data = job_wrapper(play_back_oneday, OnRecvKLine, postprocess_playback, release_resource=release_resource, stock_list=tickers,
                       start_time=today+trade_start_time.strftime('%H%M%S'),
                       stop_time=today+trade_stop_time.strftime('%H%M%S'),
                       marketdata_type=EMarketDataType.MD_KLINE_1MIN)
    # ticker fix
    data = data.reset_index()
    data['Ticker'] = data['Ticker'].str.replace('.CF', '.CFE')
    data = data.set_index(['dt', 'Ticker'])
    # unit fix
    data['open'] = data['OpenPx'] / 1E4
    data['high'] = data['HighPx'] / 1E4
    data['low'] = data['LowPx'] / 1E4
    data['close'] = data['ClosePx'] / 1E4
    data['volume'] = data['TotalVolumeTrade']
    data['amount'] = data['TotalValueTrade']
    data['position'] = data['OpenInterest']
    # calculate vwap
    future_contract = [i for i in data.index.levels[1].unique() if i.endswith('.CFE')]
    future_multiplier = [price_per_point[re.sub('\d+', '', i)] for i in future_contract]
    future_multiplier_ss = pd.Series(future_multiplier, index=future_contract)
    data['CONTRACTMULTIPLIER'] = future_multiplier_ss.reindex(data.index, level='Ticker')
    data['vwap'] = (data['amount'] / data['volume'] / data['CONTRACTMULTIPLIER']).where(data['volume'] != 0, other=np.nan)
    misc_minute_pd = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap']].infer_objects()
    out_path = os.path.join(trade_root, 'hot', today, 'misc_minute_%s.h5' % trade_stop_time.strftime('%H%M'))
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    misc_minute_pd.to_hdf(out_path, 'misc_minute', mode='w')
    return misc_minute_pd


if __name__ == '__main__':
    retrieve_misc_minute_helper()

