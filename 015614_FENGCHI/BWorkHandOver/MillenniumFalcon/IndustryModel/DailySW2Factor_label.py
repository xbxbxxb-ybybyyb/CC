# @Time : 2021/9/1 14:15
# @Author : Zhichen Lu
# @File : DailySW2Factor.py
import sys

sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])

import numpy as np
import pandas as pd
from CrossFT.basic.crossUtils import *
from CrossFT.basic.crossOperators import *
from online_conf import local_config_path
import itertools
from dataApi.LoadingTool import trans_df2arr
from tqdm import tqdm
from multiprocessing import Pool
from MillenniumFalcon.basic_conf import _date_list, _code_list,future_path
from dataApi.stockList import clean_stock_list


FACTOR_PATH = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
# FACTOR_PATH = '/data/group/800080/FactorFactory/PICKLE_DAY/'
# _date_list = get_date_range(20140701, 20210531)
# _code_list = np.load('/arch1/group/800442/800319/AAcross/basic/code_list.npy').tolist()
out_path = '/data/group/800442/800319/HFfactor/DailySW2PreNormalized/'
if not os.path.exists(out_path):
    os.makedirs(out_path)
factor_list = [x.replace('.pkl', '') for x in os.listdir(FACTOR_PATH)]
factor_list = list(filter(lambda x : not x.startswith('Fix'),factor_list))

def get_group_val(indicator, group, func):
    '''
    indicator:个股指标，用于合成组别指标
    group:个股分组情况，shape要和indicator相同
    func：组内计算方法, nansum, nanmean,nanmax,nanmin,nanmedian,nanstd,nanvar,nanquantile,自定义
    return: 返回的是个股横截面指标，index=time, columns= stock_pool
    '''
    groups = np.unique(group[np.isfinite(group)])
    shape = indicator.shape
    res = []
    for g in groups:
        val = group == g
        if len(shape) == 2:
            res.append(func(np.where(val, indicator, np.nan), axis=len(shape) - 1)[:, None])
        elif len(shape) == 3:
            res.append(func(np.where(val, indicator, np.nan), axis=len(shape) - 1)[:, :, None])
    return np.concatenate(tuple(res), axis=-1), groups.astype(int).tolist()

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

def _get_future(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=30):
    file_name = f'future{future_days}_{test_date_list[0]}_{test_date_list[-1]}_orderkeep{order_keep_min}_delay{delay_min}.npy'
    if os.path.exists((file_name)):
        print(file_name,'exist')
        future = np.load(file_name)
        return future
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_end_date = get_pre_trade_date(test_date_list[-1], - future_days)
    future_date_list = get_date_range(test_date_list[0], future_end_date)
    future = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    future = np.nanmean(future.values[idx], axis=2)
    future = future[future_days: test_date_num + future_days] / future[:test_date_num] - 1
    future = future.transpose(0, 2, 1)
    np.save(file_name,future)
    return future

def get_future(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=30):
    if isinstance(future_days,list):
        future = []
        for ft in tqdm(future_days):
            temp_res = _get_future(test_date_list, code_list, ft, delay_min, order_keep_min)
            future.append(temp_res[None,:])
        future = np.concatenate(tuple(future),axis=0)
        future = np.nanmean(future,axis=0)
    else:
        future = _get_future(test_date_list, code_list, future_days, delay_min, order_keep_min)
    return future

def get_all_stk_future_avg(future_days=1, delay_min=1, order_keep_min=30):
    future = get_future(test_date_list=_date_list, code_list=_code_list, future_days=future_days, delay_min=delay_min, order_keep_min=order_keep_min)
    future = future.swapaxes(1, 2)
    future[~np.isfinite(future)] = np.nan

    future_notnull = np.isfinite(future)
    future_daily_sum = np.nansum(future, axis=1)[:, None, :]
    future_daily_count = np.nansum(future_notnull, axis=1)[:, None, :]

    group_factor = get_daily_1factor('SW2')#.shift(1)
    group_factor = group_factor.loc[_date_list, _code_list].values[:, None, :]

    group_future_sum, group_list = get_group_val(future_daily_sum, group_factor, cross_sum)
    group_future_count, group_list_2 = get_group_val(future_daily_count, group_factor, cross_sum)
    group_label = group_future_sum / group_future_count
    group_label = pd.DataFrame(group_label[:, 0, :], index=_date_list, columns=group_list).shift(-1)
    return group_label

def get_all_stk_future_rise_pct(future_days=1, delay_min=1, order_keep_min=30):
    future = get_future(test_date_list=_date_list, code_list=_code_list, future_days=future_days, delay_min=delay_min, order_keep_min=order_keep_min)
    future = future.swapaxes(1, 2)
    future_notnull = np.isfinite(future)
    # future = future>0
    # future[~future_notnull] = np.nan
    future = np.where(future_notnull,future>0,np.nan)

    future_daily_sum = np.nansum(future, axis=1)[:, None, :]
    future_daily_count = np.nansum(future_notnull, axis=1)[:, None, :]

    group_factor = get_daily_1factor('SW2')#.shift(1)
    group_factor = group_factor.loc[_date_list, _code_list].values[:, None, :]

    group_future_sum, group_list = get_group_val(future_daily_sum, group_factor, cross_sum)
    group_future_count, group_list_2 = get_group_val(future_daily_count, group_factor, cross_sum)
    group_label = group_future_sum / group_future_count
    group_label = pd.DataFrame(group_label[:, 0, :], index=_date_list, columns=group_list).shift(-1)
    return group_label

