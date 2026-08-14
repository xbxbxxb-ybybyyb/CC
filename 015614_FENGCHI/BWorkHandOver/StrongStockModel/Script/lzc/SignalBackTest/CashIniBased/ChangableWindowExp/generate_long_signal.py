# @Time : 2022/1/20 15:37
# @Author : Zhichen Lu
# @File : generate_signal.py
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_long_integration
from dataApi.tradeDate import get_pre_trade_date
import os

param_map = {
   f'XGB_DTC_Future_{x}_Bar':[
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV3With1DayLabel_20220126/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV3With1DayLabel_20220126/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV3With1DayLabel_20220126/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
] for x in range(1,7)
}
param_map.update({'XGB_DTC_Future_7_Bar':[
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400/',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400/',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400/',
]})

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window/'
if not os.path.exists(out_path):
    os.makedirs(out_path)

signal_map = {}

for tag in param_map:
    if tag=='XGB_DTC_Future_7_Bar':
        threshold_tag = 'actual_label'
    else:
        threshold_tag = '1_day_label'
    params = dict(
    pct = 0.05,
    signal_file_name_list =  param_map[tag],
    subset_path_list = [x[:-1]+'_val_pred/' for x in param_map[tag]],
    start = 20170101,
    end = 20210531,
        threshold_tag=threshold_tag
    )
    out_file = f'{out_path}/signal_long_{tag}_pct_{params["pct"]}.pkl'
    signal_map[tag] = out_file
    if os.path.exists(out_file):
        print(out_file,'exist')
        continue
    res = get_signal_by_val_pct_threshold_long_integration(**params)
    print(tag)
    pd.to_pickle(res,out_file)
print(signal_map)