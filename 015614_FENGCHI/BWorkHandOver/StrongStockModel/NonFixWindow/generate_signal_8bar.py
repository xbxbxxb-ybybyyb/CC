# @Time : 2022/1/20 15:37
# @Author : Zhichen Lu
# @File : generate_signal.py
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_short_integration
from dataApi.tradeDate import get_pre_trade_date
import os

param_map = {
   f'XGB_DTC_Future_{x}_Bar':[
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220211/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220211/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
    f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220211/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
] for x in range(1,8)
}

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/short_8bar/'
if not os.path.exists(out_path):
    os.makedirs(out_path)

for tag in param_map:
    params = dict(
    pct = 0,
    signal_file_name_list =  param_map[tag],
    subset_path_list = [x[:-1]+'_val_pred/' for x in param_map[tag]],
    start = 20170101,
    end = 20210531)
    print(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl')
    if os.path.exists(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl'):
        print(f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl','exist')
        continue
    res = get_signal_by_val_pct_threshold_short_integration(**params)
    print(tag)
    pd.to_pickle(res,f'{out_path}/signal_short_{tag}_pct_{params["pct"]}.pkl')