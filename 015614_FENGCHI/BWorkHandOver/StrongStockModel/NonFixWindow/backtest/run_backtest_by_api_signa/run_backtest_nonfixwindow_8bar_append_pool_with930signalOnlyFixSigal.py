# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderNonFixSignal8BarWith930 import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
import pandas as pd
from dataApi.sendInfo import send_file
from StrongStockModel.model.ModelResultLoadingTool import generate_long_signal,generate_short_signal
from StrongStockModel.NonFixWindow.generate_signal.generate_signal_by_api_Min5Test import base_model_param,signal_path,get_nonfix_signal_with_930


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


bar_list = [930,1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

def calc_back_test_record(pct,per_amt_ratio, initial_cash, pool_num, deal_ratio, FIX_tag, alpha_pool_tag):
    start = 20170101
    end = 20210531
    # long_signal,short_signal,final_tag = get_nonfix_signal_with_930(pct_thre,0,start,end,FIX_tag,TAG_930)
    long_signal = generate_long_signal(pct,base_model_param[FIX_tag],start,end,f'{signal_path}/{FIX_tag}/long/')
    short_signal = generate_short_signal(0,base_model_param[FIX_tag],start,end,f'{signal_path}/{FIX_tag}/short/')

    tag = FIX_tag + alpha_pool_tag+'_OnlyFixSignal'
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    alpha_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).loc[
                 start:end].rank(ascending=False, axis=1) < pool_num
    from dataApi.tradeDate import get_date_range, get_pre_trade_date
    import os
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
    print(f'max pool num {alpha_pool.sum(axis=1).max}')


    file_name = f'{tag}_threshold_{pct:.3f}_{int(10000*cost)}bp_cost' #% (tag, int(10000 * cost))
    if not os.path.exists(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFixWindow/record_{file_name}.pkl'):
        print('record not exist')
        instance = StartWithLimitCashVolConsider(long_signal, short_signal, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        pd.to_pickle([record,cash_series,holding_num],f'/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFixWindow/record_{file_name}.pkl')
    else:
        print('record exist')
        record, cash_series, holding_num = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFixWindow/record_{file_name}.pkl')

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    out_path = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFixCompare930/{file_name}.xlsx'
    if not os.path.exists(os.path.split(out_path)[0]):
        os.makedirs(os.path.split(out_path)[0])
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)


pool_dict = {
    'old': 'daily_stock_score_v3_20210127.pkl',
    'condition_mv': 'CS_OLS_condition_mv_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'rank_ex20': 'CS_OLS_condition_style_rank_ex20_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'NoCondition': 'CS_OLS_no_condition_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_OLS': 'CS_OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB': 'CS_XGB_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'stock_pool_20210610': 'stock_pool_20210610.pkl',
    'OLS_XGB200_20211213': 'OLS_XGB200_20211213.pkl',
    'XGB_OLS_style_ex20': 'XGB_OLS_style_ex20.pkl',

    'OLS_XGB200_val_5': 'OLS_XGB200.pkl',
    'XGB_OLS_style_ex20_val_5': 'XGB_OLS_style_ex20.pkl',

    'OLS_XGB200': 'OLS_XGB200.pkl',
    'OLS_T3': 'OLS_T3.pkl',
    'OLS_XGB200_auction': 'OLS_XGB200_auction.pkl'
}
from xquant.compute.aimr import AIMR

pct_thre = 0.05#eval(AIMR.getParam())
each = (pct_thre, 0.005, 2e8, 600)
calc_back_test_record(*(each + (0.1,'XGB_DTC', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1,'XGB_DTC','XGB_Min5_DTC707', 'CS_XGB_OLS_condition_style_rank_ex20')))

