import sys

sys.path.append('/data/user/015836/HANXU/alphaResearch/dataUpdate/')

import os
import re
import gc
import time
from memory_profiler import profile
import pandas as pd

# from TSmodel.MorningModel.AlgoCSResearch.Timing.Tool import *
from dataApi.stockList import clean_stock_list, trans_windcode2int
from dataApi.tradeDate import trade_minutes, get_date_range, get_pre_trade_date
from HFfactor.MinFactorSuper.Utility.LoadBigData import get_minute_data
from dataApi import aimr
from .Tool import clip_stats, cs_kurt, cs_skew, check_data, winsorize
import numpy as np


def play_aimr(idd, parts, func, iter_list):
    todo_list = iter_list[idd::parts]
    for package in todo_list:
        try:
            if isinstance(package, (tuple, list)):
                func(*package)
            else:
                func(package)
        except:
            print('ERROR', package)
            continue


def get_fix_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/FixRoll/data/'):
    if restore:
        factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        factor_list = sorted(list({x[8:-4] for x in os.listdir(
            factor_address) if re.match('^Fix1[0134][03]0_', x)}))
        factor_list = sorted([x for x in factor_list if len([y for y in os.listdir(
            factor_address) if x in y and len(x) == len(y) - 12]) == len(freq)])
    else:
        remove_list = ['idx_date', 'idx_time', 'idx_code', 'nolimit', 'future', 'raw_idx_date', 'raw_idx_code']
        factor_list = sorted(
            [x[:-4] for x in os.listdir(factor_address) if (x[:-4] not in remove_list) & (x[0] != '_')])
    return factor_list


def load_pickle_frame(file_name, date_list, code_list, stock_pool):
    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex(date_list, code_list).values
        df[~ stock_pool] = np.nan
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x] for x in freq)].transpose(1, 0, 2)


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
        np.save(f'{address}/{k}_{name}.npy', stats[k])
    pd.to_pickle(check, f'{address}/../Temp/check_{name}.pkl')


def get_stock_pool(start_date, end_date):
    date_list = get_date_range(start_date, end_date)
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=5, least_normal_days=0,
                                  no_pause=True, least_recover_days=0, no_pause_limit=0,
                                  no_pause_stats_days=0, no_limit_up=False, no_limit_down=False,
                                  limit_range=None, other_limit=None, start_date=date_list[0],
                                  end_date=date_list[-1], trade_mode=True)
    code_list = stock_pool.columns.to_list()
    stock_pool = stock_pool.values
    return date_list, code_list, stock_pool


fix_store_path = '/arch1/user/015836/HFmodel/Timing/FixFactor/factor/'
date_list, code_list, stock_pool = get_stock_pool(20140601, 20211231)
factor_list = get_fix_factor_list(True)


# @profile
def _func(file_name, line=0):
    factor = load_pickle_frame(file_name, date_list, code_list, stock_pool)
    cs_stats_x(factor, file_name, fix_store_path)
    del factor
    gc.collect()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), file_name)


idd, parts = eval(aimr.getParam())
play_aimr(idd, parts, _func, factor_list)

# 单元测试
# %time
# @profile
# _func(factor_list[0])

#####################################################################################################
def find_trade_min(sign_min, delay_min=1, order_keep_min=5):
    sign_min = sign_min if sign_min < 242 else trade_minutes.index(sign_min)
    trade_min = [sign_min + delay_min + x for x in range(order_keep_min)]
    if trade_min[0] >= 241:
        trade_min = [242]
    elif trade_min[-1] >= 238:
        trade_min = list(range(min(trade_min[0], 238), 242))
    if len(trade_min) > order_keep_min:
        trade_min = trade_min[:order_keep_min - 1] + [241]
    elif trade_min == [242]:
        trade_min = [242] * order_keep_min
    elif len(trade_min) < order_keep_min:
        trade_min = trade_min + [241] * (order_keep_min - len(trade_min))
    return trade_min


future_days = 3
period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
future_end_date = get_pre_trade_date(date_list[-1], - future_days)
future_date_list = get_date_range(date_list[0], future_end_date)
future = get_minute_data('close_adj', future_date_list, code_list).reshape(-1, len(code_list))
date_num = len(date_list)

buy_idx = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    x, 1, 30) for x in period_list])[None, :, :]

buy_pr = np.nanmean(future[buy_idx], axis=2)

nolimit = get_minute_data('limit_status', date_list, code_list) == 0
nolimit = nolimit.reshape(len(date_list), 242, len(code_list))[
          :, [trade_minutes.index(x) for x in period_list]]
nolimit &= stock_pool[:, None]
buy_pr[~ nolimit] = np.nan

