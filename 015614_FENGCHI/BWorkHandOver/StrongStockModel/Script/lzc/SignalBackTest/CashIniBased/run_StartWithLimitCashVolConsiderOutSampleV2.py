# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderV2 import StartWithLimitCashVolConsiderV2,InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100

file_list_xgb = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']
# Linear
file_list_linear = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl']
# NN
file_list_nn = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/NNCorrStd_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/NNCorrStdGPU_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
            '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOutSample/NNCorrStdGPU_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']

para={
     'XGB_DTC':file_list_xgb,
     'Linear_DTC':file_list_linear,
     'XGB_Linear_DTC':file_list_linear+file_list_xgb
}
per_amt_ratio = 0.005
tag = 'XGB_Linear_DTC'
file_list = para[tag]
tag = tag+'_OutSampleConcept'
deal_ratio = 0.1
tag = tag+'_deal_ratio_%.1f_per_ratio_%.4f'%(deal_ratio,per_amt_ratio)
print(tag)

# signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,0,'old')
# pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_LSTMPara25SortList_union100.pkl')



signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Linear_DTC_out_of_sample.pkl')
pred_ret[~signal] = np.nan
res3 = get_daily_active_stock(20191231, 20201031).shift(1)
instance = StartWithLimitCashVolConsiderV2(pred_ret, 20200101,20201031,stock_pool=res3,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_20190102_20201030.pkl'},
                                         deal_percent=deal_ratio)
record = instance.run_backtest()
cash_series = instance.cash_series


pd.to_pickle(record,'/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderV2/record/%sOutSample.pkl'%tag)

# pd.to_pickle([record,cash_series],'/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
# record,cash_series = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderV2/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True)

print(out_path)
