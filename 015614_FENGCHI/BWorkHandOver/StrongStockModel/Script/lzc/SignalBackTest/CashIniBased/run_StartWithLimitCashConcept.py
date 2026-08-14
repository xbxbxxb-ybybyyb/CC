# @Time : 2020/12/21 17:19
# @Author : Zhichen Lu
# @File : run_StartWithLimitCashConcept.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashConcept import StartWithLimitCashConcept,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.ConceptApi import get_basic_values,get_concept_values
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock

# res1 = get_active_stock_1concept(concept='884702.WI', start_date=20200401, end_date=20201201)
# res2 = get_daily_active_concept(20200501, 20201201)


pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
max_barly_trigger = 100

file_list_xgb = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']
# Linear
file_list_linear = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl']
# NN
file_list_nn = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStd_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']

# (pct, subset_path_list, signal_file_name_list, start,val_tag=0,loading_type=None)
para={
     'XGB_DTC':file_list_xgb,
     'Linear_DTC':file_list_linear,
     'XGB_Linear_DTC':file_list_linear+file_list_xgb
}
tag = 'XGB_DTC_Concept'
# file_list = para[tag]

# signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,0,'old')
# pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Linear_DTC20201221.pkl')
signal,pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_DTC20201217.pkl')
pred_ret[~signal] = np.nan
res3 = get_daily_active_stock(20200701, 20200731)

instance = StartWithLimitCashConcept(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost, barly_max_buy=max_barly_trigger,concept=res3)
record = instance.run_backtest()
cash_series = instance.cash_series

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/%sConcept_UpBuy%d_%dbp_cost.xlsx' % (tag,
     max_barly_trigger, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True)

# print(out_path)
"""
active_concept = get_basic_values('Active_Concept')#.shift(1).reindex(sorted(pred_ret.index.levels[0].tolist()), axis=0).reindex(pred_ret.columns.tolist(), axis=1)
active_concept = active_concept.loc[20160104:20201220].T
active_concept_dict = {}
for date in active_concept.columns:
    temp_concept = active_concept[date]
    temp_concept = temp_concept[temp_concept]
    active_concept_dict[date] =  temp_concept.index.tolist()

active_concept_pool = {}
for date in active_concept_dict:
    pool = []
    for concept in active_concept_dict[date]:
        concept_stock = get_concept_values('Concept_StockList',concept=concept,start_date=date,end_date=date).T[date]
        concept_stock = concept_stock[concept_stock].index.tolist()
        pool = pool + concept_stock
    active_concept_pool[date] = pool
    print(date)
"""


