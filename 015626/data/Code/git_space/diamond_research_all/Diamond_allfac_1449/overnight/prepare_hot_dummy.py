from overnight.naming_config import *
from overnight.utility import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import time, datetime
import pandas as pd
import numpy as np
import os
import sys

# edb_cache_h5_path = '/data/group/800466/trade/overnight/cache/edb.h5'
# edb_cache_pd = pd.read_hdf(edb_cache_h5_path)
# edb_cache_pd = edb_cache_pd.fillna(method='pad')
index_spot_cache_dict = dict()

for ticker in ['000300.SH','000905.SH','000016.SH','000906.SH']:
    spot = pd.read_pickle(os.path.join(spot_data_path, 'indexMinute_%s.pkl' % ticker.split('.')[0]), compression='gzip').reset_index()
    spot['dt'] = spot['dt'] * 1E6 + spot['minute'] * 100
    spot['dt'] = pd.to_datetime(spot['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    spot = spot.rename(columns = {'amt':'amount'}).set_index('dt').drop(['Ticker','minute'], axis=1)
    index_spot_cache_dict[ticker] = spot.infer_objects()

def prepare_cfghf_data(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    start_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_start_time))
    end_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_stop_time))

    cfg_hf_data = pd.read_pickle(cfg_hf_data_path)

    target_data = []
    for x in cfg_hf_data.keys():
        target_data.append(cfg_hf_data[x].loc[start_dt : end_dt].stack().to_frame(name = x.replace('_500', '')))
    target_data = pd.concat(target_data, axis = 1).drop(['weight'], axis = 1)

    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'), f"cfg500_hf_data_{trade_stop_time.strftime('%H%M')}.h5")
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    target_data.to_hdf(out_path, f"cfg500_hf_data_{trade_stop_time.strftime('%H%M')}", mode='w')
    del(cfg_hf_data)
    return target_data


def prepare_edb_dummy(ref_date, last_num_days=20):
    end_date = IO.str_date_parser(ref_date)
    start_date = tdt.get_trading_day_offset(end_date, -last_num_days)[0]
    edb_pd = edb_cache_pd.loc[start_date:end_date]
    out_path = os.path.join(trade_root, 'hot_proof', end_date.strftime('%Y%m%d'), 'edb.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    edb_pd.to_hdf(out_path, 'edb', mode='w')
    return edb_pd


def prepare_mdconstant_dummy(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    mdconstant = IO.read_data(ref_date, columns=['S_DQ_ADJFACTOR', 'S_DQ_PRECLOSE', 'S_DQ_LIMIT', 'S_DQ_STOPPING'], alt=alla_eod_path).loc[ref_date]
    mdconstant.columns = [item.replace('S_DQ_', '').lower() for item in mdconstant.columns]
    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'), 'mdconstant.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    mdconstant.to_hdf(out_path, 'mdconstant', mode='w')
    return mdconstant


def prepare_misc_minute_dummy(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    start_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_start_time))
    end_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_stop_time))
    collector = list()
    # get index minute
    for k, v in index_spot_cache_dict.items():
        spot_data = v.loc[start_dt:end_dt].reset_index()
        spot_data['Ticker'] = k
        spot_data = spot_data.set_index(['dt', 'Ticker'])
        collector.append(spot_data)
    # get futures minute
    col_list = ['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'position']
    futures_data = IO.read_data([start_dt, end_dt], columns=col_list, alt=futures_data_path)
    collector.append(futures_data)
    # get gc minute
    gc_data = IO.read_data([start_dt, end_dt], universe=['204001.SH'],
                            columns=['open', 'high', 'low', 'close', 'volume', 'amount'], alt=gc_hispath)
    collector.append(gc_data)
    misc_minute_pd = pd.concat(collector, axis=0, sort=False).sort_index().infer_objects()
    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'), 'misc_minute_%s.h5' % trade_stop_time.strftime('%H%M'))
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    misc_minute_pd.to_hdf(out_path, 'misc_minute', mode='w')
    return misc_minute_pd


def prepare_alla_kline_1min(ref_date):
    ref_date = IO.str_date_parser(ref_date)
    start_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_start_time))
    mid_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_mid_time))
    end_dt = pd.Timestamp(datetime.datetime.combine(ref_date, trade_stop_time))
    minute_data = get_stock_data_per_date(ref_date.strftime('%Y%m%d'))[['open', 'high', 'low', 'close', 'volume', 'amount']].infer_objects()
    first_batch = minute_data.loc[start_dt:mid_dt]
    first_tag = 'alla_kline_1min_%s_%s.h5' % (trade_start_time.strftime('%H%M%S'), trade_mid_time.strftime('%H%M%S'))
    second_batch = minute_data.loc[mid_dt:end_dt]
    second_batch = second_batch.drop(second_batch.loc[:mid_dt].index)
    second_tag = 'alla_kline_1min_%s_%s.h5' % (trade_mid_time.strftime('%H%M%S'), trade_stop_time.strftime('%H%M%S'))
    out_path = os.path.join(trade_root, 'hot_proof', ref_date.strftime('%Y%m%d'))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    first_batch.to_hdf(os.path.join(out_path, first_tag), 'alla_kline_1min', mode='w')
    second_batch.to_hdf(os.path.join(out_path, second_tag), 'alla_kline_1min', mode='w')
    return first_batch, second_batch


def prepare_hot_dummy(ref_date):
    # prepare_edb_dummy(ref_date)
    prepare_mdconstant_dummy(ref_date)
    prepare_misc_minute_dummy(ref_date)
    prepare_alla_kline_1min(ref_date)
    prepare_cfghf_data(ref_date)

