# @Time : 2021/5/27 14:59
# @Author : Zhichen Lu
# @File : ic_analysis.py

import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

import os
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
import numpy as np
model_k_m = {
'lightGBM':'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t/',
'CatBoost':'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t/',
# 'XGB_C':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40/',
# 'XGB_D':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40/',
# 'XGB_T':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/',
'XGB_D_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_d_train200_test10_factor_num400/',
'XGB_T_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_t_train200_test10_factor_num400/',
'XGB_C_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_c_train200_test10_factor_num400/',
}

# model_k_m = {
# 'lightGBM':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/catboostnew2_ic_all_t/',
# 'CatBoost':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/lightgbmnew_ic_all_t/',
# 'XGB_C':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40/',
# 'XGB_D':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/',
# 'XGB_T':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40/',
# }

integrate_list = {x:[x] for x in model_k_m}
# integrate_list = {}
# integrate_list['XGB_DTC'] = ['XGB_D','XGB_T','XGB_C']
# integrate_list['XGBMonthly_DTC'] = ['XGB_D_Monthly','XGB_T_Monthly','XGB_C_Monthly',]
integrate_list['XGB_lightGBM_CatBoost'] =  ['XGB_D_Monthly','XGB_T_Monthly','XGB_C_Monthly','lightGBM','CatBoost']
# integrate_list['XGB_lightGBM_CatBoost_TOnly'] =  ['XGB_T','lightGBM','CatBoost']
# integrate_list['XGBMonthly_lightGBM_CatBoost'] =  ['XGB_D_Monthly','XGB_T_Monthly','XGB_C_Monthly','lightGBM','CatBoost']


def get_info(each,model_list,path = '/data/group/800319/信号存储/IntegratedSignal/'):
    # each = period_list[0]
    subset = {x: pd.read_pickle(model_list[x] + '%d.pkl' % each) for x in model_list}
    subset = pd.Panel(subset)
    integrate_signal = subset.sum(axis=0) / subset.count(axis=0)


    val = {x: pd.read_pickle(model_list[x][:-1] + '_val_pred/%d.pkl' % each) for x in model_list}
    val = pd.Panel(val)
    val_integrated = val.sum(axis=0) / val.count(axis=0)

    if not os.path.exists(f'{path}pred/'):
        os.mkdir(f'{path}pred/')
    if not os.path.exists(f'{path}val/'):
        os.mkdir(f'{path}val/')

    pd.to_pickle(integrate_signal,f'{path}pred/{each}.pkl')
    pd.to_pickle(val_integrated,f'{path}val/{each}.pkl')
    print(each,'done')
    return True

def get_res(model_list):
    pool_dict = {}

    pool = Pool(20)
    period_list = sorted([int(x[:-4]) for x in os.listdir(model_list[list(model_list.keys())[0]])])
    period_list = list(filter(lambda x : x<=20210518,period_list))
    for e in period_list:
        # get_info(e,model_list)
        pool_dict[e] = pool.apply_async(get_info,(e,model_list))

    pool.close()
    pool.join()

    for each in pool_dict:
        try:
            pool_dict[each] = pool_dict[each].get()
        except:
            get_info(each,model_list)

    # out_file = './Fix预测信号统计半年选因子XGB.xlsx'
    # res_dict.to_excel(out_file)
    # from dataApi.sendInfo import send_file
    # send_file(['015664'],out_file)

res = {}
for each in integrate_list:
    temp_model_list = {x:model_k_m[x] for x in integrate_list[each]}
    res[each] = get_res(temp_model_list)
    print(each)

