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

from HFfactor.MinFactorSuper.Research.FactorVal import FactorVal
# from TSmodel.MorningModel.AlgoCSResearch.Timing.Tool import *
from HFfactor.MinFactorSuper.Utility.Parallel import multidask
from .Tool import *


def cs_stats_x(x, name, address, quantiles=(0.01, 0.05, 0.10, 0.25)):
    check = check_data(x)
    stats = {}
    stats['skew'] = cs_skew(x)
    stats['kurt'] = cs_kurt(x)
    stats['mean'], stats['std'], stats['sharpe'], stats['med'], stats['mad'], stats['medmad'] = clip_stats(x)
    for q in quantiles:
        q = q if q < 0.5 else 1 - q
        q1 = 1 - q
        min = str(int(q * 100)).zfill(2)
        max = str(int(q1 * 100)).zfill(2)
        stats[f'x{min}'] = np.nanquantile(x, q=q, axis=-1)
        stats[f'x{max}'] = np.nanquantile(x, q=q1, axis=-1)
        stats[f'mean{min}'], stats[f'std{min}'], stats[f'sharpe{min}'], stats[f'med{min}'], \
        stats[f'mad{min}'], stats[f'medmad{min}'] = clip_stats(x, max_clip=stats[f'x{min}'][..., None])
        stats[f'mean{max}'], stats[f'std{max}'], stats[f'sharpe{max}'], stats[f'med{max}'], \
        stats[f'mad{max}'], stats[f'medmad{max}'] = clip_stats(x, min_clip=stats[f'x{max}'][..., None])
        stats[f's{min}'] = stats[f'x{max}'] - stats[f'x{min}']
        stats[f'mean{min}s'], stats[f'std{min}s'], stats[f'sharpe{min}s'], stats[f'med{min}s'], stats[f'mad{min}s'], \
        stats[f'medmad{min}s'] = clip_stats(x, min_clip=stats[f'x{min}'][..., None],
                                            max_clip=stats[f'x{max}'][..., None])
    for k in stats.keys():
        np.save(f'{address}/{k}_{name}.npy', stats[k].astype('float64'))
    pd.to_pickle(check, f'{address}/Check/check_{name}.pkl')

address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/HeredityFactor/'
fv = FactorVal(20140701, 20211231, reduce=True, store='FactorFixData')


def calc_heredity_timing_factor(factor_line):
    name, formula = factor_line
    factor = fv.factor_val(factor_line)
    factor = factor[1:, [5, 11, 17, 23, 29, 35, 41]]
    factor[~ fv.stock_pool.repeat(7, axis=1)] = np.nan
    factor = np.pad(factor, ((20, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)
    try:
        cs_stats_x(factor, name, address)
    except:
        return
    del factor
    gc.collect()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), name)


def _func(sublist, line=0):
    for factor_line in sublist:
        calc_heredity_timing_factor(factor_line)

factor_line_list1 = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor/'
                                   'subscript_factor_list/desample_factor_list20211127.pkl')
factor_line_list1 = [(f'Ma{str(x).zfill(4)}', factor_line_list1[x][1]) for x in range(len(factor_line_list1))]

factor_line_list2 = pd.read_excel('/data/group/800442/800319/Timing/FixFactor/FixFactor/遗传除707之外的其他因子.xlsx')
factor_line_list2 = factor_line_list2['program_code'].to_list()
factor_line_list2 = [x for x in factor_line_list2 if ('dt_cum' not in x) & ('ds_cum' not in x)]
factor_line_list2 = [(f'Mb{str(x).zfill(4)}', factor_line_list2[x]) for x in range(len(factor_line_list2))]

factor_line_list3 = pd.read_excel('/data/group/800442/800319/Timing/FixFactor/FixFactor/fix5mins_passed.xlsx')
factor_line_list3 = factor_line_list3['program_code'].drop_duplicates().to_list()
factor_line_list3 = [x for x in factor_line_list3 if ('dt_cum' not in x) & ('ds_cum' not in x)]
factor_line_list3 = [(f'Mc{str(x).zfill(4)}', factor_line_list3[x]) for x in range(len(factor_line_list3))]

multidask('aaa', [(_func, [factor_line_list3[x::16]]) for x in range(16)])




# 统计增强K使用情况
MaterialList = [
    'turn_order_passive_sell',
    'turn_order_active_sell',
    'turn_order_passive_buy',
    'ret_order_passive_sell',
    'ret_order_passive_buy',
    'turn_order_active_buy',
    'ret_order_active_sell',
    'ret_order_active_buy',
    'turn_order_passive',
    'turn_order_active',
    'ret_order_passive',
    'ret_order_active',
    'turn_cancel_sell',
    'turn_trade_sell',
    'ret_cancel_sell',
    'turn_order_sell',
    'turn_cancel_buy',
    'turn_trade_buy',
    'num_total',
    'ret_order_sell',
    'ret_cancel_buy',
    'ret_trade_sell',
    'turn_order_buy',
    'turn_acc_sell',
    'ret_order_buy',
    'ret_trade_buy',
    'turn_acc_buy',
    'turn_cancel',
    'ret_cancel',
    'turn_order',
    'ret_trade',
    'ret_order',
    'num_sell',
    'turn_acc',
    'num_buy',
]

basic_list = [
    'ret_high_close',
    'ret_close_vwap',
    'ret_low_close',
    'turn_total',
    'ret_close',
    'adj_close',
    'ret_vwap',
    'pcf_hist',
    'peg_hist',
    'ret_high',
    'adj_high',
    'adj_opn',
    'ret_low',
    'adj_low',
    'adj_vol',
    'pe_hist',
    'pb_hist',
    'adj_amt',
    'pb_f1',
    'pe_f1',
    'pe_f2'
]
def isenhance(formula, factors):
    for f in factors:
        if f in formula:
            return True
    return False
factor_isenhance = [isenhance(x[1], MaterialList) for x in factor_line_list1]
factor_isenhance = np.asanyarray(factor_isenhance).sum()