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
from dataApi.sendInfo import send_file
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

para={
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
    ],
'XGB_HX_ZSCORE':[
        '/data/user/015836/HFmodel/share/20210121/D400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400_zscore.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_zscore.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40_zscore.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40_zscore.pkl',

    ],
    'XGB_lightGBM_CatBoost_Random_Extra':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/randomforestnew_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/extratreenew2_ic_all_t.pkl',
    ],
    'XGB_Extra_info_LightGBM':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_t_train200_test10_factor_num600_norm_window_40.pkl',
                      '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
                      '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
                      '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
                      ],
    'LigtGBMOnly':[
'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'
    ],
'LigtGBMOnly_DTC':[
'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_d.pkl',
'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_c.pkl',
    ],
    'XGB_Only':[
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_dtc_single':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'],
    'XGB_dtc_No_NNExtractor':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_Light_DTCNN':[
'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'

    ],
    'XGB_HX_DTC':[
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
'XGB_HX_DTC_Cat_Light':[
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
'ALL_Integration':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_Cat_Light.pkl'],

'XGB_gain':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'],
    'XGB_weight':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl'],
    'XGB_cover':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_gwc':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
               '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
               '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'],
    'XGB_light_Cat_DTC_GWC':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'],
    'XGB_DTC_GWC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'
    ],
    'HX_DTC': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
    ],
 'XGB_DTC_GWC_HX_DTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/user/015836/HFmodel/share/20210121/D400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400_zscore.pkl',
    ],
    'Cat_Light_HX':[
        '/data/user/015836/HFmodel/share/20210121/D400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400_zscore.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
    'XGB_DTC_GWC_oldDTC':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustNoFuture20210121/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],
'AllIntegrationWithoutLightCatByTree':[ '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_ByTree.pkl'],
    'CatBoost_DTC':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_c.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_d.pkl',
    ],
'RegIntegrationNoLightCat':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_RegIntegration.pkl'],
    'XGB_RF':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/GBDTOnly_train400_test10_factornum400_eval_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
              ],
    'AllIntegrationTestSet':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_RegIntegrationOnlyTest.pkl'],
    'AllIntegrationTestSetNoMaxLimit':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_RegIntegrationOnlyTest.pkl'],
    'AllIntegrationTestSetTree':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_TreeIntegrationOnlyTest.pkl'],
    'XGB_DTC_NNEXtractor':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
    ],
    'XGB_DTC_dtc_NNEXtractor':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl',
    ],
    'XGB_DTC_and_XGB_DTC_NNExtractor_Cat_Liaght':{
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    },
'XGB_DTC_and_XGB_DTC_NNExtractor':{
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    },
'XGB_DTC_and_XGB_DTMultiFreq':{
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
    },

'XGB_DTC_and_XGB_DTMultiFreq_Ligt_Cat':[
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_d_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_c_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
],
    'XGB_DTMultiFreq':['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',],

'XGB_DCMultiFreq_T':{
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
    },
'XGB_DCMultiFreq_T_Light_Cat':{
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    },
    'XGB_LongValidation': [
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10LongValidation_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10LongValidation_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10LongValidation_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],

'XGB_DC':[
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        # '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
'XGB_DTC_DoubleEnsembleBaseline':[
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBFactorEvalYearlyBaseline_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBFactorEvalYearlyBaseline_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBFactorEvalYearlyBaseline_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
],
'XGB_DE0':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_0/round_0.pkl',
               ],
    'XGB_DE1':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_1/round_1.pkl',
               ],
    'XGB_DE2':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_2/round_2.pkl',
               ],
    'XGB_DE3':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_3/round_3.pkl',
               ],    'XGB_DE4':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_4/round_4.pkl',
               ],    'XGB_DE5':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_5/round_5.pkl',
               ],
    'XGB_DE0_5':[f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsemble_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)],


    'XGBEarly_DE0':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_0/round_0.pkl',
               ],
    'XGBEarly_DE1':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_1/round_1.pkl',
               ],
    'XGBEarly_DE2':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_2/round_2.pkl',
               ],
    'XGBEarly_DE3':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_3/round_3.pkl',
               ],    'XGBEarly_DE4':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_4/round_4.pkl',
               ],    'XGBEarly_DE5':[
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_5/round_5.pkl',
               ],
    'XGBEarly_DE0_5':[f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(6)],

