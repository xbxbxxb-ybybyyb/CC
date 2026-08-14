# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderV2 import StartWithLimitCashVolConsiderV2, InitailCashBasedEvaluationHelper

import pandas as pd

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

per_amt_ratio = 0.005
tag = 'Linear_XGB_DTC_16_18'

deal_ratio = 0.1

tag = tag + '_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Linear_DTC20201221.pkl')
pred_ret = pred_ret[signal]
instance = StartWithLimitCashVolConsiderV2(pred_ret, 20180101, 20181231, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                           per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_20160104_20181228.pkl'},
                                           deal_percent=deal_ratio)
record = instance.run_backtest()
pd.to_pickle(record, '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderV2/record/%sInSample.pkl' % tag)

cash_series = instance.cash_series

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderV2/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True)

print(out_path)
