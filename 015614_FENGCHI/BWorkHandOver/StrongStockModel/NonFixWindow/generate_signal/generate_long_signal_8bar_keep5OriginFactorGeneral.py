# @Time : 2022/1/20 15:37
# @Author : Zhichen Lu
# @File : generate_signal.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_long_integration
from dataApi.tradeDate import get_pre_trade_date
import os

param_map = {
    # f'XGB_DTC_Matrix_Light_Cat_Future_{x}_Bar': [
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
    #     f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
    #     f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_in_sample_ic_all_t/'
    # ] for x in range(1, 9)
}

param_map.update({
    f'XGB_DTC_Future_{x}_Bar': [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',

        # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
    ] for x in range(1, 9)
})

# param_map.update({
#     f'XGBReversalRes_DTC_Future_{x}_Bar': [
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
#     ] for x in range(1, 9)
# })
# param_map.update({
#     f'XGB_DTC_Matrix_Future_{x}_Bar': [
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
#         f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
#         # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
#     ] for x in range(1, 9)
# })
#
# param_map.update({
#    f'XGB_DTCOnly_Future_{x}_Bar':[
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
#     f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
#     # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
# ] for x in range(1,9)
# })

# out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window_8barOriginFactorExpandForCondition/'
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window_8bar1DayRevResFactorExpandForCondition/'
if not os.path.exists(out_path):
    os.makedirs(out_path)

signal_map = {}

# get_signal_by_val_pct_threshold_long_integration(*para, head=None, end=20210531)
tag_list = sorted(list(param_map.keys()))
from xquant.compute.aimr import AIMR
i = 0#int(AIMR.getParam())
for tag in sorted(list(param_map.keys())):
    if '8_Bar' in tag:
        threshold_tag = 'actual_label'
    else:
        threshold_tag = '1_day_label'
    params = dict(
    pct = 0.05,
    signal_file_name_list =  param_map[tag],
    subset_path_list = [x[:-1]+'_val_pred/' for x in param_map[tag]],
    start = 20161026,
    end = 20211231,
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

# import os
# for bar in range(1,9):
#     for tag in ['d','t','c']:
#         base = f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400_val_pred/20210616.pkl'
#         base2 = f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400_val_pred/20210616.pkl'
#         if os.path.exists(base):
#             os.remove(base)
#         if os.path.exists(base2):
#             os.remove(base2)