def out_factor(factor_name):
    factor = pd.read_pickle(f'{FACTOR_PATH}{factor_name}.pkl')
    factor.index = factor.index.astype(int)
    factor.columns = factor.columns.map(trans_windcode2int)
    factor = factor.loc[_date_list, _code_list].values[:, None, :]
    # group_factor = load_material('sw2', _date_list[0], _date_list[-1],freq='daily', address='/arch1/group/800442/800319/AAcross/basic/groups/')

    group_factor = get_daily_1factor('SW2')#.shift(1)
    group_factor = group_factor.loc[_date_list, _code_list].values[:, None, :]

    sw_mean, group_list1 = get_group_val(factor, group_factor, cross_mean)  # [:,0,:]
    sw_std, group_list2 = get_group_val(factor, group_factor, cross_std)  # [:,0,:]
    if group_list1 != group_list2:
        print('group list not equal')
        raise Exception('gorup list not euqal')

    sw_mean = sw_mean[:, 0, :]
    sw_std = sw_std[:, 0, :]

    sw_sharpe = sw_mean / sw_std

    pd.DataFrame(sw_mean, index=_date_list, columns=group_list1).to_pickle(f'{out_path}mean/{factor_name}.pkl')
    pd.DataFrame(sw_std, index=_date_list, columns=group_list2).to_pickle(f'{out_path}std/{factor_name}.pkl')
    pd.DataFrame(sw_sharpe, index=_date_list, columns=group_list1).to_pickle(f'{out_path}zscore/{factor_name}.pkl')
    print(factor_name, 'done')


def main(n):
    bar = tqdm(total=len(factor_list))

    def update(*para):
        bar.update()
        if bar.last_print_n >= bar.total:
            bar.close()

    pool = Pool(n)
    for fname in factor_list:
        if os.path.exists(f'{out_path}zscore/{fname}.pkl'):
            continue
        pool.apply_async(out_factor, (fname,), callback=update)

    pool.close()
    pool.join()

if __name__ == '__main__':
    # res1_5 = get_future(_date_list,_code_list,[1,2,3,4,5])
    # np.save(f'{future_path}mean_1_to_5.npy',res1_5)
    # res_1_3_5 = get_future(_date_list,_code_list,[1,3,5])
    # np.save(f'{future_path}mean_1_3_5.npy', res_1_3_5)
    #
    # for i in [[1,2,3,4,5],[1,3,5],[1,2,3]]:
    #     stk_intraday_all_avg_label = get_all_stk_future_avg(future_days=i,order_keep_min=30)
    #     stk_intraday_rise_pct_label = get_all_stk_future_rise_pct(future_days=i,order_keep_min=30)
    #     pd.to_pickle(stk_intraday_rise_pct_label, f'{out_path}label/lable_group_stk_future_rise_pct_{"_".join(list(map(str,i)))}.pkl')
    #     pd.to_pickle(stk_intraday_all_avg_label, f'{out_path}label/lable_group_stk_future_avg_{"_".join(list(map(str,i)))}.pkl')

    for kind in ['label']:#['zscore','mean','std']:
        idx_date, idx_code = None, None
        if not os.path.exists(f'{out_path}{kind}_arr/'):
            os.makedirs(f'{out_path}{kind}_arr/')
        for f_name in tqdm(list(map(lambda x: x.replace('.pkl', ''), os.listdir(f'{out_path}{kind}/')))):
            if os.path.exists(f'{out_path}{kind}_arr/{f_name}.npy'):
                print(f_name,'exist')
                continue
            factor = pd.read_pickle(f'{out_path}{kind}/{f_name}.pkl')
            factor_arr = factor.values.flatten()
            if idx_date is None or idx_code is None:
                idx_date = factor.copy()
                idx_code = factor.copy()
                stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                              no_pause=True, least_recover_days=1,
                                              no_pause_limit=0.5, no_pause_stats_days=120,
                                              no_limit_up=False, no_limit_down=False,
                                              other_limit=None, trade_mode=False,
                                              start_date=factor.index[0], end_date=factor.index[-1])
                stock_pool_arr = stock_pool.values.flatten().astype('float32')
                stock_pool_arr = np.ascontiguousarray(stock_pool_arr)
                np.save(f'{out_path}/stock_pool.npy',stock_pool_arr)

                for col in idx_code.columns:
                    idx_code[col] = col
                for idx in idx_date.index:
                    idx_date.loc[idx] = idx
                idx_date, idx_code = np.ascontiguousarray(idx_date.values.flatten().astype(int)), np.ascontiguousarray(idx_code.values.flatten().astype(int))
                np.save(f'{out_path}{kind}_arr/idx_date.npy', idx_date)
                np.save(f'{out_path}{kind}_arr/idx_code.npy', idx_code)

            if factor_arr.shape != idx_date.shape:
                raise Exception('Factor shape not same to idx')
            factor_arr = np.ascontiguousarray(factor_arr.astype('float32'))
            np.save(f'{out_path}{kind}_arr/{f_name}.npy', factor_arr)

