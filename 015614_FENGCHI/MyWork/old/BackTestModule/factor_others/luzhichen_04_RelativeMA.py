import pandas as pd
import numpy as np
import os
from QuickFactorEvaluationBackTest import FactorBackTest
from dataApi.getData import *
from config import *
import time
import copy
from dataApi.stockList import clean_stock_list
stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')

def calc_Factor_RelativeMA(MA_period_list = [2, 3, 4]):
    tag = 'RelativeMA_%s' % ('_'.join(list(map(str, MA_period_list))))
    if os.path.exists('%s/temp_daily_by_lzc/RelativeMA/result/%s.h5' % (root_path, tag)):
        factor_signal_df = pd.read_hdf('%s/temp_daily_by_lzc/RelativeMA/result/%s.h5' % (root_path, tag), tag)
        return factor_signal_df
    start = 20170101
    end = 20191231
    # ZZ500_daily_stock_pool = get_stock_pool('ZZ500')
    # HS300_daily_stock_pool = get_stock_pool('HS300')
    # ZZ800_daily_stock_pool = {}
    # for day in HS300_daily_stock_pool:
    #     ZZ800_daily_stock_pool[day] = list(set(HS300_daily_stock_pool[day]).union(set(ZZ500_daily_stock_pool[day])))
    # ZZ500_pool = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'ZZ500')
    # HS300_pool = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'HS300')
    # stk_list = list(set(ZZ500_pool.columns).union(set(HS300_pool.columns)))
    # ZZ500_pool = ZZ500_pool.loc[start:end].reindex(stk_list, axis=1).fillna(False)
    # HS300_pool = HS300_pool.loc[start:end].reindex(stk_list, axis=1).fillna(False)
    # ZZ800_pool = (HS300_pool + ZZ500_pool) > 0
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    daily_stock_pool = {}
    for day in stock_pool_all.index:
        daily_stock_pool[day] = stock_pool_all.loc[day,:].replace(False,np.nan).dropna().index.tolist()
    stk_list = stock_pool_all.columns.tolist()
    benchmark = get_minute_1stock(code='ZZ500', start_datetime=201701010925, end_datetime=201912311500, \
                                  factor_list=['open', 'close', 'high', 'low', 'amt', 'volume'], type='bench')
    ZZ500_weight = pd.read_hdf('/data/group/800319/junkData/daily/ZZ500_exdiv_weight.h5', 'ZZ500_exdiv_weight')
    # ZZ500_weight = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'ZZ500')

    daily_adj = get_daily_1factor(code_list=stk_list, factor='close_badj')
    daily = get_daily_1factor(code_list=stk_list, factor='close_badj')
    minutes_adj = get_minute_1factor(start_datetime=201701010925, end_datetime=201912311500, code_list=stk_list, factor='close_badj')
    # minutes_adj.index = [x[0]*10000+x[1] for x in minutes_adj.index]
    minutes_adj['datetime'] = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    minutes_adj = minutes_adj.reset_index().set_index('datetime')

    MA_para = pd.Series(MA_period_list, index=MA_period_list) ** 0.5
    MA_para = MA_para / MA_para.sum()

    MA = {}
    for MA_period in MA_para.index:
        MA[MA_period] = daily_adj.rolling(MA_period).mean() * MA_para[MA_period]
    MA = pd.Panel(MA)
    multiple_MA = MA.sum(axis=0).loc[20170101:20191231].replace(0, np.nan)

    MA_score = (daily_adj / MA.sum(axis=0) - 1).replace(np.inf, np.nan)  # [60:]
    benchmark_score = (ZZ500_weight * MA_score[ZZ500_weight.columns]).sum(axis=1)

    MA_score = MA_score.loc[20170101:20191231]
    MA_score = (MA_score * stock_pool_all.loc[MA_score.index]).replace(0, np.nan)
    benchmark_score = benchmark_score.loc[start:end]

    # (MA_score.T - (MA_score.std(axis=1)*benchmark_score)).T

    minutes_adj_12 = minutes_adj[minutes_adj['date'].isin(MA_score.index)].drop(['date', 'time'], axis=1)
    time_list = list(set(minutes_adj['time']))
    time_list.sort()
    minues_arr_3_dim = minutes_adj_12.values.reshape(MA_score.shape[0], 242, MA_score.shape[1])
    minues_pn = pd.Panel(minues_arr_3_dim, items=MA_score.index, major_axis=time_list, minor_axis=MA_score.columns)
    multi_MA_pre_day = (multiple_MA.shift(1) * stock_pool_all.loc[multiple_MA.index].replace(False, np.nan))
    multi_MA_pre_day = multi_MA_pre_day.replace(0, np.nan).replace(np.inf, np.nan)

    MA_score_minures_pn = pd.Panel(minues_pn.values / multi_MA_pre_day.values.reshape(multiple_MA.shape[0], 1, multiple_MA.shape[1]) - 1, \
                                   items=minues_pn.items, major_axis=minues_pn.major_axis, minor_axis=minues_pn.minor_axis)

    MA_score_minutes_df = pd.DataFrame(MA_score_minures_pn.values.reshape(minutes_adj_12.shape[0], minutes_adj_12.shape[1]),
                                       index=minutes_adj_12.index, columns=minutes_adj_12.columns)

    sell_signal = (MA_score_minutes_df.rank(axis=1) < 100) * 1
    buy_signal = (MA_score_minutes_df.rank(axis=1, ascending=False) < 100) * -1
    factor_signal_df = buy_signal + sell_signal

    # os.mkdir('%s/temp_daily_by_lzc/RelativeMA/result/' % root_path)
    factor_signal_df.to_hdf('%s/temp_daily_by_lzc/RelativeMA/result/%s.h5' % (root_path, tag), tag)
    return factor_signal_df

