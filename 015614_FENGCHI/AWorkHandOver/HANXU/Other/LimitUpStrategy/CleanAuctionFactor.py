import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import time
from multiprocessing import Pool

import os
import gc
import numpy as np
import pandas as pd
from xquant.marketdata import MarketData
from xquant.xqutils.helper import multicore_init

from dataApi.getData import get_daily_1factor
from dataApi.stockList import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range
from dataApi.stockList import clean_stock_list
from dataApi import aimr
from dataApi.sendInfo import send_file
from LimitUpStrategy.CallAuction import clean_tick_auction_data, calc_auction_factor

from TSmodel.MorningModel.PreprocessFactor import winsorize, standardize
from TSmodel.MorningModel.MorningDailyUpdate.DailyUpdate import infer_stock_pool

def get_ts_zscore_factor(factor, standardize_days=40):
    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0
    factor2 = factor ** 2
    d_cf = factor
    d_cf2 = factor2
    d_cn = factor_finite
    rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
        d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
        d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)
    rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
        d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
        d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)
    rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
        d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
        d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)
    rd_cn[rd_cn < standardize_days / 2] = np.nan
    factor[~ factor_finite] = np.nan
    rd_mean = (rd_cf / rd_cn)[:-1]
    rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[:-1]
    rd_std[rd_std == 0] = np.nan
    factor = (factor[standardize_days:] - rd_mean) / rd_std
    factor = np.pad(factor, ((standardize_days, 0), (0, 0)), mode='constant', constant_values=np.nan)
    return factor

def get_ma_factor(factor, standardize_days=5):
    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0
    d_cf = factor
    d_cn = factor_finite
    rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
        d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
        d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)
    rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
        d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
        d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)
    rd_cn[rd_cn < standardize_days / 2] = np.nan
    rd_mean = rd_cf / rd_cn
    rd_mean = np.pad(rd_mean, ((standardize_days - 1, 0), (0, 0)), mode='constant', constant_values=np.nan)
    return rd_mean

all_factor_list = [
    'T_tender_pct_mean', 'T_tender_pct_std', 'T_tender_max_up', 'T_tender_max_down', 'T_tender_mup',
    'T_tender_mup_len', 'T_tender_mdd', 'T_tender_mdd_len', 'T_tender_bid_amt_max_down', 'T_tender_ask_amt_max_down',
    'T_tender_bid_ff_rate_down', 'T_tender_ask_ff_rate_down', 'T_tender_bidask_amt_mean', 'T_tender_bidask_amt_std',
    'T_tender_bidask_ff_rate_mean', 'T_tender_bidask_ff_rate_std', 'T_tender_bidupask_rate', 'T_tender_bid_ff_rate',
    'T_tender_ask_ff_rate', 'T_tender_bidmask_ff_rate', 'T_tender_bidmask_amt', 'T_open_bid_amt', 'T_open_ask_amt',
    'T_open_bidask_amt', 'T_open_bid_ff_rate', 'T_open_ask_ff_rate', 'T_open_bidask_ff_rate', 'T_open_bidivask',
    'T_open_pct_bid2c', 'T_open_pct_ask2c', 'T_open_pct_bidask', 'T_open_main_bid_amt', 'T_open_main_ask_amt',
    'T_open_main_bidask_amt', 'T_open_main_bid_ff_rate', 'T_open_main_ask_ff_rate', 'T_open_main_bidask_ff_rate',
    'T_open_main_bidivask', 'T_open_main_pct_bid2c', 'T_open_main_pct_ask2c', 'T_open_main_pct_bidask', 'T_open_pct',
    'T_open_amt', 'T_auc1_pct', 'T_auc2_pct', 'T_auc1_climitup', 'T_auc1_climitdown', 'T_auc1_limitup',
    'T_auc1_limitdown', 'T_auc2_climitup', 'T_auc2_climitdown', 'T_auc2_limitup', 'T_auc2_limitdown', 'T_auc_climitup',
    'T_auc_climitdown', 'T_auc_limitup', 'T_auc_limitdown', 'T_auc2_upnum', 'T_auc2_downnum', 'T_auc2_updownnum',
    'T_auc_upnum', 'T_auc_downnum', 'T_auc_updownnum', 'T_auc1_upnum', 'T_auc1_downnum', 'T_auc1_updownnum'
]

