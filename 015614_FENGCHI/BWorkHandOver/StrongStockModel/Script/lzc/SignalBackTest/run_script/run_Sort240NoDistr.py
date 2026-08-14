# @Time : 2020/12/8 8:34
# @Author : Zhichen Lu
# @File : run_Sort240NoDistr.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.LimitHoldingAndBarTriggerWith240MoreHolding import LimitHoldingAndBarTriggerWith240MoreHolding,EvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold
import pandas as pd
import numpy as np

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
max_holding = 300
max_barly_trigger = 100
window = 10
signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStd_union_train200_test10_factor_num100_norm_window_40.pkl'

#每次用上一个模型的结果做阈值
# signal,pred_ret = get_rolling_threshold_with_no_val_set(pct_threshold,signal_file,signal_file.replace('.pkl','_val_pred/'),val_tag=0,loading_type='old')
#每天用滚动前5天的结果做阈值(开头5天包含上一个模型)

# signal_old,pred_ret_old = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl','_val_pred/'), signal_file, loading_type='old', bar_list=bar_list, val_tag=0)
# pd.to_pickle([signal_old,pred_ret_old],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_T.pkl')
# signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_T.pkl')
signal, pred_ret = get_signal_by_val_pct_threshold(pct_threshold,signal_file.replace('.pkl','_val_pred/'),signal_file,val_tag='future',loading_type='new')
print('loading signal done')
pred_ret[~signal] = np.nan
# pd.to_pickle(pred_ret,'/data/user/015664/限制买入和持仓/信号存储/')
instance = LimitHoldingAndBarTriggerWith240MoreHolding(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost, max_holding=max_holding, barly_max_buy=max_barly_trigger)
helper = EvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
record = instance.run_backtest()
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/LSTM_union_SeperateEnsemble_InSample_UpHolding%d_UpBuy%d_%dbp_cost.xlsx' % (
    max_holding, max_barly_trigger, int(10000 * cost))
helper.one_wave_run(record,48,output_path=out_path ,signal_record_save=True)

print(out_path)