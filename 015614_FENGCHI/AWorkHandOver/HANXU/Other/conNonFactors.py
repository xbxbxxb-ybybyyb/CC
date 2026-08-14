import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, trans_datetime2int
from dataApi.stockList import trans_windcode2int, trans_int2windcode
from dataApi.getData import get_daily_1factor, get_quarter_1factor, get_ind_neutral
from xquant.factordata import FactorData
from multiprocessing import Pool
fd = FactorData()

def multiprocess(lines, func, iterable, *args):
    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    for j in range(lines):
        sub_iter = iterable[j::lines]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args + (j,))
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

con_list = [
    'cfs_target_price', 'cfs_score', 'cfc2s_c2', 'cfc2s_c13', 'cfc2s_c9', 'cfc3s_cgb', 'cfc3s_cgpb', 'cfc3s_cgg', 'cfc3cs_cgb',
    'cfc3cs_cgpb', 'cfc3s_cgpeg', 'cfs_c1', 'cfs_c3', 'cfs_c4', 'cfs_c5', 'cfs_c6', 'cfs_c7', 'cfs_c80', 'cfs_c81',
    'cfs_c82', 'cfs_c83', 'cfs_c84', 'cfs_c12', 'cfs_cb', 'cfs_cpb', 'rating_up_number7', 'rating_up_number30',
    'rating_up_number90', 'rating_down_number7', 'rating_down_number30', 'rating_down_number90', 'report_number7',
    'report_number30', 'report_number90', 'author_number7', 'author_number30', 'author_number90', 'organ_number7',
    'organ_number30', 'organ_number90', 'buy_number7', 'buy_number30', 'buy_number90', 'overweight_number7',
    'overweight_number30', 'overweight_number90', 'neutral_number7', 'neutral_number30', 'neutral_number90',
    'underweight_number7', 'underweight_number30', 'underweight_number90', 'sell_number7', 'sell_number30',
    'sell_number90', 'csd_forward_pe_deviation5', 'csd_forward_pe_deviation25', 'csd_forward_pe_deviation75',
    'csd_forward_pb_deviation5', 'csd_forward_pb_deviation25', 'csd_forward_pb_deviation75', 'relative_report_number10',
    'relative_report_number25', 'relative_report_number75', 'organ_number10', 'organ_number25', 'organ_number75',
    'tcap', 'up_number7', 'up_number30', 'up_number90', 'down_number7', 'down_number30', 'down_number90',
    'eps_deviation5', 'eps_deviation25', 'eps_deviation75', 'ni_deviation5', 'ni_deviation25', 'ni_deviation75',
    'eps_stdev5', 'eps_stdev25', 'eps_stdev75', 'ni_stdev5', 'ni_stdev25', 'ni_stdev75', 'csd_pe_deviation5',
    'csd_pe_deviation25', 'csd_pe_deviation75', 'csd_pb_deviation5', 'csd_pb_deviation25', 'csd_pb_deviation75',
    'degree', 'stock_diversity', 'consensus_confidence5', 'consensus_confidence10', 'consensus_confidence15',
    'consensus_confidence25', 'consensus_confidence75', 'optimism_confidence5', 'optimism_confidence10',
    'optimism_confidence15', 'optimism_confidence25', 'optimism_confidence75', 'pessimism_confidence5',
    'pessimism_confidence10', 'pessimism_confidence15', 'pessimism_confidence25', 'pessimism_confidence75',
]

store_address = '/data/group/800442/800319/junkData/daily/'
factor_address='/data/group/800442/800319/BigDataFactor/BasicFactor/'
date = get_date_range(20100101)
_date = [str(x) for x in date]
parts = round(len(_date) / 150)

def _func(sub_list, line=0):
    for name in tqdm(sub_list):
        df = pd.concat([fd.get_factor_value('Basic_factor', mddate=_date[x::parts], factor_names=[name])
                        for x in range(parts)]).sort_index()
        df = df.drop('stock_type', axis=1) if 'stock_type' in df.columns else df
        df = df.reset_index().rename(columns={'mddate': 'date', 'stock': 'code'})
        df['date'] = df['date'].map(trans_datetime2int)
        df['code'] = df['code'].map(trans_windcode2int)
        if 'rpt_date' in df.columns:
            df[1::4].pivot('date', 'code', name).to_hdf('%s/%s_f0.h5' % (store_address, name), name + '_f0', format='t')
            df[2::4].pivot('date', 'code', name).to_hdf('%s/%s_f1.h5' % (store_address, name), name + '_f1', format='t')
            df[3::4].pivot('date', 'code', name).to_hdf('%s/%s_f2.h5' % (store_address, name), name + '_f2', format='t')
        else:
            df.pivot('date', 'code', name).to_hdf('%s/%s.h5' % (store_address, name), name, format='t')

