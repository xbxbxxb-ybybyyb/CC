import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from dataApi.sendInfo import send_message, send_file
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import pandas as pd
import numpy as np
import bottleneck
import torch
import shutil
import time
import os
import gc
import re

def load_timing_factor(name):
    address1 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/CrossFactor/'
    address2 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/factor/'
    address3 = '/data/group/800442/800319/Timing/FixFactor/FixFactor/HeredityFactor/'
    try:
        factor = np.load(f'{address1}/{name}.npy')
    except:
        try:
            factor = np.load(f'{address2}/{name}.npy')
        except:
            factor = np.load(f'{address3}/{name}.npy')
    return factor

def calc_time_corr(factor_list, direction, start_idx=146, end_idx=1364, pct=0.1, move_d=40, fix_bar=7, long=True):
    days = end_idx - start_idx + move_d
    move = move_d * fix_bar
    factor = np.empty((len(factor_list), days, fix_bar))
    for j, f in enumerate(factor_list):
        factor[j] = load_timing_factor(f)[start_idx - move_d + 1: end_idx + 1]
    factor *= np.asanyarray(direction)[:, None, None]
    if not long:
        factor *= -1
    corr = factor[:, move_d-1:].reshape(factor.shape[0], -1).copy()
    corr[~ np.isfinite(corr)] = 0
    corr = np.corrcoef(corr)
    common = factor.reshape(factor.shape[0], -1)
    nf = ~ np.isfinite(common)
    common[nf] = -np.inf
    x = bottleneck.move_rank(common, move, axis=-1)
    f = bottleneck.move_sum(nf.astype(x.dtype), move)
    x = ((x + 1) / 2 * (move - 1) - f) / np.fmax(move - f - 1, 1)
    common = x[:, move_d-1:] > max(pct, 1 - pct)
    num = common.sum(axis=1)
    common = common.astype('int') @ common.T.astype('int') * 2 / (num[:, None] + num[None, :])
    return corr, common

def corr_filter(corr, limit=0.7):
    corr = corr.copy()
    rank = np.arange(corr.shape[0])
    corr_triu = np.tril_indices(corr.shape[0])
    corr[corr_triu] = 0.
    corr_pool = corr.max(axis=0) < limit
    _corr_pool_num1 = 0
    _corr_pool_num2 = corr_pool.sum()
    while _corr_pool_num2 > _corr_pool_num1:
        _corr_pool_num1 = _corr_pool_num2
        corr[corr[corr_pool].max(axis=0) >= limit] = 0
        corr_pool = corr.max(axis=0) < limit
        _corr_pool_num2 = corr_pool.sum()
    return rank[corr_pool]

# Cross
address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewCrossFactorTest/'
factor_list = sorted(list(set([x[:-4] for x in os.listdir(address) if (
        x.endswith('.pkl') & (x[:-4] != 'CrossFactorTest'))])))
ins = {x: pd.read_pickle(f'{address}/{x}.pkl')['ins'] for x in factor_list[:1000]}

ins = pd.DataFrame(ins).T
ind_describe = ins.describe(percentiles=[
    0.01, 0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]).T

long_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['多头IC'] > 0) &
    (ins['多头占比'] > 0.08) &
    (ins['多头占比'] < 0.12) &
    (ins['多头收益'] > 0.0005) &
    (ins['多头策略相关性'] > 0.5)]

long_select['mix_IC'] = long_select['IC'] + long_select['多头IC']
long_select = long_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(long_select.index.to_list(), long_select['因子方向'].values)
long_select_corr = long_select.iloc[corr_filter(common, limit=0.7)]
long_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/CrossFactorLong.pkl')


short_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['空头IC'] > 0) &
    (ins['空头占比'] > 0.08) &
    (ins['空头占比'] < 0.12) &
    (ins['空头收益'] < -0.0005) &
    (ins['空头策略相关性'] > 0.5)]

short_select['mix_IC'] = short_select['IC'] + short_select['空头IC']
short_select = short_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(short_select.index.to_list(), short_select['因子方向'].values)
short_select_corr = short_select.iloc[corr_filter(common, limit=0.7)]
short_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/CrossFactorShort.pkl')


oos_long = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in long_select.index}
oos_long = pd.DataFrame(oos_long).T
oos_long = oos_long[
    (oos_long['因子方向'] == long_select['因子方向'])]

oos_short = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in short_select.index}
oos_short = pd.DataFrame(oos_short).T
oos_short = oos_short[
    (oos_short['因子方向'] == short_select['因子方向'])]


# Fix
address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewFixFactorTest/'
factor_list = sorted(list(set([x[:-4] for x in os.listdir(address) if (
        x.endswith('.pkl') & (x[:-4] != 'FixFactorTest'))])))
