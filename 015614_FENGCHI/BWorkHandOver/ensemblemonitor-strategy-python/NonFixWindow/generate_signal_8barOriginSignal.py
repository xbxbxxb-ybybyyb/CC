# @Time : 2022/1/20 15:37
# @Author : Zhichen Lu
# @File : generate_signal.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_short_integration
from dataApi.tradeDate import get_pre_trade_date
import os

param_map = {
#    f'XGB_DTC_Matrix_Light_Future_{x}_Bar':[
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
# ] for x in range(1,8)
}

param_map.update({
   f'XGB_DTC_Matrix_Future_{x}_Bar':[
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
    # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
] for x in range(1,8)
})


out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/NonFixSim/short_8barOriginFactor/'
if not os.path.exists(out_path):
    os.makedirs(out_path)

for tag in sorted(list(param_map.keys()))[::-1]:
    params = dict(
    pct = 0,
    signal_file_name_list =  param_map[tag],
    subset_path_list = [x[:-1]+'_val_pred/' for x in param_map[tag]],
    start=20220113,
    end=20220126)
    print(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl')
    if os.path.exists(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl'):
        print(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl','exist')
        continue
    res = get_signal_by_val_pct_threshold_short_integration(**params)
    print(tag)
    pd.to_pickle(res,f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl')