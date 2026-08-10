from insight_base import *
from naming_config import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import multiprocessing
import time
import pandas as pd
import numpy as np
import os
import sys

def chunks(l, n):
    # yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i+n]

def retrieve_ccbond_helper(start_time, stop_time, num_per_exec=2500, release_resource=True):
    today = pd.Timestamp.now().strftime('%Y%m%d')
    ccbond_ref_date = tdt.get_trading_day_offset(today, -1)[0]
    ccbond_ref_date_10 = tdt.get_trading_day_offset(today, -10)[0]
    # get tickers from history dump
    ccbond = IO.read_data([ccbond_ref_date_10, today], columns=['amount_3000'], alt = kzz_universe_path)
    # value check
    ccbond_num = len(ccbond.loc[ccbond_ref_date:].index.get_level_values(level='Ticker').unique())
    print(f'CCBOND UNIVERSE NUM: {ccbond_num}')
    assert ccbond_num >= 300
    ccbond_tickers = ccbond.index.get_level_values(level='Ticker').unique().tolist()
    collector = list()
    for chunk in chunks(ccbond_tickers, num_per_exec):
        print(len(chunk))
        collector.append(job_wrapper(play_back_oneday, OnRecvKLine, postprocess_playback,
                                     release_resource=False,
                                     stock_list=chunk,
                                     start_time=today+start_time.strftime('%H%M%S'), stop_time=today+stop_time.strftime('%H%M%S'),
                                     marketdata_type=EMarketDataType.MD_KLINE_1MIN))
    data = pd.concat(collector, axis=0).sort_index()
    if release_resource:
        logout()
    data['open'] = data['OpenPx'] / 1E4
    data['high'] = data['HighPx'] / 1E4
    data['low'] = data['LowPx'] / 1E4
    data['close'] = data['ClosePx'] / 1E4
    data['volume'] = data['TotalVolumeTrade']
    data['amount'] = data['TotalValueTrade']
    ccbond_pd = data[['open', 'high', 'low', 'close', 'volume', 'amount']].infer_objects()
    hot_path = os.path.join(hot_root, today)
    if not os.path.exists(hot_path):
        os.makedirs(hot_path)
    out_path = os.path.join(hot_path, 'ccbond_kline_1min_%s_%s.h5' % (start_time.strftime('%H%M%S'), stop_time.strftime('%H%M%S')))
    ccbond_pd.to_hdf(out_path, 'ccbond_kline_1min', mode='w')
    return ccbond_pd

if __name__ == '__main__':
    retrieve_ccbond_helper(morning_start_time, mid_job_time)
    retrieve_ccbond_helper(mid_job_time, ref_close_end_time)