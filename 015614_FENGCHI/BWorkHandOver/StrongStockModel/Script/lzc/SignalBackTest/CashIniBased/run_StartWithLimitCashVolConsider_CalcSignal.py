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
para={
     'XGB_DTC':[path + x for x in file_list_xgb],
     'Linear_DTC':[path + x for x in file_list_linear],
    'NN_DTC':[path + x for x in file_list_nn],
     'XGB_Linear_DTC':[path + x for x in file_list_linear+file_list_xgb],
    'XGB_Linear_NN_DTC':[path + x for x in file_list_xgb+file_list_linear+file_list_nn],
    'LinearHXV2_T':[ '/data/user/015836/HFmodel/share/20210112/LinearV2T.pkl'],
    'LinearHXV2_D':[ '/data/user/015836/HFmodel/share/20210112/LinearV2D.pkl'],
    'LinearHXV2_C':[ '/data/user/015836/HFmodel/share/20210112/LinearV2C.pkl'],
    'XGB_LinearHXV2_DTC':[ '/data/user/015836/HFmodel/share/20210112/'+x for x in file_list_hxlinear]+[path + x for x in file_list_xgb],
    'XGBRollingBest_DTC':[path + x for x in file_list_xgb_rolling],
    'NNF101':['/data/user/015836/HFmodel/share/20210113/NNF101.pkl'],
    'LSTM0115':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LSTM_union_train200_test10_factor_num100_norm_window_40.pkl'],
    'LSTM0115_NNF101':['/data/user/015836/HFmodel/share/20210113/NNF101.pkl',
                '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LSTM_union_train200_test10_factor_num100_norm_window_40.pkl'],
    'XGB_0115_DTC':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_0116_DT':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210116/part/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210116/part/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_T_Robust':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl'
],
    'Catboost0':[ '/data/group/800319/wyl/model_record/catboost0.pkl'],
    'Catboost0_XGB':[ '/data/group/800319/wyl/model_record/catboost0.pkl']+[path + x for x in file_list_xgb],
    'HX20210120DTC':[
        '/data/user/015836/HFmodel/share/20210120/T400.pkl',
        '/data/user/015836/HFmodel/share/20210120/D400.pkl',
        '/data/user/015836/HFmodel/share/20210120/C400.pkl',
                  ],
    'XGBForApp':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210119/for_app_test/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'HX20210119F101':['/data/user/015836/HFmodel/share/20210119/F101.pkl'],
'HX20210120F101':['/data/user/015836/HFmodel/share/20210120/F101.pkl'],
    'XGB_dct':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train200_test10_factor_num400_norm_window_40.pkl'],
'XGB_Linear_NN_dct':[
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/NNCorrStdAllPeriod_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/lr_train200_test10_factor_num400_norm_window_40.pkl',
                     ],
    'XGB_dtc_Robust':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210120/XGBFactorEval_ic_all_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'C3':['/data/user/015836/HFmodel/share/20210120/C3.pkl'],
        'XGB399_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
],
    'XGB_Linear_DTC399':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'HX20210121_DTC': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
    ],
    'Linear_DTC399':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
'Linear_Roubust_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl'
],
'HX20210121_dtc':['/data/user/015836/HFmodel/share/20210121/DTC400.pkl'],
    'XGBRobust399':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],
'XGBRobust399_LinearHX':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/user/015836/HFmodel/share/20210121/DTC400.pkl'
    ],
    'XGBRobust_dtc14_20':
        ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGBHalfYearly_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
],
    'XGBHalfYearly_dtc_ind':[
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'
    ],
    'WYLCatBosst':['/data/group/800319/wyl/model_record/catboostnew0.pkl'],
    'XGB_HalfYearly_HX0121_DTC':[
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HalfYearly_HX0121_dtc_ind':[
'/data/user/015836/HFmodel/share/20210121/DTC400.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_hALFyEARLY_dtcDTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'

    ],
    'XGB_HalfYealy_NewPara10_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HalfYealy_NewPara10_With_CatBoost_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew1.pkl'
    ],
    'XGB_HX_WYL':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew1.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_HalfYearly_D':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_HalfYearly_T':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_HalfYearly_C':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'CatBoost_T':['/data/group/800319/wyl/model_record/catboostnew1.pkl'],
    'XGB_WYL_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
    ],
'XGB_HX_WYL_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
'WYL_DTC':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
],
    'XGBConceptTraining':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'lightGBM':['/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'XGB_lightGBM':[
    '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_lightGBM_CatBoost':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
'XGB_lightGBM_CatBoost_T':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ]
}
pct_threshold = 0.05
per_amt_ratio = 0.005
tag ='XGB_lightGBM_CatBoost'
# file_list = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoading5minFix_union_train200_test10_factor_num100_norm_window_40.pkl']
    #['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoadingFilterLimit_union_train200_test10_factor_num100_norm_window_40.pkl']
file_list = para[tag]
print(file_list)
# file_list = [path + x for x in file_list]
deal_ratio = 0.1
tag = tag+'_OnlineTest'

for pct_threshold in [0.04,0.03,0.02]:
# signal,pred_ret = get_signal_by_zscore_integration(file_list,threshold=pct_threshold)
    if not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl'%(tag,pct_threshold)):
        signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold,[x.replace('.pkl','_val_pred/') for x in file_list],file_list,20160104,'actual_label','new',head=73)
        pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl'%(tag,pct_threshold))
    # pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
