# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
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


bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
para = {

    'XGBMonthlyV4_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
],
    'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

        'Cat':['/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'],
        'Light':[ '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
       'XGB_Mtrix_D':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl'],
       'XGB_Mtrix_T':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl'],
       'XGB_Mtrix_C':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl'],
       'XGB_D':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl'],
       'XGB_T':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl'],
       'XGB_C':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl'],

}



def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag):
    file_list = para[tag]
    print(file_list)
    start = 20210104
    end = 20211130
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    tag = tag + 'WithoutMax5'  # +'WithMax5threshold' #
    tag = tag + f'start{start}_end{end}'
    # /data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_XGB_DCMultiFreq_T_Light_CatWithMax5threshold_0.05.pkl
    if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)):

        print(pct_threshold, 'signal exist')
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
        print('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
    else:
        for each in file_list:
            if os.path.exists(each):
                check = pd.read_pickle(each)
                if check.index[-1][0]>=end:
                    continue
            print('reintegrate')
            out_signal(each.replace('.pkl', '/'))
        # signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, 20160104, 'actual_label',
        #                                                                'new',
        #                                                                head=135)
        signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, start,
                                                                                      'actual_label',
                                                                                      'new',
                                                                                      head=None, end=end)
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))

    # pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
    tag = tag + 'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))
    pred_ret[~signal.fillna(False)] = np.nan
    if pool_dict[alpha_pool_tag] is None:
        alpha_pool = pd.DataFrame()
    elif isinstance(pool_dict[alpha_pool_tag], pd.DataFrame):
        alpha_pool = pool_dict[alpha_pool_tag].shift(1).loc[start:end]
    elif isinstance(pool_dict[alpha_pool_tag], str):
        alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num
    else:
        raise Exception('Wrong type')
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
    from online_conf import code_list_path
    from dataApi.getData import trans_windcode2int
    code_file_list = list(filter(lambda x: x.endswith('.pkl') and len(x) == 12, os.listdir(code_list_path)))
    online_pool = {}
    for each in code_file_list:
        temp = pd.read_pickle(f'{code_list_path}{each}')
        date = int(each[:-4])
        temp = pd.Series(True, index=temp)
        online_pool[date] = temp

    online_pool = pd.DataFrame(online_pool).T.fillna(False)
    online_pool.columns = online_pool.columns.map(trans_windcode2int)
    online_pool = online_pool.sort_index().shift(1).loc[20210406:]

    alpha_pool = alpha_pool.drop(list(set(alpha_pool.index).intersection(set(online_pool.index))),axis=0)
    alpha_pool = pd.concat([alpha_pool,online_pool],axis=0).fillna(False)

    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(list(set(alpha_pool.index).intersection(set(original_pool.index))), axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    tag = tag.replace('RevTriggerFilterHolding', f'{alpha_pool_tag}Top{pool_num}_real{pool_num}')
    tag = tag+f'start{start}_end{end}'
    print('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    if not os.path.exists(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
        instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        order_info = instance.order_info
        # pd.to_pickle([record, cash_series, holding_num],
        #              '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
    else:
        raise Exception('Exist')
        record, cash_series, holding_num = pd.read_pickle(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    #
    # out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/PoolCompare20210519/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Upgrade2021/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
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
    'stock_pool_20210610': 'stock_pool_20210610.pkl',
    'Open_Board': get_basic_values('Open_Board_stock')
}

# pool_dict['SelectedStrong'] = pd.read_pickle('/data/group/800442/800319/Faamonitor/zhaban_syx_zt_time_10_20210511.pkl')
# pool_dict['SelectedStrong'].index = pool_dict['SelectedStrong'].index.map(int)
# pool_dict['AllMkt'] = None
# pool_dict['Replace300'] = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50_Replace300.pkl')
# pool_dict['PreDayReplace300'] = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50_PreDayReplace300.pkl')
# # pool_tag = 'old'

from xquant.compute.aimr import AIMR
tag = 'XGBMonthlyV4_Cat_Light_Val'#AIMR.getParam()
#tag = 'Cat'
each = (0.05, 0.005, 2e8, 600)
calc_back_test_record(*(each + (0.1, tag, 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light', 'PreDayReplace300')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light', 'Replace300')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBFix5MinFreqDelta_DTC_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBFix5MinFreqDeltaHandy_DTC_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_New', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyCrossFixReselect_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyCrossFixOriginFactor_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_DT_TC_DTC', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_DT', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_DTC', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_TC', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Light_DT_TC_DTC', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_DT_NoEarly', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4With5minAfterDelta_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithCrossFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4OnlyCrossFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4OnlyCrossFixMIXReselect_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4CrossFixMIXReselect_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4MIX20210908_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat3_Light3', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_Fix5min20210909', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat200_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithCrossFactorReplace_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithCrossFactorAppend_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4OnlySWCorrFixFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithSWCorrFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4OnlySWMeanFixFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Origin_SWMean_SWCorr_SWCross_FixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_SWMean_SWCorr_SWCross_FixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_SWMean_SWCorr_FixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Origin_SWMean_SWCorr_FixMIX_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthly_Val20', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithCrossFactorReplace1027_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4WithCrossFactorAppend1027_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBMonthlyV4_Cat_Light_Val', 'old')))
# calc_back_test_record(*(each + (0.1, 'XGB_lightGBM_CatBoost', 'old')))




