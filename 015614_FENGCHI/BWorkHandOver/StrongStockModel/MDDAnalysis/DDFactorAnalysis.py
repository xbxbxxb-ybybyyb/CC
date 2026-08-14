# @Time : 2022/5/20 9:21
# @Author : Zhichen Lu
# @File : DDFactorAnalysis.py

import pandas as pd
import numpy as np
import xgboost as xgb
import os
from StrongStockModel.model.ModelResultLoadingTool import generate_long_signal,generate_short_signal
from dataApi.tradeDate import get_pre_trade_date,get_date_range

model_param = {
    'XGB_DTC_Matrix_Light_Cat': {
        x: [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
            f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_all_sample_ic_all_t/',
            f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_all_sample_ic_all_t/'
        ] for x in range(1, 9)
    },

    'XGB_D': {
        x: [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',

        ] for x in range(1, 9)
    },
}

out_path = '/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/'

file_list = sorted(os.listdir(model_param['XGB_DTC_Matrix_Light_Cat'][8][3]))
update_date = 20180125
future = 8
import pandas as pd
X_test = pd.read_pickle('/data/user/015664/temp/Xtest2018.pkl')
extra_rate = {}
for date in [20180201,20180202,20180206,20180207]:
    check = X_test.loc[date]
    # check.groupby(level=0).median()
    extra_rate[date] = ((abs(check)>4).sum()/check.shape[0]).sort_values()
extra_rate = pd.DataFrame(extra_rate).sort_values(20180202)
from dataApi.sendInfo import send_file
extra_rate.to_excel('./因子极端值比例.xlsx')
send_file(['015664'],'./因子极端值比例.xlsx')

# model = xgb.Booster(model_file=model_param['XGB_DTC_Matrix_Light_Cat'][future][3][:-1]+f'_model_conf/{update_date}.pkl')
# tag = 'XGB_D'
# long_8 = generate_long_signal(0.05,{8:model_param[tag][8]},get_pre_trade_date(update_date,-1),
#                               get_pre_trade_date(update_date,-10),out_path=f'{out_path}/{tag}/long/',formate=False)
# signal, pred_ret = long_8[8][:2]
# desc = pred_ret.unstack().T.describe([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]).drop(['count','max','min'])
# signal_count = signal[signal.fillna(False)].T.count()


exp_path = {
    x:
{8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropSub10ByExtraRatioRetrain/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop{x}/XGB_ic_d_train200_test10_factor_num400_drop{x}/']}
    for x in  range(5,21,3)
}

exp_res = {}
for x in exp_path:
    temp = generate_long_signal(0.05,exp_path[x],get_pre_trade_date(update_date,-1),
                              get_pre_trade_date(update_date,-10),out_path=f'{out_path}/DropExp/ExtremDropRetrain{x}/long/',formate=False)
    signal = temp[8][0]
    exp_res[x] = signal[signal.fillna(False)].T.count()

exp_res = pd.DataFrame(exp_res)
#
# exp_path_sub = {
#     x:
# {8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropSub10/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop{x}/XGB_ic_d_train200_test10_factor_num400_drop{x}/']}
#     for x in range(0,400,10)
# }
#
# exp_res_sub = {}
# for x in exp_path_sub:
#     temp = generate_long_signal(0.05,exp_path_sub[x],get_pre_trade_date(update_date,-1),
#                               get_pre_trade_date(update_date,-10),out_path=f'{out_path}/DropExpSub/drop{x}/long/',formate=False)
#     signal = temp[8][0]
#     exp_res_sub[x] = signal[signal.fillna(False)].T.count()
#
# exp_res_sub = pd.DataFrame(exp_res_sub)


# FI_ressub = {}
# for FI_tag in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']:
#     exp_path_sub_FI = {
#         x:
#     {8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropSub10ByImportance_{FI_tag}/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop{x}/XGB_ic_d_train200_test10_factor_num400_drop{x}/']}
#         for x in range(0,400,10)
#     }
#
#     exp_res_sub = {}
#     for x in exp_path_sub_FI:
#         temp = generate_long_signal(0.05,exp_path_sub_FI[x],get_pre_trade_date(update_date,-1),
#                                   get_pre_trade_date(update_date,-10),out_path=f'{out_path}/DropExp_{FI_tag}/drop{x}/long/',formate=False)
#         signal = temp[8][0]
#         exp_res_sub[x] = signal[signal.fillna(False)].T.count()
#
#     FI_ressub[FI_tag] = pd.DataFrame(exp_res_sub)
#

# FI_ressub = {}
# for FI_tag in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']:
#     exp_path_sub_FI = {
#         x:
#     {8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropByImportance_Sub10_{FI_tag}/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop{x}/XGB_ic_d_train200_test10_factor_num400_drop{x}/']}
#         for x in range(0,400,10)
#     }
#
#     exp_res_sub = {}
#     for x in exp_path_sub_FI:
#         temp = generate_long_signal(0.05,exp_path_sub_FI[x],get_pre_trade_date(update_date,-1),
#                                   get_pre_trade_date(update_date,-10),out_path=f'{out_path}/DropExp_Sub10_{FI_tag}/drop{x}/long/',formate=False)
#         signal = temp[8][0]
#         exp_res_sub[x] = signal[signal.fillna(False)].T.count()
#
#     FI_ressub[FI_tag] = pd.DataFrame(exp_res_sub)


FI_ressub = {}
for FI_tag in ['total_cover']:
    exp_path_sub_FI = {
        x:
    # {8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropByFIRetrain_{FI_tag}/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop{x}/XGB_ic_d_train200_test10_factor_num400_drop{x}/']}
    {8:[f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropByFIRetrain_total_cover_roll/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop0/XGB_ic_d_train200_test10_factor_num400_drop0/']}
        for x in [0]#range(0,101,20)
    }

    exp_res_sub = {}
    for x in exp_path_sub_FI:
        temp = generate_long_signal(0.05,exp_path_sub_FI[x],get_pre_trade_date(update_date,-1),
                                  get_pre_trade_date(update_date,-10),out_path=f'{out_path}/DropRetrainExp_Sub10_Retrain_{FI_tag}/drop{x}/long/',formate=False)
        signal = temp[8][0]
        exp_res_sub[x] = signal[signal.fillna(False)].T.count()

    FI_ressub[FI_tag] = pd.DataFrame(exp_res_sub)


