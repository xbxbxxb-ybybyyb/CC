from overnight.insight_base import *
from overnight.naming_config import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import multiprocessing
import time
import pandas as pd
import numpy as np
import os
import sys


def get_current_futures_contract(prod_id, exp_cut_num=3):
    last_trading_day = tdt.get_trading_day_offset(pd.Timestamp.now().strftime('%Y%m%d'), -1)[0]
    data = IO.read_data(last_trading_day, columns=['PROD_ID', 'EXPIRATION_DAYS'], ftype=FType.MD, dtype=DType.FUTURES,
                                          dfreq=DFreq.DAILY, h5root=private_root).loc[last_trading_day]
    data = data.loc[data.PROD_ID == prod_id]
    assert len(data) >= 4
    data = data.sort_values(by='EXPIRATION_DAYS')
    if data.EXPIRATION_DAYS[0] <= exp_cut_num:
        return data.index[1]
    else:
        return data.index[0]


def prepare_tickers():
    index_tickers = ['000905.SH', '000300.SH', '000016.SH']
    futures_tickers = [get_current_futures_contract(item).replace('.CFE', '.CF') for item in ['IC.CFE', 'IF.CFE', 'IH.CFE']]
    misc_tickers = ['204001.SH']
    return index_tickers + futures_tickers + misc_tickers


def retrieve_misc_minute_helper():
    today = pd.Timestamp.now().strftime('%Y%m%d')
    contract_info = pd.read_hdf(futures_contract_info_path)
    tickers = prepare_tickers()
    data = job_wrapper(play_back_oneday, OnRecvKLine, postprocess_playback, release_resource=True, stock_list=tickers,
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
    data['CONTRACTMULTIPLIER'] = contract_info.CONTRACTMULTIPLIER.reindex(data.index, level='Ticker')
    data['vwap'] = (data['amount'] / data['volume'] / data['CONTRACTMULTIPLIER']).where(data['volume'] != 0, other=np.nan)
    misc_minute_pd = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap']].infer_objects()
    out_path = os.path.join(trade_root, 'hot', today, 'misc_minute.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    misc_minute_pd.to_hdf(out_path, 'misc_minute', mode='w')
    return misc_minute_pd


if __name__ == '__main__':
    retrieve_misc_minute_helper()

