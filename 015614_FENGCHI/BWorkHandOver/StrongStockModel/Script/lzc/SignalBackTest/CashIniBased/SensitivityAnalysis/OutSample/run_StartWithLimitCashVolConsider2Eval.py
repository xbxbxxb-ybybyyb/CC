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

def calc(*arg):
    if os.path.exists(out_file%arg):
        print(arg,'exist')
        return
    print(arg)
    record,cash_series,holding_num = pd.read_pickle(recor_file%arg)
    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
    #
    # out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    helper.one_wave_run(record,cash_series,48,output_path=out_file%arg ,signal_record_save=True,holding_num=holding_num)
    # print(out_path)

pct_threshold_list = [0.03,0.04,0.05,0.06]
per_amt_ratio_list = [0.003,0.004,0.005,0.007,0.009,0.01,0.02,0.025,0.05]

import itertools,time
from xquant.compute.aimr import AIMR
recor_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record_out_sample/record_XGB_Cat_Light_OnlineTestOutSampleAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%d.pkl'
out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityOutSample/XGB_lightGBM_CatBoostOutSampleAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%d.xlsx'
para_list = list(itertools.product([0.005, 0.01, 0.02],[0.04, 0.05, 0.06],[1e8],[200,600,400]))
para_list = [(x[-1],x[-1])+x[:-1] for x in para_list]



i = int(AIMR.getParam())
total = 9
length = len(para_list)
for p in para_list[length*i//total:length*(i+1)//total]:
    calc(*p)