sell_idx_f1d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    x, 1, 30) for x in period_list])[None, :, :] + 242 * 1
sell_idx_f2d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    x, 1, 30) for x in period_list])[None, :, :] + 242 * 2
sell_idx_f3d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    x, 1, 30) for x in period_list])[None, :, :] + 242 * 3
sell_idx_1000f1d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    1000, 1, 30) for x in period_list])[None, :] + 242 * 1
sell_idx_1000f2d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    1000, 1, 30) for x in period_list])[None, :] + 242 * 2
sell_idx_1000f3d = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    1000, 1, 30) for x in period_list])[None, :] + 242 * 3
sell_idx_30f = np.arange(date_num)[:, None, None] * 242 + np.asanyarray([find_trade_min(
    x, 1, 30) for x in period_list])[None, :, :] + 30

f1d30 = np.nanmean(future[sell_idx_30f], axis=2) / buy_pr - 1
f1d242 = np.nanmean(future[sell_idx_f1d], axis=2) / buy_pr - 1
f2d242 = np.nanmean(future[sell_idx_f2d], axis=2) / buy_pr - 1
f3d242 = np.nanmean(future[sell_idx_f3d], axis=2) / buy_pr - 1
f1d1000 = np.nanmean(future[sell_idx_1000f1d], axis=2) / buy_pr - 1
f2d1000 = np.nanmean(future[sell_idx_1000f2d], axis=2) / buy_pr - 1
f3d1000 = np.nanmean(future[sell_idx_1000f3d], axis=2) / buy_pr - 1

p1d30 = np.nanmean(np.sign(f1d30), axis=-1)
p1d242 = np.nanmean(np.sign(f1d242), axis=-1)
p2d242 = np.nanmean(np.sign(f2d242), axis=-1)
p3d242 = np.nanmean(np.sign(f3d242), axis=-1)
p1d1000 = np.nanmean(np.sign(f1d1000), axis=-1)
p2d1000 = np.nanmean(np.sign(f2d1000), axis=-1)
p3d1000 = np.nanmean(np.sign(f3d1000), axis=-1)

np.save(f'{fix_store_path}/../label/p1d30.npy', np.ascontiguousarray(p1d30))
np.save(f'{fix_store_path}/../label/p1d242.npy', np.ascontiguousarray(p1d242))
np.save(f'{fix_store_path}/../label/p2d242.npy', np.ascontiguousarray(p2d242))
np.save(f'{fix_store_path}/../label/p3d242.npy', np.ascontiguousarray(p3d242))
np.save(f'{fix_store_path}/../label/p1d1000.npy', np.ascontiguousarray(p1d1000))
np.save(f'{fix_store_path}/../label/p2d1000.npy', np.ascontiguousarray(p2d1000))
np.save(f'{fix_store_path}/../label/p3d1000.npy', np.ascontiguousarray(p3d1000))

wf1d30 = np.nanmean(winsorize(f1d30), axis=-1)
wf1d242 = np.nanmean(winsorize(f1d242), axis=-1)
wf2d242 = np.nanmean(winsorize(f2d242), axis=-1)
wf3d242 = np.nanmean(winsorize(f3d242), axis=-1)
wf1d1000 = np.nanmean(winsorize(f1d1000), axis=-1)
wf2d1000 = np.nanmean(winsorize(f2d1000), axis=-1)
wf3d1000 = np.nanmean(winsorize(f3d1000), axis=-1)

np.save(f'{fix_store_path}/../label/wf1d30.npy', np.ascontiguousarray(wf1d30))
np.save(f'{fix_store_path}/../label/wf1d242.npy', np.ascontiguousarray(wf1d242))
np.save(f'{fix_store_path}/../label/wf2d242.npy', np.ascontiguousarray(wf2d242))
np.save(f'{fix_store_path}/../label/wf3d242.npy', np.ascontiguousarray(wf3d242))
np.save(f'{fix_store_path}/../label/wf1d1000.npy', np.ascontiguousarray(wf1d1000))
np.save(f'{fix_store_path}/../label/wf2d1000.npy', np.ascontiguousarray(wf2d1000))
np.save(f'{fix_store_path}/../label/wf3d1000.npy', np.ascontiguousarray(wf3d1000))

f1d30 = np.nanmean(f1d30, axis=-1)
f1d242 = np.nanmean(f1d242, axis=-1)
f2d242 = np.nanmean(f2d242, axis=-1)
f3d242 = np.nanmean(f3d242, axis=-1)
f1d1000 = np.nanmean(f1d1000, axis=-1)
f2d1000 = np.nanmean(f2d1000, axis=-1)
f3d1000 = np.nanmean(f3d1000, axis=-1)

np.save(f'{fix_store_path}/../label/f1d30.npy', np.ascontiguousarray(f1d30))
np.save(f'{fix_store_path}/../label/f1d242.npy', np.ascontiguousarray(f1d242))
np.save(f'{fix_store_path}/../label/f2d242.npy', np.ascontiguousarray(f2d242))
np.save(f'{fix_store_path}/../label/f3d242.npy', np.ascontiguousarray(f3d242))
np.save(f'{fix_store_path}/../label/f1d1000.npy', np.ascontiguousarray(f1d1000))
np.save(f'{fix_store_path}/../label/f2d1000.npy', np.ascontiguousarray(f2d1000))
np.save(f'{fix_store_path}/../label/f3d1000.npy', np.ascontiguousarray(f3d1000))