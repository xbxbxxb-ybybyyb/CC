# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider5min import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration, get_signal_by_val_pct_threshold_integration_NoMaxThreshold
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os
from dataApi.sendInfo import send_file
from Script.lzc.pitches_integration import out_signal


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

from dataApi.tradeDate import get_desample_minute_dict
bar_list = get_desample_minute_dict(5)
bar_list = sorted(list(set([bar_list[x] for x in bar_list])))[:-1]
# bar_list
# bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
para = {
    'XGB5min_DTC20210624':[
    '/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_d_train200_test10_factor_num100/XGB5min_ic_half_d_train200_test10_factor_num100.pkl',
    '/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_t_train200_test10_factor_num100/XGB5min_ic_half_t_train200_test10_factor_num100.pkl',
    '/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_c_train200_test10_factor_num100/XGB5min_ic_half_c_train200_test10_factor_num100.pkl',

    ],

    'XGB5min_D':['/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_d_train200_test10_factor_num100/XGB5min_ic_half_d_train200_test10_factor_num100.pkl'],
    'XGB5min_T':['/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_t_train200_test10_factor_num100/XGB5min_ic_half_t_train200_test10_factor_num100.pkl'],
    'XGB5min_C':['/data/group/800319/junkData/StrongStock//ModelRes/XGB5min_ic_half_c_train200_test10_factor_num100/XGB5min_ic_half_c_train200_test10_factor_num100.pkl'],
}

def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag):

    start = 20170101
    end = 20201231
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    # /data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_XGB_DCMultiFreq_T_Light_CatWithMax5threshold_0.05.pkl
    if os.path.exists(f'/data/group/800319/信号存储/{tag}_{pct_threshold:.2f}.pkl'):

        print(pct_threshold, 'signal exist')
        pred_ret = pd.read_pickle(f'/data/group/800319/信号存储/{tag}_{pct_threshold:.2f}.pkl')
        if isinstance(pred_ret,tuple) or isinstance(pred_ret,list):
            signal, pred_ret = pred_ret
            pred_ret[~signal] = np.nan
        elif isinstance(pred_ret,pd.DataFrame):
            pass
        else:
            raise Exception('Unexpected type')
        print(f'/data/group/800319/信号存储/{tag}_{pct_threshold:.2f}.pkl')
    else:
        file_list = para[tag]
        for each in file_list:
            if not os.path.exists(each):
                out_signal(each.replace('.pkl','/',20210601))
        signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, 20160104,
                                                                                      'actual_label',
                                                                                      'new',
                                                                                      head=133)
        pd.to_pickle([signal, pred_ret],f'/data/group/800319/信号存储/{tag}_{pct_threshold:.2f}.pkl')
        pred_ret[~signal] = np.nan
    # pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
    # pred_ret[~signal.fillna(False)] = np.nan
    if isinstance(pool_dict[alpha_pool_tag],pd.DataFrame):
        alpha_pool = pool_dict[alpha_pool_tag].shift(1).loc[start:end]
    elif isinstance(pool_dict[alpha_pool_tag],str):
        alpha_pool = pd.read_pickle(f'/data/group/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num
    else:
        raise Exception('Wrong type')
    # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
    original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    tag = tag + '%s_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (alpha_pool_tag,deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))
    tag = tag+'bar_num%d'%len(bar_list) + 'NoPastLimit'
    print(tag)

    instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio,
                                             append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_5min_FullSample.pkl',
                                                           'future_deal_vol':deal_price_path + 'vol_future_rolling_5_sum.pkl',
                                                           'past_vol_path':deal_price_path + 'vol_rolling_future_5min_sum_5day_mean.pkl'},
                                             deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                             stk_min_amt=stk_min_amt)

    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num
    pd.to_pickle([record,cash_series,holding_num], '/data/user/015664/AFuckingTrigger/限制买入和持仓/Freq5min/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    #
    out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Freq5min/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    for each in record:
        helper.record[each] = record[each]
    # helper.evaluat_signal_by_stk(2260)
    # out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)


# pct_threshold = 0.05
# per_amt_ratio = 0.005
# initial_cash = 2e8
from xquant.compute.aimr import AIMR
import itertools, gc

# para_list = list(itertools.product([0.03, 0.04, 0.05, 0.06], [0.005, 0.007, 0.009, 0.01, 0.02, 0.025, 0.05], [2e8],[200,400]))
# para_list = list(itertools.product([0.04, 0.05, 0.06], [0.005, 0.01, 0.02], [2e8],[200,400]))
# len(para_list)
# total = 18
# i = int(AIMR.getParam())
# pct_threshold,per_amt_ratio,initial_cash = para_list[i]
# for each in para_list[len(para_list) * i // total:len(para_list) * (i + 1) // total]:
#     calc_back_test_record(*(each + (0.1, 'XGB_lightGBM_CatBoost')))
#     gc.collect()
from dataApi.ConceptApi import get_basic_values
pool_dict = {
    'old': 'daily_stock_score_v3_20210127.pkl',
    'condition_mv': 'CS_OLS_condition_mv_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'rank_ex20': 'CS_OLS_condition_style_rank_ex20_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'NoCondition': 'CS_OLS_no_condition_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_OLS': 'CS_OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB': 'CS_XGB_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'stock_pool_20210610':'stock_pool_20210610.pkl',
    'XGB_OLS20210624':'XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h135d_uniform20t50.pkl',
    'Open_Board':get_basic_values('Open_Board_stock')
}


# pool_tag = 'old'
each = (0.05, 0.005, 2e8, 600)

calc_back_test_record(*(each + (1, 'XGB5min_DTC20210624', 'XGB_OLS20210624')))


# calc_back_test_record(*(each + (0.1, 'XGBMonthly_DTC', 'rank_ex20')))
