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


bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100

para = {
    'XGB_lightGBM_CatBoost': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
}



def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash,pool_num, deal_ratio, tag):
    file_list = para[tag]
    print(file_list)
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    tag = tag + 'WithMax5threshold'
    if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)):
        print(pct_threshold, 'signal exist')
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
        print('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
    else:
        signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, 20160104, 'actual_label',
                                                                       'new',
                                                                       head=73)
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))

    # pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
    tag = tag + 'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))
    pred_ret[~signal.fillna(False)] = np.nan

    alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False, axis=1) < pool_num
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    tag = tag.replace('RevTriggerFilterHolding', f'AlphaTriggerPoolV3Top{pool_num}_real{pool_num}')

    start,end =20170101,20210531
    out_file = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/查验回撤不一致原因/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top600_敏感性测试代码_{start}_{end}.xlsx'
    print(out_file)
    if not os.path.exists(out_file):
        instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        order_info = instance.order_info
        helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
        #
        # out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
        for each in record:
            helper.record[each] = record[each]
        # helper.evaluat_signal_by_stk(2260)
        helper.one_wave_run(record, cash_series, 48, output_path=out_file, signal_record_save=True, holding_num=holding_num)

    else:
        print(tag,'exist')
    send_file(['015664'],out_file)


each = (0.05,0.005,2e8,600)
calc_back_test_record(*(each + (0.1, 'XGB_lightGBM_CatBoost')))