# multiprocess(24, _func, con_list)

con_factors = [
     'author_number30',
     'author_number7',
     'author_number90',
     'buy_number30',
     'buy_number7',
     'buy_number90',
     'cfc2s_c13',
     'cfc2s_c2',
     'cfc2s_c9',
     'cfc3cs_cgb',
     'cfc3cs_cgpb',
     'cfc3s_cgb',
     'cfc3s_cgg',
     'cfc3s_cgpb',
     'cfc3s_cgpeg',
     'cfs_c12_f0',
     'cfs_c12_f1',
     'cfs_c12_f2',
     'cfs_c1_f0',
     'cfs_c1_f1',
     'cfs_c1_f2',
     'cfs_c3_f0',
     'cfs_c3_f1',
     'cfs_c3_f2',
     'cfs_c4_f0',
     'cfs_c4_f1',
     'cfs_c4_f2',
     'cfs_c5_f0',
     'cfs_c5_f1',
     'cfs_c5_f2',
     'cfs_c6_f0',
     'cfs_c6_f1',
     'cfs_c6_f2',
     'cfs_c7_f0',
     'cfs_c7_f1',
     'cfs_c7_f2',
     'cfs_c80_f0',
     'cfs_c80_f1',
     'cfs_c80_f2',
     'cfs_c81_f0',
     'cfs_c81_f1',
     'cfs_c81_f2',
     'cfs_c82_f0',
     'cfs_c82_f1',
     'cfs_c82_f2',
     'cfs_c83_f0',
     'cfs_c83_f1',
     'cfs_c83_f2',
     'cfs_c84_f0',
     'cfs_c84_f1',
     'cfs_c84_f2',
     'cfs_cb_f0',
     'cfs_cb_f1',
     'cfs_cb_f2',
     'cfs_cpb_f0',
     'cfs_cpb_f1',
     'cfs_cpb_f2',
     'cfs_score',
     'cfs_target_price',
     'consensus_confidence10_f0',
     'consensus_confidence10_f1',
     'consensus_confidence10_f2',
     'consensus_confidence15_f0',
     'consensus_confidence15_f1',
     'consensus_confidence15_f2',
     'consensus_confidence25_f0',
     'consensus_confidence25_f1',
     'consensus_confidence25_f2',
     'consensus_confidence5_f0',
     'consensus_confidence5_f1',
     'consensus_confidence5_f2',
     'consensus_confidence75_f0',
     'consensus_confidence75_f1',
     'consensus_confidence75_f2',
     'csd_forward_pb_deviation25',
     'csd_forward_pb_deviation5',
     'csd_forward_pb_deviation75',
     'csd_forward_pe_deviation25',
     'csd_forward_pe_deviation5',
     'csd_forward_pe_deviation75',
     'csd_pb_deviation25_f0',
     'csd_pb_deviation25_f1',
     'csd_pb_deviation25_f2',
     'csd_pb_deviation5_f0',
     'csd_pb_deviation5_f1',
     'csd_pb_deviation5_f2',
     'csd_pb_deviation75_f0',
     'csd_pb_deviation75_f1',
     'csd_pb_deviation75_f2',
     'csd_pe_deviation25_f0',
     'csd_pe_deviation25_f1',
     'csd_pe_deviation25_f2',
     'csd_pe_deviation5_f0',
     'csd_pe_deviation5_f1',
     'csd_pe_deviation5_f2',
     'csd_pe_deviation75_f0',
     'csd_pe_deviation75_f1',
     'csd_pe_deviation75_f2',
     'degree_f0',
     'degree_f1',
     'degree_f2',
     'down_number30_f0',
     'down_number30_f1',
     'down_number30_f2',
     'down_number7_f0',
     'down_number7_f1',
     'down_number7_f2',
     'down_number90_f0',
     'down_number90_f1',
     'down_number90_f2',
     'eps_deviation25_f0',
     'eps_deviation25_f1',
     'eps_deviation25_f2',
     'eps_deviation5_f0',
     'eps_deviation5_f1',
     'eps_deviation5_f2',
     'eps_deviation75_f0',
     'eps_deviation75_f1',
     'eps_deviation75_f2',
     'eps_stdev25_f0',
     'eps_stdev25_f1',
     'eps_stdev25_f2',
     'eps_stdev5_f0',
     'eps_stdev5_f1',
     'eps_stdev5_f2',
     'eps_stdev75_f0',
     'eps_stdev75_f1',
     'eps_stdev75_f2',
     'neutral_number30',
     'neutral_number7',
     'neutral_number90',
     'ni_deviation25_f0',
     'ni_deviation25_f1',
     'ni_deviation25_f2',
     'ni_deviation5_f0',
     'ni_deviation5_f1',
     'ni_deviation5_f2',
     'ni_deviation75_f0',
     'ni_deviation75_f1',
     'ni_deviation75_f2',
     'ni_stdev25_f0',
     'ni_stdev25_f1',
     'ni_stdev25_f2',
     'ni_stdev5_f0',
     'ni_stdev5_f1',
     'ni_stdev5_f2',
     'ni_stdev75_f0',
     'ni_stdev75_f1',
     'ni_stdev75_f2',
     'optimism_confidence10_f0',
     'optimism_confidence10_f1',
     'optimism_confidence10_f2',
     'optimism_confidence15_f0',
     'optimism_confidence15_f1',
     'optimism_confidence15_f2',
     'optimism_confidence25_f0',
     'optimism_confidence25_f1',
     'optimism_confidence25_f2',
     'optimism_confidence5_f0',
     'optimism_confidence5_f1',
     'optimism_confidence5_f2',
     'optimism_confidence75_f0',
     'optimism_confidence75_f1',
     'optimism_confidence75_f2',
     'organ_number10',
     'organ_number25',
     'organ_number30',
     'organ_number7',
     'organ_number75',
     'organ_number90',
     'overweight_number30',
     'overweight_number7',
     'overweight_number90',
     'pessimism_confidence10_f0',
     'pessimism_confidence10_f1',
     'pessimism_confidence10_f2',
     'pessimism_confidence15_f0',
     'pessimism_confidence15_f1',
     'pessimism_confidence15_f2',
     'pessimism_confidence25_f0',
     'pessimism_confidence25_f1',
     'pessimism_confidence25_f2',
     'pessimism_confidence5_f0',
     'pessimism_confidence5_f1',
     'pessimism_confidence5_f2',
     'pessimism_confidence75_f0',
     'pessimism_confidence75_f1',
     'pessimism_confidence75_f2',
     'rating_down_number30',
     'rating_down_number7',
     'rating_down_number90',
     'rating_up_number30',
     'rating_up_number7',
     'rating_up_number90',
     'relative_report_number10',
     'relative_report_number25',
     'relative_report_number75',
     'report_number30',
     'report_number7',
     'report_number90',
     'sell_number30',
     'sell_number7',
     'sell_number90',
     'stock_diversity_f0',
     'stock_diversity_f1',
     'stock_diversity_f2',
     'tcap',
     'underweight_number30',
     'underweight_number7',
     'underweight_number90',
     'up_number30_f0',
     'up_number30_f1',
     'up_number30_f2',
     'up_number7_f0',
     'up_number7_f1',
     'up_number7_f2',
     'up_number90_f0',
     'up_number90_f1',
     'up_number90_f2',
]


