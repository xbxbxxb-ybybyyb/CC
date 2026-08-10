import pandas as pd
import numpy as np
import os
import sys
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.common as ut
import multifactor.utility.dt as tdt
from multifactor.snippet.stage_sync import send_file
import datetime
import bottleneck as bk
import shutil as stl
import zipfile
import json
import ctypes
from numpy.ctypeslib import ndpointer
from tqdm import tqdm
from functools import partial
import seaborn as sns
import matplotlib.pyplot as plt
from multifactor.commodity.factor_test_ts import ts_segment_test

CCBOND_MINUTE_PATH = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5'
CCBOND_CONVERSION_PATH = '/data/group/800080/warehouse/prod/DATABASE/WIND/CCBondConversion/CCBondConversion.h5'
CCBOND_RATING_PATH = '/data/group/800080/warehouse/prod/DATABASE/WIND/CBondRating/CBondRating.h5'
CCBOND_INFO_PATH = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv'
CCBOND_BLACKLIST_PATH = '/data/user/012245/projects/SimHF/ccbond/blacklist.csv'
STOCK_BLACKLIST_PATH = '/data/user/012245/projects/SimHF/genesis/scripts/blacklist.csv'
PROJECT_ROOT_PATH = '/data/user/012245/projects/SimHF/ccbond/'
REQUIRED_COLS = ['open', 'high', 'low', 'close', 'volume', 'amount']

morning_start_time = datetime.time(9, 25)
morning_end_time = datetime.time(9, 40)
mid_job_time = datetime.time(14, 0)
ref_close_start_time = datetime.time(14, 30)
ref_close_end_time = datetime.time(14, 44)
afternoon_start_time = datetime.time(14, 45)
afternoon_end_time = datetime.time(15, 0)
stock_ref_limit_end_time = datetime.time(14, 43)

def ccbond_transformer(ccbond):
    ccbond = ccbond.reset_index()
    ccbond['date'] = pd.to_datetime(ccbond.dt.dt.date)
    ccbond['close'] = ccbond['close'].where(ccbond['volume'] != 0, other=np.nan)
    morning_ccbond = ccbond.set_index('dt').between_time(morning_start_time, morning_end_time)
    afternoon_ccbond = ccbond.set_index('dt').between_time(afternoon_start_time, afternoon_end_time)
    morning_close = morning_ccbond.groupby(['date', 'Ticker'])['close'].mean()
    afternoon_close = afternoon_ccbond.groupby(['date', 'Ticker'])['close'].mean()
    morning_close.index.names = ['dt', 'Ticker']
    afternoon_close.index.names = ['dt', 'Ticker']
    # calculate expected returns
    ref_gap = (morning_close.unstack().shift(-1) / afternoon_close.unstack() - 1).stack()
    ref_gap.name = 'label'
    # calculate historical std
    ref_std = ccbond.set_index(['dt', 'Ticker'])['close'].unstack().pct_change(periods=5).rolling(240 * 10, min_periods=240).std().stack()
    ref_std.name = 'std'
    ref_std = ref_std.reset_index()
    ref_std['date'] = pd.to_datetime(ref_std['dt'].dt.date)
    ref_std = ref_std.set_index('dt').between_time(morning_start_time, ref_close_end_time).groupby(['date', 'Ticker'])['std'].mean()
    ref_std.index.names = ['dt', 'Ticker']
    # calculate historical amt
    ref_amt = ccbond.set_index('dt').between_time(morning_start_time, ref_close_end_time).groupby(['date', 'Ticker'])['amount'].sum()
    ref_amt.name= 'amt'
    ref_amt.index.names = ['dt', 'Ticker']
    # slice ref close
    ref_close = ccbond.set_index('dt').between_time(ref_close_start_time, ref_close_end_time).groupby(['date', 'Ticker'])['close'].mean()
    ref_close.name= 'close'
    ref_close.index.names = ['dt', 'Ticker']
    # calculate intraday gains
    ref_intra = ref_close / morning_close - 1
    ref_intra.name = 'return'
    ref_intra.index.names = ['dt', 'Ticker']
    return ccbond, ref_std, ref_amt, ref_close, ref_gap, ref_intra


