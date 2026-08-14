# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderPredConsiderV6_1 import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
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

}


def param_print():
    def wraper(func):
        def wrpaer_func(*args,**kwd):
            print(args,kwd)
            res = func(*args,**kwd)
            return res
        return wrpaer_func
    return wraper

@param_print()
def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag,down_signal_ratio,signal_threshold):
    file_list = para[tag]
    print(file_list)
    start = 20170101
    end = 20210531
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    tag = tag + 'WithoutMax5'  # +'WithMax5threshold' #
    # /data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_XGB_DCMultiFreq_T_Light_CatWithMax5threshold_0.05.pkl
    signal_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)
    tag = f'{tag}_deal{deal_ratio:.2f}_per{per_amt_ratio * 1000}bp_thre{int(pct_threshold * 100)}_cash{initial_cash:.0e}_Top{p_num}_start{start}_end{end}_' \
        f's_thre{signal_threshold:.2f}_d_thre{down_signal_ratio:.3f}'
    out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/PredConsiderV6_1PoolPerSigPrameterSeeking/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    return out_path

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

para_list = ['XGBEarly_DE_ZSCORE0', 'XGBEarly_DE_ZSCORE0_5', 'XGBEarly_DE_ZSCORE1', 'XGBEarly_DE_ZSCORE1_2', 'XGBEarly_DE_ZSCORE1_3', 'XGBEarly_DE_ZSCORE2', 'XGBEarly_DE_ZSCORE3',
             'XGBEarly_DE_ZSCORE4', 'XGBEarly_DE_ZSCORE5']

if __name__ == '__main__':

    import itertools
    # para_list = [(-1,1)]+list(itertools.product([round(x*0.001,3) for x in range(-20,21,4)], [0.4,0.5,0.6,0.7,0.8,0.9,1]))
    # para_list = [(-1,1)]+list(itertools.product([round(x*0.001,3) for x in range(-20,21,4)], [0.05,0.1,0.15,0.2,0.25,0.3,0.35]))
    from xquant.compute.aimr import AIMR
    d_threshold,s_threshold = (0,0.2)#eval(AIMR.getParam())#(0.2,1)
    para_list = list(itertools.product([0.005, 0.01, 0.015, 0.2], [200, 400, 600]))
    # per_sig_ratio, p_num = para_list[0]#eval(AIMR.getParam())
    import datetime
    now = datetime.datetime.now()

    out_list = []
    for per_sig_ratio, p_num in para_list:
        o_path = calc_back_test_record(0.05, per_sig_ratio, 2e8, p_num, 0.1, 'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20',
                          down_signal_ratio=d_threshold,signal_threshold=s_threshold)
        out_list.append(o_path)

    for each in set(out_list):
        os.remove(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/PredConsiderV6_1PoolPerSigPrameterSeeking/{each}')
    # calc_back_test_record(0.05, 0.005, 2e8, 600, 0.1, 'XGBMonthlyV4_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20',
    #                       down_signal_ratio=d_threshold, signal_threshold=s_ratio,swing_threshold=sw_thre)





