import pandas as pd
import numpy as np
import os
os.chdir('/data/group/800319/BackTestModule/')
from QuickFactorEvaluationBackTest import FactorBackTest
from dataApi.getData import *
from config import *
import time
import copy
from multiprocessing import Pool
from dataApi.stockList import clean_stock_list

def quick_get_corr(matrix_3d,matrix_1d):
    p,v,c = matrix_3d.shape
    matrix_1d_neutralize = matrix_1d.reshape(p,1,1) - matrix_1d.mean()
    matrix_3d_neutralize = matrix_3d - matrix_3d.mean(0)
    cov = (matrix_3d_neutralize*matrix_1d_neutralize).mean(axis=0)
    std_3d = matrix_3d.std(axis=0)
    std_1d = matrix_1d.std()
    corr = cov/(std_3d*std_1d)
    return corr
def get_data_ready(para):
    T,n,M = para
    start = 20170101
    end = 20191231
    ####
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')

    stk_list =  stock_pool_all.columns.tolist()
    ####

    ####
    daily_adj = get_daily_1factor(code_list=stk_list,factor='close_badj')
    daily = get_daily_1factor(code_list=stk_list,factor='close_badj')
    minutes_adj = get_minute_1factor(start_datetime=start*10000+925,end_datetime=end*10000+1500,\
                                     code_list=stk_list,factor='close_badj')
    minutes_adj.index = [x[0]*10000+x[1] for x in minutes_adj.index]
    daily_adj = daily_adj.loc[start:end]
    minutes_adj = minutes_adj.loc[start*10000+925:end*10000+1500]
    ####
    benchmark_net = get_minute_1factor(start_datetime=start*10000+925,end_datetime=end*10000+1500,code_list=['ZZ500'],factor='close',type='bench')
    benchmark_net.index = [x[0]*10000+x[1] for x in benchmark_net.index]

    corr_dict = {}
    active_dict = {}
    for m in range(M):
        corr_dict[T-n*m] = minutes_adj.rolling(T-n*m).corr(benchmark_net[benchmark_net.columns[0]])
        active_dict[T-n*m] = (minutes_adj.pct_change(T-n*m).T - benchmark_net.loc[minutes_adj.index,benchmark_net.columns[0]].pct_change(T-n*m)).T
        print(T-n*m)
    pd.to_pickle(corr_dict,'/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/temp_corr_dict_T%d_n%d_M%d.pkl'%(T,n,M))
    pd.to_pickle(active_dict,'/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/active_dict_T%d_n%d_M%d.pkl'%(T,n,M))
    # corr_dict = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/temp_corr_dict.pkl')
    for m in range(M):
        active_dict[T-n*m] = active_dict[T-n*m]/(T-n*m)
    corr_pn = pd.Panel(corr_dict)
    active_pn = pd.Panel(active_dict)

    corr_trend = quick_get_corr(corr_pn.values,np.array([x for x in range(M)]))
    corr_df = pd.DataFrame(corr_trend,index = minutes_adj.index,columns=minutes_adj.columns)
    corr_df = -1*corr_df

    active_trend = quick_get_corr(active_pn.values,np.array([x for x in range(M)]))
    active_trend_df = pd.DataFrame(active_trend,index = minutes_adj.index,columns=minutes_adj.columns)

    factor = active_trend_df * corr_df
    for idx in factor.index:
        factor.loc[idx,:] = factor.loc[idx,:]*stock_pool_all.loc[int(idx/10000),:]
    factor = factor.replace(0,np.nan)

    # '/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/factor_T%d_n%d_M%d.pkl' % (T, n, M)
    pd.to_pickle(factor,'/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/factor_T%d_n%d_M%d.pkl' % (T, n, M))
    print(T,n,M,'done')
