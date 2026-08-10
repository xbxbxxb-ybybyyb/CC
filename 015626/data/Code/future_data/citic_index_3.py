#from multifactor.IO.naming_config import private_h5root, minute_stock_per_date_path
import multifactor.utility.common as ut
import multifactor.utility.dt as tdt
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import functools
import pandas as pd
import numpy as np
import datetime
import os


@functools.lru_cache(maxsize=None)
def to_datetime(x, format='%Y%m%d%H%M%S'):
    return pd.to_datetime(x, format=format)
    
def fill_infinite(x, value=0):
    if np.any([isinstance(x, item) for item in [pd.DataFrame, pd.Series]]):
        return x.replace([np.nan, np.inf, -np.inf], value)
    elif isinstance(x, np.ndarray):
        return np.where(np.isfinite(x), x, value)
    else:
        raise AssertionError

minute_stock_per_date_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/'

def retrieve_stock_minute(start_date, end_date):
    print('retrieving stock minute data per day')
    collector = list()
    for ts in tdt.get_trading_date_range(start_date, end_date):
        print('processing %s' % ts)
        file_path = os.path.join(minute_stock_per_date_path, ts.strftime('%Y%m%d') + '.pkl')
        collector.append(pd.read_pickle(file_path, compression='gzip'))
    spot_data = pd.concat(collector, axis=0)
    spot_data = spot_data.reset_index()
    spot_data['dt'] = spot_data['dt'] * 1E6 + spot_data['minute'] * 100
    spot_data['dt'] = spot_data['dt'].astype('int').map(to_datetime)
    spot_data['Ticker'] = spot_data['Ticker'].apply(ut.ticker_match)
    spot_data = spot_data.set_index(['dt', 'Ticker'])
    spot_data[['open', 'high', 'low', 'close']].replace(0, np.nan, inplace=True)
    spot_data['midprice'] = spot_data[['open', 'high', 'low', 'close']].mean(axis=1)
    spot_data['volume'] = fill_infinite(spot_data['volume'], 0)
    spot_data['amt'] = fill_infinite(spot_data['amt'], 0)
    spot_data['vwap'] = spot_data['midprice'].where((spot_data['volume'] == 0) | (spot_data['amt'] == 0), other=spot_data['amt'] / spot_data['volume'])
    spot_data['trading_day'] = pd.to_datetime(spot_data.index.get_level_values(level=0).date)
    spot_data = spot_data.drop(['midprice', 'minute'], axis=1)
    return spot_data


def CITIC_helper(level):
    citic_info = pd.read_csv('/data/user/015626/data/share/LOCAL_DATA/CSV/WIND/AIndexMembersCITICS'+str(level)+'.csv')
    citic_info['S_CON_INDATE'] = citic_info['S_CON_INDATE'].astype('float')
    citic_info['S_CON_OUTDATE'] = citic_info['S_CON_OUTDATE'].astype('float')
    citic_info['S_CON_OUTDATE'].fillna(np.inf, inplace=True)
    def decorate(date):
        date = int(IO.str_date_parser(date).strftime('%Y%m%d'))
        valid_sliced = citic_info[(citic_info.S_CON_INDATE <= date) & (citic_info.S_CON_OUTDATE > date)]
        collector = list()
        for tag, group in valid_sliced.groupby('S_INFO_WINDCODE'):
            container = dict()
            container['Ticker'] = list(group.S_CON_WINDCODE)
            container['dt'] = IO.str_date_parser(date)
            container['CITIC'] = tag
            collector.append(pd.DataFrame.from_dict(container))
        return pd.concat(collector, axis=0).drop_duplicates(subset = ['dt', 'Ticker'], keep = 'first').set_index(['dt', 'Ticker'])
    return decorate


def get_CITIC_range(start_date, end_date, level):
    collector = list()
    get_CITIC3_info = CITIC_helper(level=level)
    for ts in tdt.get_trading_date_range(start_date, end_date):
        collector.append(get_CITIC3_info(ts))
    return pd.concat(collector, axis=0)


def forge_CITIC_index(start_date, end_date, level=3, base_point=1000, mode='create'):
    assert mode == 'create'
#    h5_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.INDEX, ftype=FType.MD,
#                                dfreq=DFreq.MINUTE, dsource=eval(f'DSource.CITIC{level}'), dtable=None,
#                                alt=None, h5root=private_h5root)
    h5_path = '/data/user/015626/data/share/MD/CHINA_INDEX/CITIC'+str(level)+'/full_MD_CHINA_INDEX_MINUTE_CITIC' + str(level) + '_' + str(end_date) +'.h5'
#    append_mode, from_scratch = ut.h5_helper(h5_path, mode)
    minute_data = retrieve_stock_minute(start_date, end_date)
    citic_info = get_CITIC_range(start_date, end_date, level=level)
    minute_unstacked = minute_data.unstack()
    price_unstacked = minute_unstacked[['open', 'high', 'low', 'close', 'vwap']].fillna(method='pad')
    minute_return = (price_unstacked / price_unstacked.shift(1) - 1).fillna(0).stack()
    citic_info = citic_info['CITIC'].unstack().reindex(price_unstacked.index, method='pad').stack()
    minute_return['citic'] = citic_info
    citic_index_price = ((minute_return.groupby(['dt', 'citic']).mean().unstack() + 1).cumprod() * base_point).stack()
    minute_vol = minute_data[['volume', 'amt']].fillna(0)
    minute_vol['citic'] = citic_info
    citic_index_vol = minute_vol.groupby(['dt', 'citic']).sum()
    citic_index = pd.concat([citic_index_price, citic_index_vol], axis=1)
    citic_index['trading_day'] = pd.to_datetime(citic_index.index.get_level_values(level=0).date)
    # dump to h5 file
    citic_index.index.names = ['dt', 'Ticker']
#    IO.pd_hdf5_writer(citic_index, h5_path, 'CITIC', append=append_mode, from_scratch=from_scratch)
    IO.pd_hdf5_writer(citic_index, h5_path, 'CITIC')
    return citic_index


if __name__ == '__main__':
    forge_CITIC_index(20180101, 20200123, level=1)

