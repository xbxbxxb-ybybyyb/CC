# @Time : 2021/1/6 8:48
# @Author : Zhichen Lu
# @File : integrate_factor_for_hx.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100

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

para={
     'XGB_DTC':file_list_xgb,
     'Linear_DTC':file_list_linear,
     'XGB_Linear_DTC':file_list_linear+file_list_xgb
}
per_amt_ratio = 0.005
tag = 'XGB_Linear_DTC'
file_list = para[tag]
deal_ratio = 0.2
import pandas as pd
signal, pred_ret,subset_dict = pd.read_pickle('/data/group/800319/信号存储/IntegratedFactorForHX20210106.pkl')
signal_old, pred_ret_old = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Linear_DTC20201221.pkl')
signal, pred_ret,subset_dict = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,
                                                               0,'old',get_subset=True)
pd.to_pickle([signal, pred_ret,subset_dict],'/data/group/800319/信号存储/IntegratedFactorForHX20210106.pkl')