def calc_Factor_DailyRetS(n,Lag):
    # if os.path.exists('%s/temp_daily_by_lzc/DailyRegRet/DailyRegRet_n%d_Lag%d.h5' % (root_path, n, Lag)):
    #     signal_df = pd.read_hdf('%s/temp_daily_by_lzc/DailyRegRet/DailyRegRet_n%d_Lag%d.h5' % (root_path, n, Lag), 'DailyRegRet_n%d_Lag%d' % (n, Lag))
    #     return signal_df
    start = 20160101
    end = 20191231
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    daily_stock_pool = {}
    for day in stock_pool_all.index:
        daily_stock_pool[day] = stock_pool_all.loc[day,:].replace(False,np.nan).dropna().index.tolist()
    stk_list = stock_pool_all.columns.tolist()
    ####
    daily_adj = get_daily_1factor(code_list=stk_list, factor='close_badj')
    minutes_adj = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, \
                                     code_list=stk_list, factor='close_badj')
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    daily_adj = daily_adj.loc[start:end]
    minutes_adj = minutes_adj.loc[start * 10000 + 925:end * 10000 + 1500]
    ####
    benchmark_net = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, code_list=['ZZ500'], factor='close', type='bench')
    benchmark_net.index = [x[0] * 10000 + x[1] for x in benchmark_net.index]
    # benchmark_daily = get_daily_1factor(code_list=['ZZ500'], factor='close', type='bench')

    daily_ret = daily_adj / daily_adj.shift(1) - 1
    daily_rolling_ret = daily_adj.rolling(n).mean() / daily_adj - 1
    factor_values = pd.DataFrame()
    for day in daily_rolling_ret.index[n + Lag - 1:]:
        X = daily_rolling_ret.loc[:day][-Lag:].T
        X = X.loc[daily_stock_pool[day]].copy()
        X['constant'] = 1
        X = X.T
        reg = np.linalg.inv(X.dot(X.T)).dot(X).dot(np.array(daily_ret.loc[day, X.columns]))
        res = daily_ret.loc[day, X.columns] - X.T.dot(reg)
        res = pd.DataFrame(res, columns=[day]).T
        factor_values = pd.concat([factor_values, res])
        print(day)

    factor_signal = (factor_values.rank(axis=1, ascending=False) < 150) * 1
    factor_signal = factor_signal.reindex(daily_ret.index, axis=0).shift(1)
    time_list = [x % 10000 for x in minutes_adj.index[:242]]

    signal_pn = pd.Panel(1, items=daily_adj.index, major_axis=time_list, minor_axis=factor_signal.columns)
    signal_pn = signal_pn.multiply(factor_signal.T, axis=1)
    signal_pn.loc[:, :1000, :] = 0
    signal_df = pd.DataFrame(signal_pn.values.reshape(minutes_adj.shape[0], factor_signal.shape[1]),
                             index=minutes_adj.index, columns=factor_signal.columns)

    signal_df = signal_df.loc[20170101 * 10000:end * 10000 + 1500]
    # os.mkdir('%s/temp_daily_by_lzc/DailyRegRet/' % root_path)
    signal_df.to_hdf('%s/temp_daily_by_lzc/DailyRegRet/DailyRegRet_n%d_Lag%d.h5' % (root_path, n, Lag), 'DailyRegRet_n%d_Lag%d' % (n, Lag))
    return  signal_df


if __name__=="__main__":
    print(1)
    MA_period_list = [5,10,15]
    tag = 'RelativeMA_%s' % ('_'.join(list(map(str, MA_period_list))))
    factor_df = calc_Factor_RelativeMA(MA_period_list)
    factor_df1 = factor_df
    print('origin')
    ###########################
    n = 8
    Lag = 3
    factor_df_daily = calc_Factor_DailyRetS(n,Lag)
        # pd.read_hdf('%s/temp_daily_by_lzc/DailyRegRet/DailyRegRet_n%d_Lag%d.h5' % (root_path, n, Lag), 'DailyRegRet_n%d_Lag%d' % (n, Lag))
    factor_df1 = factor_df * factor_df_daily
    tag = tag + 'DailyRegRet_n%d_Lag%d' % (n, Lag)
    print(tag)
    #################################
    print(factor_df1.shape)
    factor_test = FactorBackTest(factor_df1)
    factor_test.evaluation(30)

    factor_test.result_output(fileroot='%s/temp_daily_by_lzc/RelativeMA/result/' % root_path, filename='luzhichen_04_'+tag)
    print(factor_test.evaluation_result)
    # if not os.path.exists('%s/temp_daily_by_lzc/RelativeMA/result/fig_%s' % (root_path, tag)):
    #     os.mkdir('%s/temp_daily_by_lzc/RelativeMA/result/fig_%s' % (root_path, tag))
    # factor_test.check_part_signal(80, '%s/temp_daily_by_lzc/RelativeMA/result/fig_%s' % (root_path, tag), 18)
    print(factor_test.running_time)