close = get_daily_1factor('close')


# con_factors = list(set(con_factors) - {'cfs_target_price', 'cfs_score', 'cfc2s_c2', 'cfc2s_c13', 'cfc2s_c9',
#                     'cfc3s_cgb', 'cfc3s_cgpb', 'cfc3s_cgg', 'cfc3s_cgpeg', 'cfc3cs_cgb', 'cfc3cs_cgpb'})


def calc_con_factor(name, C=False, P=False, I=False, days=60):

    df = get_daily_1factor(name)
    if C:
        df = df / close
        name += 'C'
    if P:
        df = df.pct_change(days)
        name += 'P'
    # if I:
    #     df = get_ind_neutral(df)
    #     name += 'I'
    if ~ (C | P | I):
        name += 'O'
    df1 = df.loc[20140630 : 20200630]
    df1.index = df1.index.map(str)
    df1.columns = df1.columns.map(trans_int2windcode)
    df1.to_pickle(f'{factor_address}/{name}.pkl')

def calc_batch_con_factor(name):
    #TODO: IndNeu
    calc_con_factor(name, C=False, P=False, I=False)
    calc_con_factor(name, C=True, P=False, I=False)
    calc_con_factor(name, C=False, P=True, I=False)
    # calc_con_factor(name, C=False, P=False, I=True)
    # calc_con_factor(name, C=False, P=True, I=True)
    # calc_con_factor(name, C=True, P=False, I=True)
    calc_con_factor(name, C=True, P=True, I=False)
    # calc_con_factor(name, C=True, P=True, I=True)

def _func1(sub_list, line=0):

    for name in sub_list:
        calc_batch_con_factor(name)

multiprocess(24, _func1, con_factors)
