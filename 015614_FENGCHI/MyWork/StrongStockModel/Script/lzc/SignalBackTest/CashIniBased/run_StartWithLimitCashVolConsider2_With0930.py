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


# max_barly_trigger = 100

para = {'XGB_lightGBM_CatBoost': [
    '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
    '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
],
}
pct_threshold = 0.1
per_amt_ratio = 0.05
deal_ratio = 0.1
initial_cash = 2e7

bar_list = [930]
cost = 0.001
print(pct_threshold, per_amt_ratio)
tag = 'XGB_lightGBM_CatBoost'
print(tag)
file_list = para[tag]
from Script.lzc.pitches_integration import out_signal

for each in file_list:
    if not os.path.exists(each):
        out_signal(each.replace('.pkl', '/'), 20181231)

print(file_list)

# tag = tag + 'WithMax5threshold'
# if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)):
#     print(pct_threshold, 'signal exist')
#     signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
# else:
#     signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list],
#                                                                    file_list, 20160104, 'actual_label', 'new', head=73)
#     pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))

# pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
tag = tag + 'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))
# pred_ret[~signal.fillna(False)] = np.nan
pred_ret = pd.DataFrame()
pred_ret_930 = pd.read_pickle('/data/group/800319/信号存储/sign930V4.pkl').shift(1)
tag = tag.replace('RevTriggerFilterHolding', 'Only930V4_RevTriggerFilterHolding')

pred_ret = pd.concat([pred_ret, pred_ret_930]).sort_index()

# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False, axis=1) < 600
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/stock_pool/stock_pool_20210426.pkl').shift(1).rank(ascending=False, axis=1) < 600
alpha_pool = pd.DataFrame()
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1)  # .loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index, axis=0)
alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
tag = tag.replace('RevTriggerFilterHolding', '930PoolTop600')
# col_list688 = list(filter(lambda x : str(x).startswith('688'),alpha_pool.columns.tolist()))
# alpha_pool.loc[:,col_list688] = False
restrict_list = pd.read_pickle('/data/group/800319/strategy_local_path3_for_930/restrict_list.pkl')
restrict_list = list(set(alpha_pool.columns).intersection([int(x[:-3]) for x in restrict_list]))
alpha_pool.loc[:, restrict_list] = False
# res3 = get_daily_active_stock(20151231, 20181231).shift(1)
# tag = tag.replace('RevTriggerFilterHolding','RevTriggerFilterHolding_Concept')
instance = StartWithLimitCashVolConsider(pred_ret, 20201104, 20210104, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash)
record = instance.run_backtest()

pd.to_pickle([instance.daily_holding, instance.daily_buy_time_info, instance.daily_conf], '/data/group/800319/strategy_local_path/FolderFor930/fake_sample.pkl')

# ###########################
#
# from dataApi.sendInfo import send_file
# import pandas as pd
# import os
# import configparser
# from online_conf import code_list_path
# from dataApi.getData import trans_int2windcode
# from dataApi.tradeDate import get_pre_trade_date
# # conf = configparser.ConfigParser()
#
# daily_holding,daily_buy_time_info,daily_conf = pd.read_pickle('/data/group/800319/strategy_local_path/FolderFor930/fake_sample.pkl')
# vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
# vol_info = vol_info.swaplevel(0,1).loc[930].loc[20201101:]
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').rank(ascending=False, axis=1) < 600
# alpha_pool.columns = alpha_pool.columns.map(trans_int2windcode)
#
# for date in daily_holding:
#     if date<20201101:
#         continue
#     stk_list = alpha_pool.loc[date]
#     stk_list = stk_list[stk_list].index.tolist()
#     pd.to_pickle(stk_list,f'{code_list_path}{date}.pkl')
#
#     pre_date = get_pre_trade_date(date)
#     next_day = get_pre_trade_date(date,-1)
#     if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/'):
#         os.mkdir(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/')
#     if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyOut/'):
#         os.mkdir(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyOut/')
#     if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyIn/'):
#         os.mkdir(f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyIn/')
#     pd.to_pickle(vol_info.loc[date].fillna(0), f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyIn/vol_info{date}.pkl')
#
#     holding_info = pd.Series(daily_holding[date])
#     buy_time_info = pd.Series(daily_buy_time_info[date]).reindex(holding_info.index).apply(lambda x : x[:2])
#
#     holding_info.index = holding_info.index.map(trans_int2windcode)
#     buy_time_info.index = buy_time_info.index.map(trans_int2windcode)
#
#     init_conf = daily_conf[date].copy()
#     holding_info['cash'] = init_conf['cash']
#
#     temp_signal = pred_ret_930.loc[(date, 930)].dropna()
#     temp_signal.index = temp_signal.index.map(trans_int2windcode)
#     pd.to_pickle(temp_signal,f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyIn/signal{date}.pkl')
#     pd.to_pickle(dict(holding_info),f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyOut/holding{date}.pkl')
#     pd.to_pickle(dict(buy_time_info),f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyOut/buy_time_info{date}.pkl')
#     pd.to_pickle(init_conf,f'/data/group/800319/strategy_local_path3/FolderFor930/{date}/StrategyIn/init{date}.pkl')
#
#
#
#
#
# ##########################


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
