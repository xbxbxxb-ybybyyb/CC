# @Time : 2020/12/22 10:16
# @Author : Zhichen Lu
# @File : calc_signal.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashConcept import StartWithLimitCashConcept,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd


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

tag = 'XGB_DTC'
file_list = para[tag]

for pct_threshold in [0.06,0.07,0.08,0.09,0.1]:
    signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,0,'old')
    pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_DTC_%dpct_threshold.pkl'%int(pct_threshold*100))
    print(pct_threshold)