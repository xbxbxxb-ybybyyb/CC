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

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100



path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/'
file_list = list(filter(lambda x : not x.endswith('_zscore.pkl') and x.endswith('.pkl'),os.listdir(path)))
file_list_xgb = list(filter(lambda x : x.startswith('XGB'),file_list))
file_list_linear = list(filter(lambda x : x.startswith('Linear'),file_list))
file_list_nn = list(filter(lambda x : x.startswith('NN'),file_list))

para={
     'XGB_DTC':file_list_xgb,
     'Linear_DTC':file_list_linear,
    'NN_DTC':file_list_nn,
     'XGB_Linear_DTC':file_list_linear+file_list_xgb,
    'XGB_Linear_NN_DTC':file_list_xgb+file_list_linear+file_list_nn
}
per_amt_ratio = 0.005
tag = 'XGB_DTC'
# file_list = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoading5minFix_union_train200_test10_factor_num100_norm_window_40.pkl']
    #['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoadingFilterLimit_union_train200_test10_factor_num100_norm_window_40.pkl']
file_list = para[tag]
file_list = [path + x for x in file_list]
deal_ratio = 0.1
tag = tag+'_OnlineTest'


# signal,pred_ret = get_signal_by_zscore_integration(file_list,threshold=pct_threshold)
signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,'actual_label','new')
# pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s.pkl'%tag)
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s.pkl'%tag)
tag = tag+'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f'%(deal_ratio,per_amt_ratio)
pred_ret[~signal] = np.nan
# res3 = get_daily_active_stock(20151231, 20181231).shift(1)
instance = StartWithLimitCashVolConsider(pred_ret, 20160101, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_20160104_20181228.pkl'},
                                         deal_percent=deal_ratio)
record = instance.run_backtest()
# pd.to_pickle(record,'/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderOnlineTest/record/%sInSample.pkl'%tag)

cash_series = instance.cash_series
# pd.to_pickle([record,cash_series],'/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
# record,cash_series = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderOnlineTest/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True)

print(out_path)


val_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40_val_pred/'
os.listdir(val_path)
check = pd.read_pickle(val_path+'20170719.pkl')