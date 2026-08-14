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
    'HX20210120F101': ['/data/user/015836/HFmodel/share/20210120/F101.pkl'],
    'XGB_dct': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_Linear_NN_dct': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/NNCorrStdAllPeriod_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/lr_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_dtc_Robust': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobust20210120/XGBFactorEval_ic_all_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'C3': ['/data/user/015836/HFmodel/share/20210120/C3.pkl'],
    'XGB399_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_Linear_DTC399': [
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
    'Linear_DTC399': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'Linear_Roubust_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollNoFuture20210120/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl'
    ],
    'HX20210121_dtc': ['/data/user/015836/HFmodel/share/20210121/DTC400.pkl'],
    'XGBRobust399': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGBRobust399_LinearHX': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/user/015836/HFmodel/share/20210121/DTC400.pkl'
    ],
    'XGBRobust_dtc14_20':
        ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGBHalfYearly_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGBHalfYearly_dtc_ind': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'
    ],
    'WYLCatBosst': ['/data/group/800319/wyl/model_record/catboostnew0.pkl'],
    'XGB_HalfYearly_HX0121_DTC': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HalfYearly_HX0121_dtc_ind': [
        '/data/user/015836/HFmodel/share/20210121/DTC400.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_hALFyEARLY_dtcDTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'

    ],
    'XGB_HalfYealy_NewPara10_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HalfYealy_NewPara10_With_CatBoost_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/catboostnew1.pkl'
    ],
    'XGB_HX_WYL': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/catboostnew1.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_HalfYearly_D': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_HalfYearly_T': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_HalfYearly_C': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'CatBoost_T': ['/data/group/800319/wyl/model_record/catboostnew1.pkl'],
    'XGB_WYL_DTC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
    ],
    'XGB_HX_WYL_DTC': [
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
    'WYL_DTC': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
    ],
    'XGBConceptTraining': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10Concept_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'lightGBM': ['/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'XGB_lightGBM': [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_lightGBM_CatBoost': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_lightGBM_CatBoost_T': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HX_ZSCORE': [
        '/data/user/015836/HFmodel/share/20210121/D400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400_zscore.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_zscore.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40_zscore.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40_zscore.pkl',

    ],
    'XGB_lightGBM_CatBoost_Random_Extra': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/randomforestnew_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/extratreenew2_ic_all_t.pkl',
    ],
    'XGB_Extra_info_LightGBM': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_t_train200_test10_factor_num600_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'LigtGBMOnly': [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'
    ],
    'LigtGBMOnly_DTC': [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_d.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_c.pkl',
    ],
    'XGB_Only': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_dtc_single': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'],
    'XGB_dtc_No_NNExtractor': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_Light_DTCNN': [
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'

    ],
    'XGB_gain': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'],
    'XGB_weight': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl'],
    'XGB_cover': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_gwc': ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
                '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
                '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_light_Cat_DTC_GWC': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_DTC_GWC': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_HX_DTC': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_HX_DTC_Cat_Light': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
}


def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash,pool_num, deal_ratio, tag):
    file_list = para[tag]
    print(file_list)
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

    alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False, axis=1) < pool_num
    # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
    original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    tag = tag.replace('RevTriggerFilterHolding', f'AlphaTriggerPoolV3Top{pool_num}_real{pool_num}')
    print('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    if not os.path.exists(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
        instance = StartWithLimitCashVolConsider(pred_ret, 20160101, 20181231, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        order_info = instance.order_info
        pd.to_pickle([record, cash_series, holding_num],
                     '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
    else:

        print(tag,'exist')


# pct_threshold = 0.05
# per_amt_ratio = 0.005
# initial_cash = 2e8
from xquant.compute.aimr import AIMR
import itertools, gc

# para_list = list(itertools.product([0.03, 0.04, 0.05, 0.06], [0.005, 0.007, 0.009, 0.01, 0.02, 0.025, 0.05], [2e8],[200,400]))
para_list = list(itertools.product([0.04, 0.05, 0.06], [0.005, 0.01, 0.02], [1e8],[200,600,400]))
len(para_list)
total = 9
i = 0#int(AIMR.getParam())
# pct_threshold,per_amt_ratio,initial_cash = para_list[i]
for each in para_list[len(para_list) * i // total:len(para_list) * (i + 1) // total]:
    calc_back_test_record(*(each + (0.1, 'XGB_lightGBM_CatBoost')))
    gc.collect()
# each = (0.05,0.005,2e8,600)
# calc_back_test_record(*(each + (0.1, 'XGB_lightGBM_CatBoost')))