import sys

import numpy as np
import pandas as pd

sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import get_date_range
from dataApi.getData import get_daily_1factor


def prepare_ind(ind_type='SW1', ind_modify=True, date_list=None, code_list=None, ind_address=None):
    if ind_modify:
        if ind_type == 'SW1':
            ind = get_daily_1factor('SW1', date_list, code_list, diy_address=ind_address)
            ind2 = get_daily_1factor('SW2', date_list, code_list, diy_address=ind_address)
            ind[ind == 6134] = ind2[ind == 6134]
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[np.isfinite(ind_codes)]))
        elif ind_type == 'CITICS1':
            ind = get_daily_1factor('CITICS1', date_list, code_list, diy_address=ind_address).replace(np.nan, 'nan')
            ind2 = get_daily_1factor('CITICS2', date_list, code_list, diy_address=ind_address).replace(np.nan, 'nan')
            ind[ind == 'b10m'] = ind2[ind == 'b10m']
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[ind_codes != 'nan']))
        else:
            raise ValueError("Only SW1 or CITICS1 can be modified.")
    else:
        ind = get_daily_1factor(ind_type, date_list, code_list, diy_address=ind_address)
        if np.dtype('O') in np.unique(ind.dtypes):
            ind = ind.replace(np.nan, 'nan')
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[ind_codes != 'nan']))
        else:
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[np.isfinite(ind_codes)]))

    return ind, ind_codes


def cal_ind_bias(factor, ind_type='SW1', bench='ZZ500'):
    ########先归一化###########
    factor = (factor.T / factor.sum(axis=1)).T
    #######先获取数据###############
    start_date = factor.index[0]
    end_date = factor.index[-1]
    date_list = get_date_range(start_date, end_date)  # 日期列表
    stock_list = get_daily_1factor('stock_list', date_list)  # 股票列表
    code_list = stock_list.columns.to_list()  # 股票列表
    ind, ind_codes = prepare_ind(ind_type=ind_type, date_list=date_list, code_list=code_list)  # 获取个股所属行业

    ###计算行业分布的情况：
    ind_result = pd.DataFrame(index=date_list, columns=ind_codes)
    for date in date_list:
        _ind = ind.loc[date]  # 获取个股对应的行业
        _X_ind = np.r_['0,2', tuple((_ind == x).values for x in ind_codes)]  # 获取个股属于哪一个行业
        ind_result.loc[date] = pd.Series(_X_ind @ factor.loc[date].reindex(code_list).fillna(0), index=ind_codes)

    ###4、基准行业分布情况：
    bench_weight = get_daily_1factor('%s_exdiv_weight' % bench, date_list, code_list).fillna(0)  # 基准权重

    bench_ind_result = pd.DataFrame(index=date_list, columns=ind_codes)
    for date in date_list:
        _ind = ind.loc[date]
        _bench_weight = bench_weight.loc[date]
        _bench_ind = \
        pd.concat([_bench_weight.rename('wgt'), _ind.rename('ind')], axis=1).replace('nan', np.nan).dropna().groupby(
            'ind')['wgt'].sum().reindex(ind_codes).fillna(0)
        bench_ind_result.loc[date] = _bench_ind

    ###计算一下行业偏离########
    ind_bias = ind_result - bench_ind_result
    return ind_bias, ind_result, bench_ind_result


def cal_MV_bias(factor, bench='ZZ500'):
    ########先归一化###########
    factor = (factor.T / factor.sum(axis=1)).T
    #######先获取数据###############
    start_date = factor.index[0]
    end_date = factor.index[-1]
    date_list = get_date_range(start_date, end_date)  # 日期列表
    stock_list = get_daily_1factor('stock_list', date_list)  # 股票列表
    code_list = stock_list.columns.to_list()  # 股票列表
    mv = np.log(get_daily_1factor('mkt_cap_ard', date_list, code_list)).fillna(0)  # 获取log市值
    #######市值偏离#######
    MV = (factor * mv).sum(axis=1)
    ########基准的市值偏离##########
    bench_weight = get_daily_1factor('%s_exdiv_weight' % bench, date_list, code_list).fillna(0)  # 基准权重
    bench_MV = (bench_weight * mv).sum(axis=1)
    bias = (MV - bench_MV) / bench_MV
    return bias
