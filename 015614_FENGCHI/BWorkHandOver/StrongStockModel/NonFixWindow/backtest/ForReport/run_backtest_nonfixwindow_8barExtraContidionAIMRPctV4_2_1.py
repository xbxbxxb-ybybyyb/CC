# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderNonFixSignal8BarExtraContition import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
import pandas as pd
from dataApi.sendInfo import send_file,send_message
from dataApi.tradeDate import get_pre_trade_date,get_recent_trade_date
import os,datetime,time
from StrongStockModel.model.ModelResultLoadingTool import generate_long_signal,generate_short_signal
from StrongStockModel.NonFixWindow.generate_signal.generate_signal_by_api_Min5Test import base_model_param
signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储20220512/'


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



condition = {
    'V4_2_1':'((((bar_first_trigger_num/bar_ratio)>(0.15*pool_num)) or ((bar_cum_first_trigger_num/barly_cum_ratio)>(0.15*pool_num))) or False)and (bar_down_trigger_signal/bar_trigger_signal)>0.5',
    'v6_2_1':'(((bar_first_trigger_num/bar_ratio)>(0.15*pool_num)) or ((bar_cum_first_trigger_num/barly_cum_ratio)>(0.15*pool_num)))and ((SZCZ/SZCZ_MA5 -1)<-0.008 or SZCZ_MA5_to_MA10<0)',
}


def calc_back_test_record(pct,per_amt_ratio, initial_cash, pool_num, deal_ratio, model_tag, alpha_pool_tag,down_signal_ratio,signal_threshold,down_definition,STAGE):
    start = 20170101
    end = 20220510

    condition_series = {
        get_pre_trade_date(start): f'((((bar_first_trigger_num/bar_ratio)>({signal_threshold}*pool_num)) or '
        f'((bar_cum_first_trigger_num/barly_cum_ratio)>({signal_threshold}*pool_num))) or False)and (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}'

    }

    tag = f'{model_tag}_{pct:.3f}_{alpha_pool_tag}_{down_signal_ratio:.2f}_{signal_threshold:.2f}_{down_definition:.3f}_NonFixSignal1000Base8Bar'
    file_name = '%s_%dbp_cost' % (tag, int(10000 * cost))
    base_dir = '/data/user/015664/AFuckingTrigger/限制买入和持仓/历史版本比对/'
    if not os.path.exists(f'{base_dir}/record/'):
        os.makedirs(f'{base_dir}/record/')
    record_file = f'{base_dir}/record/record_{file_name}.pkl'
    out_path = f'{base_dir}/{file_name}.xlsx'
    if os.path.exists(out_path):
        return
    if not os.path.exists(record_file) and STAGE==0:

        print('record not exist')
        short_signal = generate_short_signal(0, base_model_param[model_tag], start, end,
                                             f'{signal_path}/{model_tag}/short/')
        long_signal = generate_long_signal(pct, base_model_param[model_tag], start, end,
                                           f'{signal_path}/{model_tag}/long/')


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


        instance = StartWithLimitCashVolConsider(long_signal, short_signal, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt,condition_series=condition_series,down_swing_threshold=down_definition)
        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        pd.to_pickle([record,cash_series,holding_num,instance.condition_series],record_file)
        return
    elif os.path.exists(record_file) and STAGE==1:
        record, cash_series, holding_num = pd.read_pickle(record_file)[:3]
    elif STAGE==1:
        send_message(['015664'],f'{signal_threshold,down_signal_ratio,down_definition} no record')
        return
    else:
        print(f'{signal_threshold,down_signal_ratio,down_definition} record exist')
        return

    if STAGE==0:
        return

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)

no_running_period = [(610, 900), (1555, 1700),(1830,1915)]

def get_forbidden_tag():
    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    forbiden_period = False
    trading_day = get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d'))
    if trading_day:
        for s, e in no_running_period:
            if HHMM > s and HHMM < e:
                forbiden_period = True
                break
    return forbiden_period


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

from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
import itertools
para_list = [(1,1,0)]+list(itertools.product([ 0.3,0.4,0.5, 0.6, 0.7], [0.1,0.15,0.2,0.25,0.3], [-0.005, 0, 0.005]))
para_list = [x+(0.04,) for x in para_list] + [x+(0.03,) for x in para_list]
para_list_stage1= [x+(0,) for x in para_list]
para_list_stage2 = [x+(1,) for x in para_list]

if get_forbidden_tag():
    pass
else:
    d_signal_ratio,s_threshold,d_definition,pct_thre = 0.5,0.15,0,0.05
    calc_back_test_record(pct_thre,0.005, 2e8, 600,0.1, 'XGB_DTC_Matrix_Light_Cat', 'CS_XGB_OLS_condition_style_rank_ex20',
                          d_signal_ratio,s_threshold,d_definition,0)
    # calc_back_test_record(pct_thre, 0.005, 2e8, 600, 0.1, 'XGB_DTC_Matrix_Light_Cat', 'CS_XGB_OLS_condition_style_rank_ex20',
    #                       d_signal_ratio, s_threshold, d_definition, 1)