def retrieve_ccbond_data(start_date, end_date):
    ccbond = IO.read_data([start_date, end_date], alt=CCBOND_MINUTE_PATH)
    return ccbond_transformer(ccbond)


def ccbond_historical_dumper(ref_date=None, look_back_days=60):
    if ref_date is None:
        ref_date = IO.str_date_parser(pd.Timestamp.now().strftime('%Y%m%d'))
    else:
        ref_date = IO.str_date_parser(ref_date)
    ccbond_ref_date = tdt.get_trading_day_offset(ref_date, -look_back_days)[0]
    ccbond = IO.read_data([ccbond_ref_date, ref_date], columns=REQUIRED_COLS, alt=CCBOND_MINUTE_PATH)
    out_path = os.path.join(PROJECT_ROOT_PATH, 'Data', 'History', ref_date.strftime('%Y%m%d'))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    ccbond.to_hdf(os.path.join(out_path, 'ccbond_kline_1min_history.h5'), 'ccbond_kline_1min')
    return ccbond


def get_ccbond_blacklist(ref_date, ref_gap, ref_intra, ref_amt, universe, redemption_ban_periods=30, historical_wr_limit=0.4, ipo_ban_periods=10):
    # redemption blacklist
    ccbond_conv = pd.read_hdf(CCBOND_CONVERSION_PATH)
    ccbond_dt_last = ccbond_conv.reset_index('dt')['TRADE_DT_LAST'].dropna()
    ccbond_dt_last = pd.to_datetime(ccbond_dt_last.astype('int'), format='%Y%m%d')
    dt_days = (ccbond_dt_last - ref_date).dt.days
    redemption_list = set(dt_days.loc[dt_days.abs() <= redemption_ban_periods].sort_values().index)
    # amount jump blacklist
    ref_amt_unstacked = ref_amt.unstack().fillna(0)
    amt_jump = ref_amt_unstacked / ref_amt_unstacked.shift()
    amt_jump = amt_jump.stack().reindex(ref_intra.index)
    amt_jump = amt_jump.where(ref_intra >= 0.0, other=-amt_jump).loc[ref_date]
    amt_jump_blacklist = set(amt_jump.loc[(amt_jump >= 50) | (amt_jump <= -1.5)].index)
    # amount decay blacklist
    amt_ratio = ref_amt_unstacked / ref_amt_unstacked.rolling(10, min_periods=1).max()
    amt_ratio = amt_ratio.rolling(5, min_periods=1).mean().stack().reindex(ref_intra.index)
    amt_ratio = amt_ratio.where(ref_intra >= 0.0, other=-amt_ratio).loc[ref_date]
    amt_decay_blacklist = set(amt_ratio.loc[(amt_ratio < 0) & (amt_ratio >= -0.15)].index)
    # stock limit price blacklist
    ccbond_info = pd.read_csv(CCBOND_INFO_PATH)
    ccbond_stock_pd = pd.read_hdf(os.path.join(PROJECT_ROOT_PATH, 'Data', 'Hot', ref_date.strftime('%Y%m%d'),
                                               'ccbond_stock_kline_1min_%s_%s.h5' % (morning_start_time.strftime('%H%M%S'), stock_ref_limit_end_time.strftime('%H%M%S'))))
    mdconstant = pd.read_hdf(os.path.join(PROJECT_ROOT_PATH, 'Data', 'Hot', ref_date.strftime('%Y%m%d'), 'mdconstant.h5'))
    stock_high_pd = ccbond_stock_pd['high'].unstack().max()
    stock_low_pd = ccbond_stock_pd['low'].unstack().min()
    limit_pd = stock_high_pd == mdconstant['limit'].reindex(stock_high_pd.index)
    limit_stocks = set(limit_pd.loc[limit_pd].index)
    stop_pd = stock_low_pd == mdconstant['stopping'].reindex(stock_low_pd.index)
    stop_stocks = set(stop_pd.loc[stop_pd].index)
    stock_limit_filter_set = limit_stocks | stop_stocks
    stock_limit_blacklist = set(ccbond_info.loc[ccbond_info['stockcode'].isin(stock_limit_filter_set)]['Ticker'])
    # bond rating blacklist
    ccbond_rating = pd.read_hdf(CCBOND_RATING_PATH)
    universe_rating = ccbond_rating.loc[(slice(None), universe), 'B_INFO_CREDITRATING'].sort_index().groupby(level='Ticker').last()
    rating_blacklist = set(universe_rating.loc[(~universe_rating.str.contains('A')) | (universe_rating == 'A') | (universe_rating == 'A-')].index)
    # stock blacklist
    stock_blacklist = pd.read_csv(STOCK_BLACKLIST_PATH)
    stock_blacklist = set(ccbond_info.loc[ccbond_info['stockcode'].isin(stock_blacklist['Ticker'])]['Ticker'])
    # historical winning rate blacklist
    wr_ref_date = tdt.get_trading_day_offset(ref_date, -1)[0]
    ref_gap_unstacked = ref_gap.unstack()
    wr_blacklist = set()
    for roll_window in [20, 40, 60]:
        gap_wr = ((ref_gap_unstacked > 0).rolling(roll_window, min_periods=roll_window // 2).sum() / roll_window).stack()
        num_wrt = ref_gap_unstacked.rolling(roll_window, min_periods=roll_window // 2).count().stack()
        gap_wr = gap_wr.reindex(num_wrt.loc[num_wrt >= roll_window // 2].index).reindex(ref_gap.index).dropna()
        wr_ref_wr = gap_wr.loc[wr_ref_date]
        wr_blacklist = wr_blacklist | set(wr_ref_wr.loc[wr_ref_wr <= historical_wr_limit].index)
    # newly listed blacklist
    listed_days = (ref_date - pd.to_datetime(ccbond_info.set_index('Ticker')['LISTEDDATE'].dropna().astype('int'), format='%Y%m%d')).dt.days
    ipo_blacklist = set(listed_days.loc[listed_days <= ipo_ban_periods].index)
    # ccbond blacklist
    ccbond_blacklist = set(pd.read_csv(CCBOND_BLACKLIST_PATH, index_col=0).index)
    return redemption_list | amt_jump_blacklist | amt_decay_blacklist | stock_limit_blacklist | \
           rating_blacklist | stock_blacklist | wr_blacklist | ipo_blacklist | ccbond_blacklist

def ccbond_trader(ref_date, std_lim, amt_lim, close_lim, num_lim, return_lim):
    if ref_date is None:
        ref_date = IO.str_date_parser(pd.Timestamp.now().strftime('%Y%m%d'))
    else:
        ref_date = IO.str_date_parser(ref_date)
    # read historical data
    historical_data = pd.read_hdf(os.path.join(PROJECT_ROOT_PATH, 'Data', 'History', ref_date.strftime('%Y%m%d'),
                                                                  'ccbond_kline_1min_history.h5'))
    print('READ HISTORICAL DATA')
    # read hot mid data
    hot_mid_data = pd.read_hdf(os.path.join(PROJECT_ROOT_PATH, 'Data', 'Hot', ref_date.strftime('%Y%m%d'),
                                            'ccbond_kline_1min_%s_%s.h5' % (morning_start_time.strftime('%H%M%S'), mid_job_time.strftime('%H%M%S'))))
    print('READ MID JOB DATA')
    # read hot data
    hot_last_data = pd.read_hdf(os.path.join(PROJECT_ROOT_PATH, 'Data', 'Hot', ref_date.strftime('%Y%m%d'),
                                             'ccbond_kline_1min_%s_%s.h5' % (mid_job_time.strftime('%H%M%S'), ref_close_end_time.strftime('%H%M%S'))))
    print('READ LAST JOB DATA')
    # merge data
    ccbond = pd.concat([historical_data[REQUIRED_COLS],
                        hot_mid_data[REQUIRED_COLS],
                        hot_last_data[REQUIRED_COLS]], axis=0)
    print('DATA CONCATENATION FINISH')
    _, ref_std, ref_amt, ref_close, ref_gap, ref_intra = ccbond_transformer(ccbond)
    print('TRANSFORMATION FINISH')
    _ref_std = ref_std.loc[ref_date]
    _ref_amt = ref_amt.loc[ref_date]
    _ref_close = ref_close.loc[ref_date]
    _ref_intra = ref_intra.loc[ref_date]
    std_filtered = set(_ref_std.loc[_ref_std >= std_lim].index)
    amt_filtered = set(_ref_amt.loc[_ref_amt >= amt_lim].index)
    close_filtered = set(_ref_close.loc[_ref_close >= close_lim].index)
    return_filtered = set(_ref_intra.loc[_ref_intra >= return_lim].index)
    print('POST STD NUM: %d\nPOST AMT NUM: %d\nPOST CLOSE NUM: %d\nPOST RETURN NUM: %d' % (len(std_filtered), \
                                                                                           len(amt_filtered), \
                                                                                           len(close_filtered), \
                                                                                           len(return_filtered)))
    selected_tickers = std_filtered & amt_filtered & close_filtered & return_filtered
    print('TOTAL LEFT NUM: %d' % len(selected_tickers))
    # retrieve blacklist
    blacklist = get_ccbond_blacklist(ref_date, ref_gap, ref_intra, ref_amt, selected_tickers)
    candidate_tickers = selected_tickers - blacklist
    print('FINAL CANDIDATES NUM: %d' % len(candidate_tickers))
    clipped_tickers = list(_ref_amt.reindex(candidate_tickers).sort_values().tail(num_lim).index)
    print('FINAL SELECTED NUM: %d' % len(clipped_tickers))
    # retrieve ref close for trading
    trade_price_ref = ccbond['close'].unstack().fillna(method='pad').iloc[-1, :]
    out_path = os.path.join(PROJECT_ROOT_PATH, 'Data', 'Trade', ref_date.strftime('%Y%m%d'))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    ut.dump_json(os.path.join(out_path, 'target.json'), {'target': clipped_tickers,
                                                         'ref_price': trade_price_ref.to_dict()})
    # send signals
    send_file(out_path, 'target.json', f'CCBond_{ref_date:%Y%m%d}.sig')
    return clipped_tickers


def eval_predict_score(start_date, end_date, return_series, ref_std, ref_amt, ref_close, ref_intra, num_ref,
                       std_lim=0.006, amt_lim=1E8, close_lim=130, num_lim=30, return_lim=-0.025, trading_fee=0.002):
    assert isinstance(return_series, pd.Series)
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    ret_ref = (return_series - trading_fee).loc[start_date:end_date]
    ret_ref = ret_ref.reindex(ref_std.loc[ref_std >= std_lim].index).reindex(\
                              ref_amt.loc[ref_amt >= amt_lim].index).reindex(\
                              ref_close.loc[ref_close >= close_lim].index).reindex(\
                              ref_intra.loc[ref_intra >= return_lim].index).dropna()
    filter_final_y = ret_ref.reindex(num_ref.reindex(ret_ref.index).groupby(pd.Grouper(level=0)).nlargest(num_lim).reset_index(level=0, drop=True).index)
    wr = filter_final_y.loc[filter_final_y > 0].size / filter_final_y.size
    wlr = abs(filter_final_y.loc[filter_final_y > 0].mean() / filter_final_y.loc[filter_final_y < 0].mean())
    oc = filter_final_y.groupby(pd.Grouper(level=0)).count()
    daily_pnl = filter_final_y.groupby(pd.Grouper(level=0)).mean() * oc / num_lim
    daily_pnl.cumsum().plot(figsize=(20, 5))
    oc.plot(figsize=(20, 5), secondary_y=True, linewidth=1.5, style='k-.', alpha=0.25)
    mdd = ut.max_drawdown_ts(daily_pnl.cumsum()).min()
    sharpe = daily_pnl.mean() / daily_pnl.std() * np.sqrt(242)
    calmar = daily_pnl.sum() / abs(mdd)
    daily_wr = daily_pnl.loc[daily_pnl > 0].size / daily_pnl.size
    kelly = (wlr * wr - (1 - wr)) / wlr
    print(f'daily winning rate: {daily_wr:.2%}, sharpe: {sharpe}, max drawdown: {mdd:.2%}, calmar ratio: {calmar}')
    print(f'sample winning rate: {wr:.2%}, win-loss ratio: {wlr}, kelly coef: {kelly}')
    print(oc.groupby(oc.index.year).mean().to_dict())
    return daily_pnl, filter_final_y


if __name__ == '__main__':
    ccbond_trader(ref_date=None, std_lim=0.0035, amt_lim=2.5E8, close_lim=110, num_lim=30, return_lim=-0.025)