ins = {x: pd.read_pickle(f'{address}/{x}.pkl')['ins'] for x in factor_list}

ins = pd.DataFrame(ins).T
ind_describe = ins.describe(percentiles=[
    0.01, 0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]).T

long_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['多头IC'] > 0) &
    (ins['多头占比'] > 0.08) &
    (ins['多头占比'] < 0.12) &
    (ins['多头收益'] > 0.0005) &
    (ins['多头策略相关性'] > 0.7)]

long_select['mix_IC'] = long_select['IC'] + long_select['多头IC']
long_select = long_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(long_select.index.to_list(), long_select['因子方向'].values)
long_select_corr = long_select.iloc[corr_filter(common, limit=0.7)]
long_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/FixFactorLong.pkl')

short_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['空头IC'] > 0) &
    (ins['空头占比'] > 0.08) &
    (ins['空头占比'] < 0.12) &
    (ins['空头收益'] < -0.0005) &
    (ins['空头策略相关性'] > 0.7)]

short_select['mix_IC'] = short_select['IC'] + short_select['空头IC']
short_select = short_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(short_select.index.to_list(), short_select['因子方向'].values)
short_select_corr = short_select.iloc[corr_filter(common, limit=0.7)]
short_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/FixFactorShort.pkl')

oos_long = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in long_select.index}
oos_long = pd.DataFrame(oos_long).T
oos_long = oos_long[
    (oos_long['因子方向'] == long_select['因子方向'])]


oos_short = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in short_select.index}
oos_short = pd.DataFrame(oos_short).T
oos_short = oos_short[
    (oos_short['因子方向'] == short_select['因子方向'])]

# Heredity
address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewHeredityFactorTest/'
factor_list = sorted(list(set([x[:-4] for x in os.listdir(address) if (
        x.endswith('.pkl') & (x[:-4] != 'FixFactorTest'))])))
ins = {x: pd.read_pickle(f'{address}/{x}.pkl')['ins'] for x in factor_list}

ins = pd.DataFrame(ins).T
ind_describe = ins.describe(percentiles=[
    0.01, 0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]).T

long_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['多头IC'] > 0) &
    (ins['多头占比'] > 0.08) &
    (ins['多头占比'] < 0.12) &
    (ins['多头收益'] > 0.0005) &
    (ins['多头策略相关性'] > 0.7)]

short_select = ins[
    (ins['因子缺失率'] < 0.05) &
    (ins['IC'] > 0.07) &
    (ins['空头IC'] > 0) &
    (ins['空头占比'] > 0.08) &
    (ins['空头占比'] < 0.12) &
    (ins['空头收益'] < -0.0005) &
    (ins['空头策略相关性'] > 0.7)]

oos_long = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in long_select.index}
oos_long = pd.DataFrame(oos_long).T
oos_long = oos_long[
    (oos_long['因子方向'] == long_select['因子方向'])]

long_select['mix_IC'] = long_select['IC'] + long_select['多头IC']
long_select = long_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(long_select.index.to_list(), long_select['因子方向'].values)
long_select_corr = long_select.iloc[corr_filter(common, limit=0.7)]
long_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/HeredityFactorLong.pkl')

oos_short = {x: pd.read_pickle(f'{address}/{x}.pkl')['oos'] for x in short_select.index}
oos_short = pd.DataFrame(oos_short).T
oos_short = oos_short[
    (oos_short['因子方向'] == short_select['因子方向'])]

short_select['mix_IC'] = short_select['IC'] + short_select['空头IC']
short_select = short_select.sort_values(['mix_IC'], ascending=False)
corr, common = calc_time_corr(short_select.index.to_list(), short_select['因子方向'].values)
short_select_corr = short_select.iloc[corr_filter(common, limit=0.7)]
short_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/HeredityFactorShort.pkl')

long_select = pd.concat([
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/CrossFactorLong.pkl'),
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/FixFactorLong.pkl'),
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/HeredityFactorLong.pkl'),
])
corr, common = calc_time_corr(long_select.index.to_list(), long_select['因子方向'].values)
long_select_corr = long_select.iloc[corr_filter(common, limit=0.7)]
long_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/MixFactorLong.pkl')

short_select = pd.concat([
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/CrossFactorShort.pkl'),
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/FixFactorShort.pkl'),
    pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/HeredityFactorShort.pkl'),
])
corr, common = calc_time_corr(short_select.index.to_list(), short_select['因子方向'].values)
short_select_corr = short_select.iloc[corr_filter(common, limit=0.7)]
short_select_corr.to_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/MixFactorShort.pkl')