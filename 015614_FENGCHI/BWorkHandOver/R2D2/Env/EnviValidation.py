# @Time : 2021/6/21 10:56
# @Author : Zhichen Lu
# @File : EnviValidation.py

from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider
from StrongStockModel.conf.path_config import deal_price_path

import pandas as pd
import numpy as np

start=20171115
end=20171130
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_lightGBM_CatBoostWithMax5threshold_0.05.pkl')
signal = signal.loc[start:end]
pred_ret = pred_ret.loc[start:end]
pred_ret[~signal] = np.nan

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
pct_threshold = 0.05
per_amt_ratio = 0.005
deal_ratio = 0.1
initial_cash = 2e8
pool_num = 600

instance = StartWithLimitCashVolConsider(pred_ret, start, end,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio,barly_max_buy=100,initial_cash=initial_cash)
instance.run_backtest()
