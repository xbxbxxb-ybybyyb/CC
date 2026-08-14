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
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os
from dataApi.sendInfo import send_file


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


para = {
    'olsF4top10':'/data/group/800319/信号存储/morning_model/olsF4top10.pkl',
    'olsF4top20':'/data/group/800319/信号存储/morning_model/olsF4top20.pkl'
}

pct_threshold = 0.1
per_amt_ratio = 0.03
deal_ratio = 0.1
initial_cash = 2e7
start = 20170103
end = 20210430

bar_list = [930]
cost = 0.001
print(pct_threshold, per_amt_ratio)
tag = 'olsF4top10'
print(tag)
pred_ret = pd.DataFrame()
pred_ret_930 = pd.read_pickle(para[tag]).shift(1)


pred_ret = pd.concat([pred_ret, pred_ret_930]).sort_index()

alpha_pool = pd.DataFrame()
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1)  # .loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index, axis=0)
alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
restrict_list = pd.read_pickle('/data/group/800319/strategy_local_path3/restrict_list.pkl')
restrict_list = list(set(alpha_pool.columns).intersection([int(x[:-3]) for x in restrict_list]))
alpha_pool.loc[:, restrict_list] = False
instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash)
record = instance.run_backtest()

# pd.to_pickle([instance.daily_holding, instance.daily_buy_time_info, instance.daily_conf], '/data/group/800319/strategy_local_path/FolderFor930/fake_sample.pkl')

cash_series = instance.cash_series
holding_num = instance.holding_num
cash_series.index = cash_series.index.astype(int).astype(str)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraWith930/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
print(out_path)
send_file(['015664'], out_path)

# union_stk = sorted(list(set(signal.columns).union(set(pred_ret_930.columns))))
# final_signal = signal.swaplevel(0,1).loc[1430].reindex(union_stk,axis=1)>0.5
# signal_930 = pred_ret_930.reindex(union_stk,axis=1).notnull().swaplevel(0,1).loc[930]
#
# overlap_index = sorted(list(set(final_signal.index).intersection(set(signal_930.index))))
# intersection = final_signal.loc[overlap_index]&signal_930.loc[overlap_index]
# intersection.sum(axis=1)
