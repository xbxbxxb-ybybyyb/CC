from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.IO.naming_config import *
from multifactor.factor.cfc_norm_ii import report_date_filter
from multifactor.preprocessing.cleansing import ts_rolling_normalize
import multifactor.utility.common as ut
import numbers
import pandas as pd
import numpy as np
import os


def forecast_citic(start_date, end_date, columns, forecast_year=1):
    if isinstance(columns, str):
        columns = [columns]
    mapper = {'CC10': 'ind1', 'CC11': 'ind2', 'CC12': 'ind3', 'CC20': 'ind4', 'CC21': 'ind5', 'CC22': 'ind6',
              'CC23': 'ind7', 'CC24': 'ind8', 'CC25': 'ind9', 'CC26': 'ind10', 'CC27': 'ind11', 'CC28': 'ind12',
              'CC30': 'ind13', 'CC31': 'ind14', 'CC32': 'ind15', 'CC33': 'ind16', 'CC34': 'ind17', 'CC35': 'ind18',
              'CC36': 'ind19', 'CC37': 'ind20', 'CC40': 'ind21', 'CC41': 'ind29', 'CC42': 'ind22', 'CC50': 'ind23',
              'CC60': 'ind24', 'CC61': 'ind25', 'CC62': 'ind26', 'CC63': 'ind27', 'CC70': 'ind28'}
    pd_raw = IO.read_data([start_date, end_date], columns=list(set(['STOCK_TYPE', 'RPT_DATE', 'RPT_TYPE']).union(set(columns))),
                           universe=list(mapper.keys()), dtable=DTable.con_forecast_zx, dsource=DSource.SUNTIME)
    filtered_pd = pd_raw[(pd_raw['STOCK_TYPE'] == 4) & (pd_raw['RPT_TYPE'] == 4)].drop(columns=['STOCK_TYPE', 'RPT_TYPE'])
    res = ut.pd_unstack(report_date_filter(filtered_pd, columns, forecast_year=forecast_year))
    if isinstance(res, dict):
        for k, v in res.items():
            res[k] = v.rename(columns=mapper)
    else:
        res = res.rename(columns=mapper)
    return res


def retrieve_morning_amount_adj(sd, ed, ref=None, raw=False):
    sd = IO.str_date_parser(sd)
    ed = IO.str_date_parser(ed) + pd.Timedelta('1D')
    collector = list()
    for ticker in ['000905', '000300']:
        spot_data = pd.read_pickle(os.path.join(minute_per_index_path, f'indexMinute_{ticker}.pkl'), compression='gzip')
        spot_data = spot_data.loc[spot_data.minute.isin([925])].reset_index()
        spot_data['dt'] = spot_data['dt'] * 1E6 + spot_data['minute'] * 100
        spot_data['dt'] = pd.to_datetime(spot_data['dt'].astype('int64'), format='%Y%m%d%H%M%S')
        spot_data = spot_data.set_index('dt').loc[(sd - pd.Timedelta('365D')):ed]['amt']
        spot_data.name = ticker
        collector.append(spot_data)
    market_amount = pd.concat(collector, axis=1).sum(axis=1)
    market_amount = market_amount.groupby(market_amount.index.date).sum()
    market_amount.index = pd.to_datetime(market_amount.index)
    if raw:
        return market_amount.loc[sd:ed]
    # calculate adjust factor range [0, 2]
    if ref is None:
        market_adj = ts_rolling_normalize(market_amount, 120, 60, method='NORM', std=0.35, cutoff=3).clip(-1, 1) + 1
        return market_adj.loc[sd:ed]
    else:
        # calculate just in time scale number for real time trading
        assert isinstance(ref, numbers.Number)
        market_amount = pd.Series(np.append(market_amount.values, ref))
        market_adj = ts_rolling_normalize(market_amount, 120, 60, method='NORM', std=0.35, cutoff=3).clip(-1, 1) + 1
        return market_adj.iloc[-1]


def get_stock_ref_price_between_time(date, begin_time, end_time, ref='close', ufunc='max'):
    date = IO.str_date_parser(date)
    min_pd = pd.read_pickle(os.path.join(minute_stock_per_date_path, date.strftime('%Y%m%d') + '.pkl'), compression='gzip')
    min_pd = min_pd.reset_index()
    min_pd['dt'] = min_pd['dt'] * 1E6 + min_pd['minute'] * 100
    min_pd['dt'] = pd.to_datetime(min_pd['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    min_pd['Ticker'] = min_pd['Ticker'].map(ut.ticker_match)
    min_pd = min_pd.set_index(['dt', 'Ticker'])
    min_pd = min_pd['close'].unstack()
    res = getattr(min_pd.between_time(begin_time, end_time), ufunc)()
    res.name = ufunc
    res = res.reset_index()
    res['dt'] = date
    res = res.set_index(['dt', 'Ticker'])[ufunc]
    return res