'XGBEarly_DE1_3':[f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(1,4)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(1,4)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(1,4)],

'XGBEarly_DE1_2':[f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(1,3)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(0,3)]+\
    [f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl' for i in range(0,3)],


    'XGB_DTC_RollingModel':[
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelReCheck/XGBSelectBestPast_fix_eval_ic_half_d_400/res.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelReCheck/XGBSelectBestPast_fix_eval_ic_half_t_400/res.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelReCheck/XGBSelectBestPast_fix_eval_ic_half_c_400/res.pkl',
    ],
'XGBMultiFreq_DE1':[
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_ic_half_d_ic_d_half_year//round_1.pkl',
    '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/XGBMultiFreqDoubleEnsemble_train200_test10_ic_half_d_ic_d_half_year//round_1.pkl',
                    ]

}

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
pct_threshold = 0.05
per_amt_ratio = 0.005
deal_ratio = 0.1
initial_cash = 2e8
pool_num = 600
print(pct_threshold,per_amt_ratio,pool_num)
tag ='XGB_DCMultiFreq_T_Light_Cat'
print(tag)
file_list = para[tag]
from Script.lzc.pitches_integration import out_signal
for each in file_list:
    if not os.path.exists(each):
        out_signal(each.replace('.pkl','/'),20181231)

print(file_list)
tag = tag+'WithMax5threshold'
if False:#os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_%s_%.2f.pkl' % (tag, pct_threshold)):
    print(pct_threshold, 'signal exist')
    signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_%s_%.2f.pkl' % (tag, pct_threshold))
else:
    # signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list],
    #                                                                file_list, 20160104, 'actual_label', 'new', head=73)
    for each in file_list:
        out_signal(each.replace('.pkl','/'),20201231)
    signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('res.pkl', 'val_pred_path/').replace('.pkl', '_val_pred/') for x in file_list],
                                                                   file_list, 20160104, 'actual_label', 'new', head=73)
    pd.to_pickle([signal, pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_%s_%.2f.pkl' % (tag, pct_threshold))
    print('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_%s_%.2f.pkl' % (tag, pct_threshold))

tag = tag+'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d'%(deal_ratio,per_amt_ratio,pct_threshold,int(initial_cash))
pred_ret[~signal.fillna(False)] = np.nan
alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False,axis=1)<pool_num
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index,axis=0)
alpha_pool = pd.concat([original_pool,alpha_pool]).sort_index()>0.5
tag = tag.replace('RevTriggerFilterHolding','AlphaTriggerPoolV3Top%d'%pool_num)

instance = StartWithLimitCashVolConsider(pred_ret, 20160101, 20181231,stock_pool=alpha_pool,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio,barly_max_buy=100,initial_cash=initial_cash)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
cash_series.index = cash_series.index.astype(int).astype(str)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/DoubleEnsembleEarlyStop/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True,holding_num=holding_num)
send_file(['015664'],out_path)
print(out_path)

# '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
#  '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
#     '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
#     '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl'
# import os,shutil
# # source = '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl'
# # target = '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'
# source = '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl'
# target = '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'
#
# file_list = os.listdir(source.replace('.pkl','/'))
# for each in file_list:
#     if not os.path.exists(target.replace('.pkl','/')+each):
#         shutil.copy(source.replace('.pkl','/')+each,target.replace('.pkl','/')+each)
#     else:
#         print(target.replace('.pkl','/')+each,'exist')
#     if not os.path.exists(target.replace('.pkl','_val_pred/')+each):
#         shutil.copy(source.replace('.pkl', '_val_pred/') + each, target.replace('.pkl','_val_pred/') + each)
#     else:
#         print(target.replace('.pkl','_val_pred/') + each,'exist')
#     print(each,'done')
