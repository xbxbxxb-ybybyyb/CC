import sys

sys.path.append('/data/user/015836/HANXU/alphaResearch/dataUpdate/')

import os

from TSmodel.MorningModel.AlgoCSResearch.Timing.Tool import *
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range
from HFfactor.MinFactorSuper.Utility.Parallel import play_aimr
from dataApi import aimr
from .Tool import clip_stats, cs_kurt, cs_skew, check_data
import numpy as np
import pandas as pd

def get_stock_pool(start_date, end_date, code_list):
    date_list = get_date_range(start_date, end_date)
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=5, least_normal_days=0,
                                  no_pause=True, least_recover_days=0, no_pause_limit=0,
                                  no_pause_stats_days=0, no_limit_up=False, no_limit_down=False,
                                  limit_range=None, other_limit=None, start_date=date_list[0],
                                  end_date=date_list[-1], trade_mode=True)
    stock_pool = stock_pool.reindex(columns=code_list) > 0
    stock_pool = stock_pool.values
    return stock_pool


def get_sub_fold_file(path):
    sub_fold = sorted([x for x in os.listdir(path) if '.' not in x])
    file_list = []
    for sub in sub_fold:
        s_path = f'{path}/{sub}/'
        for f in os.listdir(s_path):
            if f.endswith('.npy'):
                file_list.append((f[:-4], sub))
    return file_list


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


cross_start_date = 20140701
cross_end_date = 20210531
test_start_date = 20140601
test_end_date = 20211231
start_fill = len(get_date_range(test_start_date, cross_start_date)) - 1
end_fill = len(get_date_range(cross_end_date, test_end_date)) - 1

save_address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/CrossFactor/'
m5_address = '/arch1/group/800442/800319/AAcross/factor_result_rerun9/5mins/20140701_20210531/'
daily_address = '/arch1/group/800442/800319/AAcross/factor_result_rerun9/daily/20140701_20210531/'
date_list = np.load('/arch1/group/800442/800319/AAcross/date_list.npy')
code_list = np.load('/arch1/group/800442/800319/AAcross/code_list.npy')
stock_pool = get_stock_pool(cross_start_date, cross_end_date, code_list)


def _func_m5(name, sub):
    factor = np.load(f'{m5_address}/{sub}/{name}.npy')[:, [5, 11, 17, 23, 29, 35, 41]]
    factor[~ stock_pool[:, None].repeat(7, axis=1)] = np.nan
    factor = np.pad(factor, ((start_fill, end_fill), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)
    cs_stats_x(factor, name, save_address, quantiles=(0.01, 0.05, 0.10, 0.25))


def _func_daily(name, sub):
    factor = np.load(f'{daily_address}/{sub}/{name}.npy').repeat(7, axis=1)
    factor[~ stock_pool[:, None].repeat(7, axis=1)] = np.nan
    factor = np.pad(factor, ((start_fill + 1, end_fill - 1), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)
    cs_stats_x(factor, name, save_address, quantiles=(0.01, 0.05, 0.10, 0.25))


m5_files = get_sub_fold_file(m5_address)
daily_files = get_sub_fold_file(daily_address)

idd, parts = eval(aimr.getParam())
play_aimr(idd, parts, _func_daily, daily_files)