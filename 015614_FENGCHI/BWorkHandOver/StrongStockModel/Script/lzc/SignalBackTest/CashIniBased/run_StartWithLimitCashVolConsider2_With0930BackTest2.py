# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

from conf.path_config import deal_price_path
from backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
import pandas as pd



bar_list = [930]
cost = 0.001

per_amt_ratio = 0.015
deal_ratio = 0.3
initial_cash = 2e8



pred_ret_930 = pd.read_pickle('/data/group/800319/信号存储/morning_model/olsF4top20.pkl')

pred_ret = pred_ret_930.sort_index()


instance = StartWithLimitCashVolConsider(pred_ret, 20170101, 20210430, stock_pool=None, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash)
record = instance.run_backtest()

cash_series = instance.cash_series
holding_num = instance.holding_num
cash_series.index = cash_series.index.astype(int).astype(str)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)

out_path = 'data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraWith930/olsF4top20HXCode.xlsx'
helper.one_wave_run(record, cash_series, 16, output_path=out_path, signal_record_save=True, holding_num=holding_num)
print(out_path)
