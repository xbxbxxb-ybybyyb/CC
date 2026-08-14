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
    'XGB_DTC': [path + x for x in file_list_xgb],
    'Linear_DTC': [path + x for x in file_list_linear],
    'NN_DTC': [path + x for x in file_list_nn],
    'XGB_Linear_DTC': [path + x for x in file_list_linear + file_list_xgb],
    'XGB_Linear_NN_DTC': [path + x for x in file_list_xgb + file_list_linear + file_list_nn],
    'LinearHXV2_T': ['/data/user/015836/HFmodel/share/20210112/LinearV2T.pkl'],
    'LinearHXV2_D': ['/data/user/015836/HFmodel/share/20210112/LinearV2D.pkl'],
    'LinearHXV2_C': ['/data/user/015836/HFmodel/share/20210112/LinearV2C.pkl'],
    'XGB_LinearHXV2_DTC': ['/data/user/015836/HFmodel/share/20210112/' + x for x in file_list_hxlinear] + [path + x for x in file_list_xgb],
    'XGBRollingBest_DTC': [path + x for x in file_list_xgb_rolling],
    'NNF101': ['/data/user/015836/HFmodel/share/20210113/NNF101.pkl'],
    'LSTM0115': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LSTM_union_train200_test10_factor_num100_norm_window_40.pkl'],
    'LSTM0115_NNF101': ['/data/user/015836/HFmodel/share/20210113/NNF101.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LSTM_union_train200_test10_factor_num100_norm_window_40.pkl'],
    'XGB_0115_DTC': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_0116_DT': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210116/part/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210116/part/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_T_Robust': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl'
                     ],
    'Catboost0': ['/data/group/800319/wyl/model_record/catboost0.pkl'],
    'Catboost0_XGB': ['/data/group/800319/wyl/model_record/catboost0.pkl'] + [path + x for x in file_list_xgb],
    'HX20210120DTC': [
        '/data/user/015836/HFmodel/share/20210120/T400.pkl',
        '/data/user/015836/HFmodel/share/20210120/D400.pkl',
        '/data/user/015836/HFmodel/share/20210120/C400.pkl',
    ],
    'XGBForApp': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'HX20210119F101': ['/data/user/015836/HFmodel/share/20210119/F101.pkl'],
    'XGB_dct': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train200_test10_factor_num400_norm_window_40.pkl'],
    'C3': ['/data/user/015836/HFmodel/share/20210120/C3.pkl'],
    'XGB399_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HalfYealy_NewPara10_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],

    'XGB_Cat_Light': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_Light': [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ]

}
per_amt_ratio = 0.005
tag = 'XGB_Cat_Light'
# file_list = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoading5minFix_union_train200_test10_factor_num100_norm_window_40.pkl']
# ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoadingFilterLimit_union_train200_test10_factor_num100_norm_window_40.pkl']
file_list = para[tag]
print(file_list)
# file_list = [path + x for x in file_list]
deal_ratio = 0.1
tag = tag + '_OnlineTest'
start = 20190102
end = 20201231

for pct_threshold in [0.03,0.05,0.04,0.06]:
    # signal,pred_ret = get_signal_by_zscore_integration(file_list,threshold=pct_threshold)
    if not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s.pkl' % tag):
        signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, start, 'actual_label', 'new',
                                                                       tail=54)
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold))
    else:
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold))

# # pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
# tag = tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
# pred_ret[~signal] = np.nan
#
# # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[start:end].rank(ascending=False,axis=1)<600
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/stock_pool/stock_pool_20210426.pkl').shift(1).loc[start:end].rank(ascending=False,axis=1)<600
#
# # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
# original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
# original_pool = original_pool.drop(alpha_pool.index,axis=0)
# alpha_pool = pd.concat([original_pool,alpha_pool]).sort_index()>0.5
# tag = tag.replace('RevTriggerFilterHolding','AlphaTriggerPoolV3Top600_real600')
#
# # res3 = get_daily_active_stock(20181228,20201031).shift(1)
# # tag = tag.replace('OutSampleRevTriggerFilterHolding','OutSampleRevTriggerFilterHolding_Concept')
# instance = StartWithLimitCashVolConsider(pred_ret, start,end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
#                                          per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
#                                          deal_percent=deal_ratio)#, initial_cash=20000000)
# record = instance.run_backtest()
# cash_series = instance.cash_series
#
# # pd.to_pickle([record, cash_series], '/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoResShift/record/%sOutSample_0105_0127OnlineLimit.pkl' % tag)
#
# # pd.to_pickle([record,cash_series],'/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
# # record,cash_series = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB20201217_eval_record.pkk')
# helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
# cash_series.index = cash_series.index.astype(int).astype(str)
# out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/PoolNumCompare/%s_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
# helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True,holding_num=instance.holding_num)
#
# print(out_path)
