# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from R2D2.ChangingCash.StartWithLimitCashVolConsiderNonFixSignal8BarExtraContitionChangingCashByRatioLimitShort import StartWithLimitCashVolConsider, \
    InitailCashBasedEvaluationHelper
import pandas as pd
from dataApi.sendInfo import send_file, send_message
from dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date
import os, datetime, time


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


bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

# long_param = {i: f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window_8barOriginFactor//signal_long_XGB_DTC_Matrix_Light_Cat_Future_{i}_Bar_pct_0.05.pkl' for i in range(1,9)}
# short_param = {i:f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/short_8barOriginFactor/signal_short_XGB_DTC_Matrix_Light_Cat_Future_{i}_Bar_pct_0.pkl' for i in range(1,8)}

long_param = {
    i: f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window_8barOriginFactorExpandForCondition//signal_long_XGB_DTC_Matrix_Light_Cat_Future_{i}_Bar_pct_0.05.pkl' for
    i in range(1, 9)}
short_param = {i: f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/short_8barOriginFactorExpandForCondition/signal_short_XGB_DTC_Matrix_Light_Cat_Future_{i}_Bar_pct_0.pkl' for i in
               range(1, 8)}


def calc_back_test_record(per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag, timing_tag, down_definition):
    start = 20170101
    end = 20211130
    condition_series = {
        get_pre_trade_date(start): 'False'
    }
    if timing_tag == 'NoTiming':
        timing_signal = pd.Series()
    else:
        timing_signal_path = '/data/group/800442/800319/Timing/BackTest/Signal/'
        timing_signal = pd.read_pickle(f'{timing_signal_path}{timing_tag}.pkl')
        timing_signal = timing_signal.stack()
        timing_signal = timing_signal[timing_signal.columns[0]]
    tag = f'{tag}_{alpha_pool_tag}_{timing_tag}_NonfixWindow'  # _{down_signal_ratio:.2f}_{signal_threshold:.2f}_{down_definition:.3f}_NonFixSignal1000Base8Bar'
    # tag = f'{tag}_{alpha_pool_tag}_{down_signal_ratio:.2f}_{signal_threshold:.2f}_{down_definition:.3f}_NonFixSignal1000Base8Bar'
    file_name = 'MaxBuy100_%s_%dbp_cost' % (tag, int(10000 * cost))
    base_dir = '/data/group/800442/800319/MarketTiming/NonFixWindowWithLongCompare/'
    if not os.path.exists(f'{base_dir}/record/'):
        os.makedirs(f'{base_dir}/record/')
    record_file = f'{base_dir}/record/record_{file_name}.pkl'
    out_path = f'{base_dir}/{file_name}.xlsx'
    if os.path.exists(out_path):
        print('res exist')
        send_file(['015664'], out_path)
        # return
    if not os.path.exists(record_file):
        stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
        alpha_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).loc[
                     start:end].rank(ascending=False, axis=1) < pool_num

        from dataApi.tradeDate import get_date_range
        append_pool = {}
        pool_path = '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/code_list/'
        date_list = get_date_range(start, end)
        date_list = sorted(list(set(date_list) - set(alpha_pool.index)))
        for date in date_list:
            if os.path.exists(f'{pool_path}{get_pre_trade_date(date)}.pkl'):
                temp_pool = pd.read_pickle(f'{pool_path}{get_pre_trade_date(date)}.pkl')
                append_pool[date] = pd.Series(True, index=[int(x[:6]) for x in temp_pool])
            else:
                print(date, 'not exist')

        append_pool = pd.DataFrame(append_pool).T.fillna(False).sort_index()
        append_pool = append_pool.reindex(date_list).fillna('pad')
        alpha_pool = pd.concat([alpha_pool, append_pool])

        original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
        original_pool = original_pool.drop(alpha_pool.index, axis=0)
        alpha_pool = pd.concat([original_pool, alpha_pool]).reindex(original_pool.columns, axis=1).sort_index() > 0.5

        short_signal = {}
        long_signal = {}
        for i in range(1, 9):
            temp_long_sigal, temp_long_pred_ret = pd.read_pickle(long_param[i])[:2]
            long_signal[i] = temp_long_pred_ret[temp_long_sigal.fillna(False)]
            print(f'window {i} {temp_long_sigal.index[0], temp_long_sigal.index[-1]}')
            if i < 8:
                temp_signal, temp_pred_ret = pd.read_pickle(short_param[i])[:2]
                short_signal[i] = temp_pred_ret[temp_signal.fillna(False)]
                print(f'window {i} {temp_signal.index[0], temp_signal.index[-1]}')
        instance = StartWithLimitCashVolConsider(long_signal, short_signal, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt, condition_series=condition_series, down_swing_threshold=down_definition, intra_discount_ratio=timing_signal)
        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        pd.to_pickle([record, cash_series, holding_num, instance.condition_series], record_file)
    else:
        record, cash_series, holding_num, _ = pd.read_pickle(record_file)
    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)


#    send_file(['015664'], out_path)


pool_dict = {'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl'}

# d_signal_ratio,s_threshold,d_definition = 0,0,0

timing_tag_list = ['cross2_ic_mdd_short3', 'cross2_ic_mdd100_short3',
                   'cross2_ic_mdd200_short3', 'cross2_ic_mdd300_short3',
                   'cross2_ic_mdd400_short3', 'cross2_ic_mdd500_short3',
                   'NoTiming']

from xquant.compute.aimr import AIMR

tm_tag = 'NoTiming'
# tm_tag = 'long_short3'
# tm_tag = 'XGB300'

calc_back_test_record(0.005, 2e8, 600, 0.1, 'XGB_DTC_Matrix_Light_CatNonFixWindow', 'CS_XGB_OLS_condition_style_rank_ex20', tm_tag, 0)
print(tm_tag)