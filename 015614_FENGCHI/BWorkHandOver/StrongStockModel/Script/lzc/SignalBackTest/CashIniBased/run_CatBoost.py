# @Time : 2021/5/16 11:43
# @Author : Zhichen Lu
# @File : run_validation.py

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
from Script.lzc.pitches_integration import out_signal
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


bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100

path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/'
file_list = list(filter(lambda x: not x.endswith('_zscore.pkl') and x.endswith('.pkl'), os.listdir(path)))
file_list_xgb = list(filter(lambda x: x.startswith('XGB'), file_list))
file_list_linear = list(filter(lambda x: x.startswith('Linear'), file_list))
file_list_nn = list(filter(lambda x: x.startswith('NN'), file_list))
file_list_hxlinear = list(filter(lambda x: x.endswith('.pkl'), os.listdir('/data/user/015836/HFmodel/share/20210112/')))
file_list_xgb_rolling = list(filter(lambda x: x.startswith('XGBFactorEvalRollingBest'), file_list))
para = {
    'XGB_lightGBM_CatBoost': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    f'XGB_lightGBM_subjectiveExtra_CatBoost':
    ['/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/wyl/subjective/model_record/extratree/k10/ic_all_t_best.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
],

f'XGB_subjectiveExtra_CatBoost':
    ['/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/subjective/model_record/extratree/k10/ic_all_t_best.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
],
f'XGB_lightGBM_subjectiveExtra':
    [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/wyl/subjective/model_record/extratree/k10/ic_all_t_best.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
],
    'ExtraSubjective':['/data/group/800319/wyl/subjective/model_record/extratree/k10/ic_all_t_best.pkl'],
    'lightGBM':[ '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'CatBoost':['/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl']
}

for each in 'ftest_list1,feature_importance,feature_importance1,ftest_method,multual_info_method,var_list1,var_method'.split(','):
    cat_path = f'/data/group/800319/wyl/model_record/catboosts/catboostnew2_{each}.pkl'
    para[f'XGB_lightGBM_{each}_CatBoost'] = [
        cat_path,
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ]

def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash,pool_num, deal_ratio, tag,alpha_pool_tag):
    file_list = para[tag]
    print(file_list)
    for each in file_list:
        if not os.path.exists(each):
            out_signal(each.replace('.pkl','/'),20181231)
    start = 20160101
    end = 20181231
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

    alpha_pool = pd.read_pickle(f'/data/group/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num
    # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
    original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    tag = tag.replace('RevTriggerFilterHolding', f'{alpha_pool_tag}Top{pool_num}_real{pool_num}')

    if not os.path.exists(
            f'{base_path}/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
        instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        order_info = instance.order_info
        pd.to_pickle([record, cash_series, holding_num],
                     f'{base_path}/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
    else:
        record, cash_series, holding_num = pd.read_pickle(f'{base_path}/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    #
    out_path = f'{base_path}%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'],out_path)

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/CatBoostCompare/'
if not os.path.exists(base_path):
    os.mkdir(base_path)
if not os.path.exists(f'{base_path}/record/'):
    os.mkdir(f'{base_path}/record/')
pool_dict={
'old':'daily_stock_score_v3_20210127.pkl',
 'condition_mv':'CS_OLS_condition_mv_F400T488P1_future925t241h123d_uniform20t50.pkl',
 'rank_ex20':'CS_OLS_condition_style_rank_ex20_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'NoCondition':'CS_OLS_no_condition_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_OLS':'CS_OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl'
}

# tag_tag = ['XGB_lightGBM_CatBoost', 'XGB_lightGBM_ftest_list1_CatBoost', 'XGB_lightGBM_feature_importance_CatBoost', 'XGB_lightGBM_feature_importance1_CatBoost', 'XGB_lightGBM_ftest_method_CatBoost', 'XGB_lightGBM_multual_info_method_CatBoost', 'XGB_lightGBM_var_list1_CatBoost', 'XGB_lightGBM_var_method_CatBoost']
tag_tag = ['XGB_lightGBM_subjectiveExtra_CatBoost','ExtraSubjective','lightGBM','CatBoost','XGB_lightGBM_subjectiveExtra',f'XGB_subjectiveExtra_CatBoost']

# pool_tag = 'old'
each = (0.05,0.005,2e8,600)

from xquant.compute.aimr import AIMR
i = int(AIMR.getParam())
calc_back_test_record(*(each + (0.1, tag_tag[i],'old')))

