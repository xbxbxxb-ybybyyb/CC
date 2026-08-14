# @Time : 2020/12/8 8:34
# @Author : Zhichen Lu
# @File : run_Sort240NoDistr.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.LimitHoldingAndEquallyDistribut import LimitHoldingAndEquallyDistribut,EvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold,get_periodly_ret_distribute
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_desample_minute_dict

pct_threshold = 0.05

cost = 0.001
max_holding = 300
max_barly_trigger = 100

# bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
# signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStd_union_train200_test10_factor_num400_norm_window_40.pkl'
# signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/5min/FactorEval/XGB5minFactorEval_sdt_adjusted_train200_test10_factor_num100_norm_window_40.pkl'
bar_list = get_desample_minute_dict(5)
bar_list = [bar_list[x] for x in bar_list]
bar_list = sorted(list(set(bar_list)))[:-1]
# signal,pred_ret = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl','_val_pred/'), signal_file, loading_type='new',
#                                                   bar_list=bar_list, val_tag='future')
tag = 'min5_NN_Comp100_param04'
pred_ret = pd.read_pickle('/data/group/800319/信号存储/%s'%tag)
pred_ret.index = pd.MultiIndex.from_tuples(pred_ret.index.tolist())
pred_ret = pred_ret.loc[20160104:].swaplevel(0,1).loc[bar_list].swaplevel(0,1).sort_index()
instance = LimitHoldingAndEquallyDistribut(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost, max_holding=max_holding)
helper = EvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
record = instance.run_backtest()
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Rev240DTC/%sDistr_InSample_UpHolding%d_UpBuy%d_%dbp_cost.xlsx' % (tag,
    max_holding, max_barly_trigger, int(10000 * cost))
helper.one_wave_run(record,48,output_path=out_path ,signal_record_save=True)

print(out_path)