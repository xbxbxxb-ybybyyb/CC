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


def chunks(l, n):
    # yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i+n]


def retrieve_alla_helper(start_time, stop_time, num_per_exec=2500, release_resource=True):
    today = pd.Timestamp.now().strftime('%Y%m%d')
    alla_ref_date = tdt.get_trading_day_offset(today, -1)[0]
    alla_tickers = IO.read_data(alla_ref_date, columns='alla', dtype=DType.STOCK, ftype=FType.UNIV, dsource=DSource.OPTM)['alla']
    alla_tickers = alla_tickers.loc[alla_tickers].index.get_level_values(level='Ticker').tolist()
    collector = list()
    for chunk in chunks(alla_tickers, num_per_exec):
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
    alla_pd = data[['open', 'high', 'low', 'close', 'volume', 'amount']].infer_objects()
    out_path = os.path.join(trade_root, 'hot', today, 'alla_kline_1min_%s_%s.h5' % (start_time.strftime('%H%M%S'), stop_time.strftime('%H%M%S')))
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    alla_pd.to_hdf(out_path, 'alla_kline_1min', mode='w')
    return alla_pd


if __name__ == '__main__':
    retrieve_alla_helper(trade_start_time, trade_mid_time)
    # retrieve_alla_helper(trade_mid_time, trade_stop_time)