amt_factor_list = [
    'T_tender_bid_amt_max_down', 'T_tender_ask_amt_max_down', 'T_tender_bidask_amt_mean', 'T_tender_bidask_amt_std',
    'T_tender_bidmask_amt', 'T_open_bid_amt', 'T_open_ask_amt', 'T_open_bidask_amt', 'T_open_main_bid_amt',
    'T_open_main_ask_amt', 'T_open_main_bidask_amt', 'T_open_amt'
]


stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                              no_pause=True, least_recover_days=1,
                              no_pause_limit=0.5, no_pause_stats_days=120,
                              no_limit_up=False, no_limit_down=False,
                              other_limit=None, trade_mode=False,
                              start_date=20130101, end_date=20211031)

data = pd.read_pickle(f'/arch1/user/015836/LimitUpStrategy2/data.pkl')
data['date'] = data['date'].map(int)
data['code'] = data['code'].map(int)

# col = all_factor_list[0]
for col in all_factor_list:
    factor = data.pivot('date', 'code', col).shift(-1).reindex_like(stock_pool)[stock_pool]
    Raw_factor = np.ascontiguousarray(factor.loc[20140801:].values[stock_pool.loc[20140801:].values], 'float32')
    np.save(f'/arch1/user/015836/LimitUpStrategy/restore/{col}.npy', Raw_factor)
    print(time.strftime('%Y-%m-%d %H:%M:%S'), col)

    factor.loc[:] = winsorize(factor.values)
    W_factor = np.ascontiguousarray(factor.loc[20140801:].values[stock_pool.loc[20140801:].values], 'float32')
    np.save(f'/arch1/user/015836/LimitUpStrategy/restore/W_{col}.npy', W_factor)

    if col in amt_factor_list:
        factor.loc[:] = winsorize(get_ts_zscore_factor(factor.values, standardize_days=40))

    WC_factor = factor.copy()
    WC_factor.loc[:] = standardize(WC_factor.values)
    WC_factor = np.ascontiguousarray(WC_factor.loc[20140801:].values[stock_pool.loc[20140801:].values], 'float32')
    # WC_factor[~ np.isfinite(WC_factor)] = 0
    np.save(f'/arch1/user/015836/LimitUpStrategy/restore/WC_{col}.npy', WC_factor)

    T40WC_factor = factor.copy()
    T40WC_factor.loc[:] = standardize(winsorize(get_ts_zscore_factor(T40WC_factor.values, standardize_days=40)))
    T40WC_factor = np.ascontiguousarray(T40WC_factor.loc[20140801:].values[stock_pool.loc[20140801:].values], 'float32')
    # T40WC_factor[~ np.isfinite(T40WC_factor)] = 0
    np.save(f'/arch1/user/015836/LimitUpStrategy/restore/T40WC_{col}.npy', T40WC_factor)

    LMA5_factor = factor.copy()
    LMA5_factor.loc[:] = standardize(winsorize(get_ma_factor(LMA5_factor.shift(1).values, standardize_days=5)))
    LMA5_factor = np.ascontiguousarray(LMA5_factor.loc[20140801:].values[stock_pool.loc[20140801:].values], 'float32')
    # LMA5_factor[~ np.isfinite(LMA5_factor)] = 0
    np.save(f'/arch1/user/015836/LimitUpStrategy/restore/LMA5_{col}.npy', LMA5_factor)
    print(time.strftime('%Y-%m-%d %H:%M:%S'), col)
