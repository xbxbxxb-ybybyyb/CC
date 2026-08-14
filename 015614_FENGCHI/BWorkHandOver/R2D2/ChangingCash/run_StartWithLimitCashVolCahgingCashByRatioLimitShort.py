# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from R2D2.ChangingCash.StartWithLimitCashVolConsiderChangingCashByRatioLimitShort import StartWithLimitCashVolConsiderChangingCash, \
    InitailCashBasedEvaluationHelper
import pandas as pd
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from online_conf import code_list_path, local_config_path


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

per_amt_ratio = 0.005
deal_ratio = 0.1

per_ratio_change = {
}
discount_ratio = {
}

intra_ratio = pd.read_pickle('/data/group/800442/800319/MarketTiming/FixTime20220127.pkl')
intra_ratio = pd.Series(intra_ratio).clip(0, 1)

max_trigger_num = {}
tag = 'FixTimeShortOldFrame'

start = 20170101
end = 20210531

signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGBWithSWSHIFReSaveTWithOrigin_Cat_LightWithoutMax5_0.05.pkl')
pred_ret = pred_ret[signal]
tag = tag + 'AlphaTriggerPoolTop600_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)

original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')
pool_num = 600
alpha_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).loc[start:end].rank(
    ascending=False, axis=1) < pool_num
original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
original_pool = original_pool.drop(alpha_pool.index, axis=0)
alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5

instance = StartWithLimitCashVolConsiderChangingCash(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                     per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                     deal_percent=deal_ratio, initial_cash=200000000, discount_ratio_series=discount_ratio, per_ratio_change=per_ratio_change,
                                                     max_trigger_num=max_trigger_num, intra_discount_ratio=intra_ratio)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x: instance.last_buy_time[x][0] * 10000 + instance.last_buy_time[x][1] for x in instance.holding}
pd.to_pickle([record, cash_series, holding_num], '/data/group/800442/800319/MarketTiming/ShortTuning/%sOnlineTracing.pkl' % tag)

# record, cash_series, holding_num = pd.read_pickle('/arch1/user/015664/%sOnlineTracing.pkl' % tag)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/group/800442/800319/MarketTiming/%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (tag, int(10000 * cost), end)
_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
from dataApi.sendInfo import send_file

send_file(['015664'], out_path)
# send_file(['015664'], '/data/group/800442/800319/MarketTiming/FixTime20220127AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050VolConsiderOnlineLimit_UpBuy100_10bp_cost_20210531.xlsx')
