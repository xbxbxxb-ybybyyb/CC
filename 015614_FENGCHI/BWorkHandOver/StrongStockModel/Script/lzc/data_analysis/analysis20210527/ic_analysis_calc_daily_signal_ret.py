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
'XGB_C':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40/',
'XGB_D':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40/',
'XGB_T':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/',
'XGB_D_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_d_train200_test10_factor_num400/',
'XGB_T_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_t_train200_test10_factor_num400/',
'XGB_C_Monthly':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_c_train200_test10_factor_num400/',
}
# import shutil
# for date in [20210525,20210526,20210527]:
#     shutil.copy('/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/%d.pkl'%date,
#                 '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t/%d.pkl'%date)
#     shutil.copy('/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample_val_pred/%d.pkl' % date,
#                 '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_val_pred/%d.pkl' % date)
#
#     shutil.copy('/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample/%d.pkl' % date,
#                 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t/%d.pkl' % date)
#     shutil.copy('/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample_val_pred/%d.pkl' % date,
#                 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_val_pred/%d.pkl' % date)
# model_k_m = {
# 'lightGBM':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/catboostnew2_ic_all_t/',
# 'CatBoost':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/lightgbmnew_ic_all_t/',
# 'XGB_C':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40/',
# 'XGB_D':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40/',
# 'XGB_T':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40/',
# }

# integrate_list = {x:[x] for x in model_k_m}
integrate_list = {}
# integrate_list['XGB_DTC'] = ['XGB_D','XGB_T','XGB_C']
# integrate_list['XGBMonthly_DTC'] = ['XGB_D_Monthly','XGB_T_Monthly','XGB_C_Monthly',]
integrate_list['XGB_lightGBM_CatBoost'] =  ['XGB_D','XGB_T','XGB_C','lightGBM','CatBoost']
integrate_list['XGBMonthly_lightGBM_CatBoost'] =  ['XGB_D_Monthly','XGB_T_Monthly','XGB_C_Monthly','lightGBM','CatBoost']


def get_info(each,model_list,threshold=0.05):
    # each = period_list[0]
    subset = {x: pd.read_pickle(model_list[x] + '%d.pkl' % each) for x in model_list}
    subset = pd.Panel(subset)
    integrate_signal = subset.sum(axis=0) / subset.count(axis=0)


    val = {x: pd.read_pickle(model_list[x][:-1] + '_val_pred/%d.pkl' % each) for x in model_list}
    val = pd.Panel(val)
    val_integrated = val.sum(axis=0) / val.count(axis=0)

    th = (val_integrated['actual_label']<threshold).sum()/val_integrated.shape[0]
    pct = val_integrated['prediction'].quantile(th)
    pct_with_50bp_bar = max(pct,0.005)


    # all_signal.append(integrate_signal)
    # corr_series[each] = integrate_signal.corr().values[0, 1]
    # mae_series[each] = abs(integrate_signal['prediction'] - integrate_signal['actual_label']).mean()
    if len(integrate_signal)==0:
        return {x:np.nan for x in ['corr','mae','Top1Pct','Top3Pct','Top5Pct','Top7Pct','Top9Pct']}
    integrate_signal['rank'] = integrate_signal['prediction'].rank(pct=True)
    res = {'res':integrate_signal,
            'corr':integrate_signal.corr().values[0, 1],
            'mae':abs(integrate_signal['prediction'] - integrate_signal['actual_label']).mean(),
            'Top1Pct':integrate_signal[integrate_signal['rank']>0.99]['actual_label'].mean(),
            'Top3Pct':integrate_signal[integrate_signal['rank']>0.97]['actual_label'].mean(),
            'Top5Pct':integrate_signal[integrate_signal['rank']>0.95]['actual_label'].mean(),
            'Top7Pct':integrate_signal[integrate_signal['rank']>0.93]['actual_label'].mean(),
            'Top9Pct':integrate_signal[integrate_signal['rank']>0.91]['actual_label'].mean(),
           'Signal':integrate_signal[integrate_signal['prediction']>pct]['actual_label'].mean(),
           'SignalWith50bpBar':integrate_signal[integrate_signal['prediction']>pct_with_50bp_bar]['actual_label'].mean(),
            }
    print(each,'done')
    return res

def get_res(model_list):
    pool_dict = {}

    pool = Pool(20)
    period_list = sorted([int(x[:-4]) for x in os.listdir(model_list[list(model_list.keys())[0]])])
    period_list = list(filter(lambda x : x<=20210527,period_list))
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
    res_dict = {}
    for each in pool_dict:
        res_dict[each] = {i:pool_dict[each][i] for i in ['corr','mae','Top1Pct','Top3Pct','Top5Pct','Top7Pct','Top9Pct','Signal','SignalWith50bpBar']}

    res_dict = pd.DataFrame(res_dict).T
    return res_dict
    # out_file = './Fix预测信号统计半年选因子XGB.xlsx'
    # res_dict.to_excel(out_file)
    # from dataApi.sendInfo import send_file
    # send_file(['015664'],out_file)

res = {}
for each in integrate_list:
    temp_model_list = {x:model_k_m[x] for x in integrate_list[each]}
    res[each] = get_res(temp_model_list)
    print(each)

# res.keys()
# check = res['XGB_lightGBM_CatBoost']
# check.to_excel('./截止20210601_IC.xlsx')

for each in res:
    res[each] = res[each].stack().swaplevel(0,1)
res = pd.DataFrame(res)

out_file = '/data/user/015664/AFuckingTrigger/DataForPaperWork/优化前后信号收益对比.xlsx'
with  pd.ExcelWriter(out_file) as writer:
    for each in res.index.levels[0]:
        res.loc[each].to_excel(writer,sheet_name=each)
writer.close()
#
from dataApi.sendInfo import send_file
send_file(['015664'],out_file)