# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderChangingCash import StartWithLimitCashVolConsiderChangingCash, \
    InitailCashBasedEvaluationHelper

import pandas as pd
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from ExtraTools import get_path_conf

path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
code_list_path, local_config_path = [path_conf[x] for x in 'code_list_path,local_config_path'.split(',')]
# from online_conf import code_list_path, local_config_path




def get_signal_by_zscore_integration(path_file_list, threshold=0.05):
    res_list = {}
    for each in path_file_list:
        temp = pd.read_pickle(each)
        res_list[each] = temp['adjusted_prediction']
    res_df = pd.DataFrame(res_list)
    pred_ret = res_df.mean(axis=1)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.pivot_table(index=[pred_ret.columns[0], pred_ret.columns[1]], columns=pred_ret.columns[2], values=0)
    return pred_ret > threshold, pred_ret


pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

backtest_start_date = 20210910
pre_date = 20211215
per_amt_ratio = 0.005

per_ratio_change = {}
pct_threshold_change = {}

cash_flow = {}
max_trigger_num = {}
deal_ratio = 0.1
strategy_tag = 'XGB_Cat_Light_SWMatrix'
final_tag = strategy_tag + '_OnlineTest'+ 'AllMkt_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)

signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_SWMatrix_OnlineTest_20211215.pkl')
pred_ret[~signal] = np.nan
original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')


alpha_pool = original_pool.shift(1).loc[backtest_start_date:pre_date]
unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
alpha_pool.loc[:, list(unavailable_pool.intersection(set(alpha_pool.columns)))] = False
alpha_pool = alpha_pool.fillna(False)



instance = StartWithLimitCashVolConsiderChangingCash(pred_ret, backtest_start_date, pre_date, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                     per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                     deal_percent=deal_ratio, initial_cash=2000000, cash_added=cash_flow, per_ratio_change=per_ratio_change, max_trigger_num=max_trigger_num)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x: instance.last_buy_time[x][0] * 10000 + instance.last_buy_time[x][1] for x in instance.holding}
# pd.to_pickle([record, cash_series, holding_num], '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪_股票池之间对比/record/%sOnlineTracing.pkl' % final_tag)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪_股票池之间对比2/%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (final_tag, int(10000 * cost), pre_date)
_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)