def out_put_factor_signal(up_corr,low_corr,N,T = 150, n = 5, M = 15):
    if os.path.exists('/data/group/800319/junkData/temp_daily_by_lzc/factor_signal_BreakCorr/factor_signal_corr_break_T%d_n%d_M%d_up%s_low%s_extrem%d.pkl'%\
             (T,n,M,str(up_corr),str(low_corr),N)):
        factor_signal = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/factor_signal_BreakCorr/factor_signal_corr_break_T%d_n%d_M%d_up%s_low%s_extrem%d.pkl'%\
             (T,n,M,str(up_corr),str(low_corr),N))
        return factor_signal, 'CorrBreak_T%d_n%d_M%d_up%s_low%s_extrem%d' % (T, n, M, str(up_corr), str(low_corr), N)
    factor = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/factor_T%d_n%d_M%d.pkl' % (T, n, M))
    corr_dict = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/factor_temp_data_CorrBreak/temp_corr_dict_T%d_n%d_M%d.pkl'%(T,n,M))
#     active_dict = pd.read_pickle('/data/group/800319/junkData/temp_daily_by_lzc/active_dict_T%d_n%d_M%d.pkl'%(T,n,M))
    corr_pn = pd.Panel(corr_dict)
    buy_filter = (corr_pn.loc[corr_pn.items[0],:,:]>up_corr)*(corr_pn.loc[corr_pn.items[-1],:,:]<low_corr)
    ranking = factor.rank(axis = 1,ascending = False)
    buy = (ranking<(100+N)*(ranking>N))*1
    buy_signal = buy*buy_filter

    factor_abs = factor.apply(lambda x : abs(x)).replace(0,np.nan)
    sell_rank = factor_abs.rank(ascending = True,axis=1)
    sell = (sell_rank>N)*(sell_rank<100+N)*1
    sell_filter = (corr_pn.loc[corr_pn.items[0],:,:]<low_corr)
    sell_signal = sell*sell_filter*-1
    factor_signal = sell_signal + buy_signal
    pd.to_pickle(factor_signal, \
                 '/data/group/800319/junkData/temp_daily_by_lzc/factor_signal_BreakCorr/factor_signal_corr_break_T%d_n%d_M%d_up%s_low%s_extrem%d.pkl' % \
                 (T, n, M, str(up_corr), str(low_corr), N))
    print('/data/group/800319/junkData/temp_daily_by_lzc/factor_signal_BreakCorr/factor_signal_corr_break_T%d_n%d_M%d_up%s_low%s_extrem%d.pkl'%\
             (T,n,M,str(up_corr),str(low_corr),N))
    return factor_signal,'CorrBreak_T%d_n%d_M%d_up%s_low%s_extrem%d'%(T,n,M,str(up_corr),str(low_corr),N)
def datagenerator_wraper(para):
    up_corr, low_corr, N = para
    return out_put_factor_signal(up_corr, low_corr, N)

def calc_Factor_multi():
    para_list = []
    for low in [0.3, 0.4, 0.5]:
        for high in [0.7, 0.75, 0.8, 0.85]:
            for N_ in [20, 60, 100]:
                para_list.append((high, low, N_))

    for temp_para in para_list:
        print(temp_para)
        e = time.time()
        datagenerator_wraper(temp_para)
        print(time.time() - e)
    pool = Pool(6)
    r = pool.map(datagenerator_wraper, para_list)
    pool.close()
    pool.join()
if __name__=="__main__":
    get_data_ready((150,5,15))
    datagenerator_wraper((0.8,0.3,20))
    print(1)
    factor_df1,tag = out_put_factor_signal(0.8,0.3,20,T = 150, n = 5, M = 15)


    factor_df1 = factor_df1
    print(factor_df1.shape)
    factor_test = FactorBackTest(factor_df1)
    factor_test.evaluation(30)
    print(factor_test.evaluation_result)
    factor_test.result_output(fileroot='/data/group/800319/junkData/temp_daily_by_lzc/CorrBreak_Result/', filename=tag)
    print(factor_test.running_time)
    print(tag, 'done')


