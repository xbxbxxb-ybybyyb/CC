# @Time : 2020/12/21 17:19
# @Author : Zhichen Lu
# @File : run_StartWithLimitCashRev.py

# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashRev import StartWithLimitCash,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
max_barly_trigger = 100

file_list_xgb = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']
# Linear
file_list_linear = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl']
# NN
file_list_nn = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStd_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']

# (pct, subset_path_list, signal_file_name_list, start,val_tag=0,loading_type=None)
para={
     'XGB_DTC':file_list_xgb,
     'Linear_DTC':file_list_linear,
     'XGB_Linear_DTC':file_list_linear+file_list_xgb
}
tag = 'XGB_Linear_DTC'
file_list = para[tag]

signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,0,'old')
pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Linear_DTC20201221.pkl')
# signal,pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_Linear_DTC.pkl')
pred_ret[~signal] = np.nan
instance = StartWithLimitCash(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost, barly_max_buy=max_barly_trigger)
record = instance.run_backtest()
cash_series = instance.cash_series

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/%sRev_UpBuy%d_%dbp_cost.xlsx' % (tag,
     max_barly_trigger, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True)

# print(out_path)