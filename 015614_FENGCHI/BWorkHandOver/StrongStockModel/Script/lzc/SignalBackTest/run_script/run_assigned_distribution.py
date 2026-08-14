# @Time : 2020/12/4 9:26
# @Author : Zhichen Lu
# @File : run_assigned_distribution.py

from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.LimitHoldingAndAssignedDistribut import LimitHoldingAndAssignedDistribut,EvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold,get_periodly_ret_distribute
import pandas as pd
import numpy as np

pct_threshold = 0.05
point_list = [1000,1030,1100,1300,1330,1400,1430]
cost = 0.001
max_holding = 300
signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num100_norm_window_40.pkl'
signal,pred_ret = get_signal_by_val_pct_threshold(pct_threshold,signal_file.replace('.pkl','_val_pred/'),signal_file,loading_type='old')
signal,pred_ret = signal.swaplevel(0,1).loc[point_list].swaplevel(0,1),pred_ret.swaplevel(0,1).loc[point_list].swaplevel(0,1)
pred_ret[~signal] = np.nan
distribution = get_periodly_ret_distribute(signal_file,signal,loading_type='old')
# pd.to_pickle(distribution,'/data/user/015664/AFuckingTrigger/限制买入和持仓/动态触发分布/XGBFactorEval_ic_all_t_distribution.pkl')
instant = LimitHoldingAndAssignedDistribut(pred_ret,20160104,20181231,
                                           target_point=point_list,buy_cost=cost,sell_cost=cost,
                                           max_holding=max_holding,distribution=distribution)
helper = EvaluationHelper(buy_cost_ratio=cost,sell_cost_ratio=cost)
record = instant.run_backtest()
out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/动态触发分布/XGB5min30BarAssignedDistribution_InSample_UpHolding%d_cost%dbp.xlsx' % (max_holding, int(10000 * cost))

helper.one_wave_run(record,48,output_path=out_file)