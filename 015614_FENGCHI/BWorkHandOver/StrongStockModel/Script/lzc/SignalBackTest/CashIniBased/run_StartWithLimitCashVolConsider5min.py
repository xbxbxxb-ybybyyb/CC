# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.tradeDate import get_desample_minute_dict

bar_list = get_desample_minute_dict(5)
bar_list = sorted(list(set([bar_list[x] for x in bar_list])))[5:-6]
pct_threshold = 0.05
cost = 0.001
per_amt_ratio = 0.005
tag = 'HXSignal20210107_5min'
deal_ratio = 0.1
tag = tag + '_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
pred_ret = pd.read_pickle('/data/group/800319/信号存储/IntegratedFactor5Min20210107.pkl')

alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False, axis=1) < 600
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index, axis=0)
alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
tag = tag + 'AlphaPoolTOP600'

instance = StartWithLimitCashVolConsider(pred_ret, 20160104, 20181231, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                           deal_percent=deal_ratio)
record = instance.run_backtest()

cash_series = instance.cash_series
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEra/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=instance.holding_num)

print(out_path)
