# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCash import StartWithLimitCash,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

per_amt_ratio = 0.0025
tag = 'XGB_DTC'
tag = tag+'_%.4f'%per_amt_ratio

signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_DTC20201217.pkl')
pred_ret[~signal] = np.nan
instance = StartWithLimitCash(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost, barly_max_buy=int(1/per_amt_ratio//7),per_amt_ratio=per_amt_ratio)
record = instance.run_backtest()
cash_series = instance.cash_series

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/per_ration_compare/%s_UpBuy_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True)

print(out_path)