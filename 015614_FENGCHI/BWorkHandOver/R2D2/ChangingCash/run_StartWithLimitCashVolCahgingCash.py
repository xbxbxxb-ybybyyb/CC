# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from R2D2.ChangingCash.StartWithLimitCashVolConsiderChangingCash import StartWithLimitCashVolConsiderChangingCash, \
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

backtest_start_date = 20210406
per_amt_ratio = 0.005
deal_ratio = 0.1

per_ratio_change = {
    20210525: 0.02,
    20210617: 0.01,
    20210624: 0.005,
    20210727: 0.006,
    20210729: 0.00167,
    20210730: 0.005,
    20210803: 0.003125,
    20210804: 0.005,
}
cash_flow = {20210413: 28000000,
             20210420: -20000000,
             20210506: 20000000,
             20210513: 50000000,
             20210525: 120000000,
             20210527: -170000000,
             20210603: 50000000,
             20210604: 70000000,
             20210616: -10000000,
             20210706: 60000000,
             20210727: -50000000,
             20210730: -100000000 - 7925804.88,
             20210802: 30000000,
             20210804: -30000000,
             20210817: -30859736.86,
             20210825: 20000000,
             20210827: 30000000,
             20210928: -36846732.2,
             20210930: 36846732.2,
             20211015: -44401839.49,
             20211105: 30000000,
             20211111: 50000000,
             20211126: -80000000
             }
max_trigger_num = {20210729: 28, 20210730: 100, 20210803: 28}
tag = 'XGB_Cat_Light'
tag = tag + '_OnlineTest'

start = 20210406
end = get_pre_trade_date(20211201)

signal, pred_ret = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_{tag}_{pre_date}.pkl')

# pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
# pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
tag = tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
pred_ret[~signal] = np.nan

original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')

alpha_pool = []
for date in get_date_range(get_pre_trade_date(backtest_start_date), end):
    temp_pool = pd.read_pickle(f'{code_list_path}{date}.pkl')
    temp_pool = pd.DataFrame(True, index=[date], columns=temp_pool)
    alpha_pool.append(temp_pool)
alpha_pool = pd.concat(alpha_pool)
alpha_pool.columns = [int(x[:-3]) for x in alpha_pool.columns]
alpha_pool = alpha_pool.reindex(original_pool.columns, axis=1).fillna(False).shift(1).loc[backtest_start_date:]

unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
alpha_pool.loc[:, list(unavailable_pool.intersection(set(alpha_pool.columns)))] = False
alpha_pool = alpha_pool.fillna(False)

tag = tag.replace('RevTriggerFilterHolding', 'RevTriggerFilterHolding_AlphaTriggerPoolTop600')

instance = StartWithLimitCashVolConsiderChangingCash(pred_ret, backtest_start_date, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                     per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                     deal_percent=deal_ratio, initial_cash=2000000, cash_added=cash_flow, per_ratio_change=per_ratio_change,
                                                     max_trigger_num=max_trigger_num)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x: instance.last_buy_time[x][0] * 10000 + instance.last_buy_time[x][1] for x in instance.holding}
pd.to_pickle([record, cash_series, holding_num], '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/record/%sOnlineTracing.pkl' % tag)

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (tag, int(10000 * cost), pre_date)
_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)

pd.to_pickle([res_pn, last_buy_time], f'/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/daily_res_pn/{pre_date}.pkl')
print(out_path)
cash_flow[get_pre_trade_date(backtest_start_date)] = 2000000
