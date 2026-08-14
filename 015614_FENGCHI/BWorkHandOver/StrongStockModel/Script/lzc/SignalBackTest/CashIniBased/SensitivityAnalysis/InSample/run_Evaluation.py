# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os

def get_signal_by_zscore_integration(path_file_list,threshold=0.05):
    res_list = {}
    for each in path_file_list:
        temp = pd.read_pickle(each)
        res_list[each] = temp['adjusted_prediction']
    res_df = pd.DataFrame(res_list)
    pred_ret = res_df.mean(axis=1)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.pivot_table(index=[pred_ret.columns[0],pred_ret.columns[1]],columns=pred_ret.columns[2],values=0)
    return pred_ret>threshold, pred_ret


bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100

path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/'
file_list = list(filter(lambda x : not x.endswith('_zscore.pkl') and x.endswith('.pkl'),os.listdir(path)))
file_list_xgb = list(filter(lambda x : x.startswith('XGB'),file_list))
file_list_linear = list(filter(lambda x : x.startswith('Linear'),file_list))
file_list_nn = list(filter(lambda x : x.startswith('NN'),file_list))
file_list_hxlinear = list(filter(lambda x : x.endswith('.pkl'),os.listdir( '/data/user/015836/HFmodel/share/20210112/')))
file_list_xgb_rolling = list(filter(lambda x : x.startswith('XGBFactorEvalRollingBest'),file_list))

def calc(*arg):
    print(arg)
    record,cash_series,holding_num = pd.read_pickle(recor_file%arg)
    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
    #
    # out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    for each in record:
        helper.record[each]=record[each]
    # helper.evaluat_signal_by_stk(2260)
    helper.one_wave_run(record,cash_series,48,output_path=out_file%arg ,signal_record_save=True,holding_num=holding_num)
    # print(out_path)



import itertools,time
from xquant.compute.aimr import AIMR

recor_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record/record_XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.pkl'
out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
# para_list = list(itertools.product([0.005, 0.007, 0.009, 0.01, 0.02, 0.025, 0.05],[0.03, 0.04, 0.05, 0.06], [4e8, 6e8, 8e8, 1e9]))
# para_list = list(itertools.product([0.005, 0.007, 0.009, 0.01, 0.02, 0.025, 0.05],[0.03, 0.04, 0.05, 0.06], [2e8]))
para_list = list(itertools.product([0.005, 0.01, 0.02],[0.04, 0.05, 0.06], [2e8],[200,400]))
para_list = [(x[-1],x[-1])+x[:-1] for x in para_list]


left = sorted(list(filter(lambda x: os.path.exists(recor_file%(x)) and not os.path.exists(out_file%x),para_list)))
i = int(AIMR.getParam())
total = 7
while left:
    calc(*sorted(left)[i*len(left)//total])
    left = sorted(list(filter(lambda x: os.path.exists(recor_file % (x)) and not os.path.exists(out_file % x), para_list)))





