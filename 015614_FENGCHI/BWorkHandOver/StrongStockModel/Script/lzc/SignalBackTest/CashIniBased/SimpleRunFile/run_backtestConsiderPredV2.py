# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderPredConsiderV2 import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
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

    'XGB_lightGBM_CatBoost': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_lightGBM_CatBoost_T': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_HX_ZSCORE': [
        '/data/user/015836/HFmodel/share/20210121/D400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400_zscore.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400_zscore.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_zscore.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40_zscore.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40_zscore.pkl',

    ],
    'XGB_lightGBM_CatBoost_Random_Extra': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/wyl/model_record/randomforestnew_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/extratreenew2_ic_all_t.pkl',
    ],
    'XGB_Extra_info_LightGBM': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_t_train200_test10_factor_num600_norm_window_40.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'LigtGBMOnly': [
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'
    ],
    'LigtGBMOnly_DTC': [
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_d.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_c.pkl',
    ],
    'XGB_Only': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_dtc_single': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'],
    'XGB_dtc_No_NNExtractor': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearly_ic_half_dtc_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_Light_DTCNN': [
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeature_ic_half_dtc_train200_test10_factor_num700_norm_window_40.pkl'

    ],
    'XGB_gain': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_gain.pkl'],
    'XGB_weight': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl'],
    'XGB_cover': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_gwc': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
                '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
                '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_light_Cat_DTC_GWC': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_DTC_GWC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'],
    'XGB_HX_DTC': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    'XGB_HX_DTC_Cat_Light': [
        '/data/user/015836/HFmodel/share/20210121/D400.pkl',
        '/data/user/015836/HFmodel/share/20210121/T400.pkl',
        '/data/user/015836/HFmodel/share/20210121/C400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
    'XGB_DCMultiFreq_T_Light_Cat': {
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    },

    'XGB_DCMultiFreq_Light_Cat': {
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    },

    'XGB_DCMultiFreq': {
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
        # '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        # '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    },
    'XGB_DCMultiFreq_T': {
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBWithNNFeatureNear40_ic_half_t_train200_test10_factor_num700_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_d_ic_d_half_year.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBMultiFreq_train200_test10_ic_half_c_ic_c_half_year.pkl',
        # '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        # '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    },
    'XGB_lightGBM_CatBoost_Validation': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],

    'XGBEarly_DE_ZSCORE0': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_0/round_0.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_0/round_0.pkl',
    ],
    'XGBEarly_DE_ZSCORE1': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_1/round_1.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_1/round_1.pkl',
    ],
    'XGBEarly_DE_ZSCORE2': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_2/round_2.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_2/round_2.pkl',
    ],
    'XGBEarly_DE_ZSCORE3': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_3/round_3.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_3/round_3.pkl',
    ], 'XGBEarly_DE_ZSCORE4': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_4/round_4.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_4/round_4.pkl',
    ], 'XGBEarly_DE_ZSCORE5': [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_5/round_5.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_5/round_5.pkl',
    ],
    'XGBEarly_DE_ZSCORE0_5': [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(6)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(6)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(6)],

    'XGBEarly_DE_ZSCORE1_3': [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(1, 4)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(1, 4)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(1, 4)],

    'XGBEarly_DE_ZSCORE1_2': [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_d_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(1, 3)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_t_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(0, 3)] + \
                             [
                                 f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsemble/ZSCORE/XGBDoubleEnsembleParamBestEarlyStop_ic_half_c_train200_test10_factor400/round_{i}/round_{i}.pkl'
                                 for i in range(0, 3)],

    'XGBMonthly_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ic_c_train200_test10_factor_num400.pkl',
    ],
    'XGB_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],
    'XGB_ZSCORE': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    ],

    'XGB_CatBoost_light_ZSCORE': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/ZSCORE/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',

    ],

    'XGBMonthly_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV2_ic_c_train200_test10_factor_num400.pkl',

    ],
    'XGB_ZhaBan_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ZhaBan_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ZhaBan_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_ZhaBan_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBMonthlyV3_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV3FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV3FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV3FactorList_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBMonthlyV4_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBMonthly_D': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl'],
    'XGBMonthly_T': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl'],
    'XGBMonthly_C': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl'],
    'CatBoost': ['/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'],
    'lighGBM': ['/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'XGB_D_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',

    ],

    'XGBFix5Min_DTC':
        [
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_d_ic_half_dcp.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_t_ic_half_tcp.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_c_ic_half_ccp.pkl',

        ],

    'XGBFix5Min_DTC_Cat_Light':
        [
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_d_ic_half_dcp.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_t_ic_half_tcp.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_c_ic_half_ccp.pkl',
            '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
            '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        ],
    'XGB5minFixPoint_DTC_Cat_Light': [
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBFix5minOnly_train200_test10_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBFix5minOnly_train200_test10_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBFix5minOnly_train200_test10_ic_half_c.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGB5minFixPointOldLoader_DTC_Cat_Light': [
        '/data/group/800442/800319/junkData/StrongStock//ModelRes/XGB5minFixPoint_ic_half_d_train200_test10_factor_num400/XGB5minFixPoint_ic_half_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/junkData/StrongStock//ModelRes/XGB5minFixPoint_ic_half_t_train200_test10_factor_num400/XGB5minFixPoint_ic_half_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/junkData/StrongStock//ModelRes/XGB5minFixPoint_ic_half_c_train200_test10_factor_num400/XGB5minFixPoint_ic_half_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGBFixWithInforcedMinute_DTC_Cat_Light': [
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBVALLFixSelected_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBVALLFixSelected_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBVALLFixSelected_ic_c_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGBFixCrossVal_DTC_Cat_Light': [
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_d/XGB_ic_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_t/XGB_ic_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_c/XGB_ic_c.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
    'XGB_DTC_Val40_Cat_Light': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_c_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],
    'XGB_DTC_Val40': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_c_train200_test10_factor_num400.pkl',

    ],
    'XGB_D_Val40': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_d_train200_test10_factor_num400.pkl'],
    'XGB_T_Val40': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_t_train200_test10_factor_num400.pkl'],
    'XGB_C_Val40': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList40Val_ic_c_train200_test10_factor_num400.pkl'],

    'XGB_DTC_Val40NoNorm': [
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_d/XGB_ic_dNoNorm.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_t/XGB_ic_tNoNorm.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_c/XGB_ic_cNoNorm.pkl',
    ],

    'XGB_D_Val40NoNorm': ['/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_d/XGB_ic_dNoNorm.pkl'],
    'XGB_T_Val40NoNorm': ['/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_t/XGB_ic_tNoNorm.pkl'],
    'XGB_C_Val40NoNorm': ['/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/HXCrossVal/XGB_ic_c/XGB_ic_cNoNorm.pkl'],
    'XGB_DTC_Mix5MinFix': [
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5minSortTogether_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5minSortTogether_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMulti/XGBMultiFreqFix5minSortTogether_train200_test10_ic_c_ic_half_c.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGB_DTC_FixWithAllEnhanced': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBEnhanced_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBEnhanced_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBEnhanced_ic_c_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGBWithNNExtracted800_Cat_Light': [
        '/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtractor_ic_d_train200_test10_factor_num800/XGBUseNNExtractor_ic_d_train200_test10_factor_num800.pkl',
        '/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtractor_ic_t_train200_test10_factor_num800/XGBUseNNExtractor_ic_t_train200_test10_factor_num800.pkl',
        '/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtractor_ic_c_train200_test10_factor_num800/XGBUseNNExtractor_ic_c_train200_test10_factor_num800.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    ],

    'XGBFix5MinFreqDelta_DTC_Cat_Light':
        [
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_d_ic_h_d.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_t_ic_h_t.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_c_ic_h_c.pkl',
            '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
            '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        ],
    'XGBFix5MinFreqDeltaT_DTC_Cat_Light':
        [
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_d_ic_h_d.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_t_ic_h_d.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinute_train200_test10_ic_c_ic_h_d.pkl',
            '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
            '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        ],

    'XGBFix5MinFreqDeltaHandy_DTC_Cat_Light':
        [
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_d_ic_h_d.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_t_ic_h_t.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_c_ic_h_c.pkl',
            '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
            '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        ],

    'XGBMonthlyV4_Cat_Light_New': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbm_record/lightgbmcus_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBMonthlyV4_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

    ],
    'XGBMonthlyMixDelta_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEra/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',

    ],
    'XGBMonthlyMixDelta20210820_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraData20210820/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraData20210820/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraData20210820/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',

    ],
 'XGBMonthlyTorchNNExtract_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_d_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_d_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_t_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_t_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_c_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_c_train200_test10_factor_num800.pkl',

    ],

 'XGBMonthlyTorchNNExtract': [
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_d_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_d_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_t_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_t_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseNNExtraTroch_ic_c_train200_test10_factor_num800/XGBUseNNExtraTroch_ic_c_train200_test10_factor_num800.pkl',

    ],

 'XGBMonthlyHXTorchNNExtract_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseHXNNExtractor_ic_d_train200_test10_factor_num800/XGBUseHXNNExtractor_ic_d_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseHXNNExtractor_ic_t_train200_test10_factor_num800/XGBUseHXNNExtractor_ic_t_train200_test10_factor_num800.pkl',
f'/data/group/800442/800319/Strong_stock/C3PO/XGBUseHXNNExtractor_ic_c_train200_test10_factor_num800/XGBUseHXNNExtractor_ic_c_train200_test10_factor_num800.pkl',

    ],

 'XGBMonthlyCrossFixOriginFactor_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
# f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_c_train200_test10_factor_num400.pkl'

 ],

 'XGBMonthlyCrossFixReselect_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_c_train200_test10_factor_num400.pkl',


 ],



'XGBWithCrossFactor_Cat_Light':[
'/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorListWithCross_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorListWithCross_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorListWithCross_ic_c_train200_test10_factor_num400.pkl',


],

    'XGBMonthlyV4WithCrossFix_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4WithCrossFix': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBCrossReSelect_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBMonthlyV4_Cat_Light_DT_TC_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4_Cat_Light_DT': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4_Cat_Light_TC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

    ],


'XGBMonthlyV4_Cat_Light_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        # '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4_Light_DT_TC_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4_Cat_DT_TC_DTC': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_tc_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatV4FactorList_ic_dtc_train200_test10_factor_num400.pkl',

    ],
'XGBMonthlyV4_Cat_DT_NoEarly': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatNoEarlyV4FactorList_ic_dt_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/LightNoEarlyStopV4FactorList_ic_dt_train200_test10_factor_num400.pkl'

    ],

'XGBMonthlyV4With5minAfterDelta_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210903/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210903/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210903/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',

    ],


'XGBMonthlyV4WithCrossFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4OnlyCrossFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4OnlyCrossFixMIXReselect_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4CrossFixMIXReselect_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossReselect_ic_c_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4MIX20210908_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
    '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210907/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
    '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210907/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
    '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210907/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],

'XGBMonthlyV4_Cat3_Light3': [
        '/data/group/800442/800319/wyl/model_record/catboosts/catboostnew3_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbm_record/lightgbmnew3_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

    ],
    'XGBMonthlyV4_Cat_Light_Fix5min20210909': [
      '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
      '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
                                              ],

'XGBMonthlyV4_Cat200_Light': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/CatNoEarlyV4FactorList_ic_dt_train200_test10_factor_num200.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',],

'XGBMonthlyV4WithCrossFactorReplace_Cat_Light': [
   '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
   '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_d_train200_test10_factor_num113.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_t_train200_test10_factor_num113.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_c_train200_test10_factor_num113.pkl',
],

'XGBMonthlyV4WithCrossFactorAppend_Cat_Light': [
   '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
   '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_d_train200_test10_factor_num400.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_t_train200_test10_factor_num400.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend0915_ic_c_train200_test10_factor_num400.pkl',
],


'XGBMonthlyV4WithSWCorrFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4OnlySWCorrFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4OnlySWMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4_Origin_SWMean_SWCorr_SWCross_FixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_c_train200_test10_factor_num400.pkl',

'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],


'XGBMonthlyV4_SWMean_SWCorr_SWCross_FixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCross_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4_SWMean_SWCorr_FixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4_Origin_SWMean_SWCorr_FixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly_ic_c_train200_test10_factor_num400.pkl',

f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossCorrSW_ic_c_train200_test10_factor_num400.pkl',

'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBMonthly_Val20': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_Val20_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_Val20_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGB_Val20_ic_c_train200_test10_factor_num400.pkl',

    ],

'XGBMonthlyV4WithCrossFactorReplace1027_Cat_Light': [
   '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
   '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_d_train200_test10_factor_num200.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_t_train200_test10_factor_num200.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_c_train200_test10_factor_num200.pkl',
],
'XGBMonthlyV4WithCrossFactorAppend1027_Cat_Light': [
   '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
   '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_d_train200_test10_factor_num400.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_t_train200_test10_factor_num400.pkl',
   '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4WithCrossAppend1027_ic_c_train200_test10_factor_num400.pkl',
],










################################################ SHITF_1_CORR_MATRIX

'XGBMonthlyV4OnlySWSHIFTMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_c_train200_test10_factor_num400.pkl',


    ],

'XGBMonthlyV4WithSWSHIFTMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnly20211104_ic_c_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],


################

'XGBMonthlyV4OnlySWSHIFTTestMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_c_train200_test10_factor_num400.pkl',


    ],

'XGBMonthlyV4WithSWSHIFTTestMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_c_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

'XGBMonthlyV4_Cat_Light_FIX5minOnlyFixSWMean': [
      '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
      '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_c_train200_test10_factor_num400.pkl',

                                              ],

'XGBMonthlyV4_Cat_Light_XGBMonthlyV4_Cat_Light_FIX5minWithFixSWMean': [
      '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
      '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
      '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_d_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_t_train200_test10_factor_num400.pkl',
f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211104/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211109_ic_c_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
                                              ],

}



def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag, signal_threshold, down_signal_ratio):
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
    tag = f'{tag}_deal{deal_ratio:.2f}_per{per_amt_ratio * 1000}bp_thre{int(pct_threshold * 100)}_cash{initial_cash:.0e}_Top600_start{start}_end{end}_' \
        f's_thre{signal_threshold:.2f}_d_thre{down_signal_ratio:.2f}'
    out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/PredConsiderV2PrameterSeeking/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    if os.path.exists(out_path):
        print(out_path,'exist')
        return
    if os.path.exists(signal_file):

        print(pct_threshold, 'signal exist')
        signal, pred_ret = pd.read_pickle(signal_file)
        print(signal_file)
    else:
        for each in file_list:
            if not os.path.exists(each):
                out_signal(each.replace('.pkl', '/'))
        # signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, 20160104, 'actual_label',
        #                                                                'new',
        #                                                                head=135)
        signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, start,
                                                                                      'actual_label',
                                                                                      'new',
                                                                                      head=None, end=end)
        pd.to_pickle([signal, pred_ret], signal_file)

    # pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
    # tag = tag + 'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))


    pred_ret[~signal.fillna(False)] = np.nan
    if pool_dict[alpha_pool_tag] is None:
        alpha_pool = pd.DataFrame()
    elif isinstance(pool_dict[alpha_pool_tag], pd.DataFrame):
        alpha_pool = pool_dict[alpha_pool_tag].shift(1).loc[start:end]
    elif isinstance(pool_dict[alpha_pool_tag], str):
        alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num
    else:
        raise Exception('Wrong type')
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    # tag = tag.replace('RevTriggerFilterHolding', f'{alpha_pool_tag}Top{pool_num}_real{pool_num}')
    # tag = tag+f'start{start}_end{end}'
    print('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    if not os.path.exists(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
        instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt, signal_threshold=signal_threshold, down_signal_ratio=down_signal_ratio)

        record = instance.run_backtest()
        cash_series = instance.cash_series
        holding_num = instance.holding_num
        order_info = instance.order_info
        # pd.to_pickle([record, cash_series, holding_num],
        #              '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
    else:
        raise Exception('Exist')
        record, cash_series, holding_num = pd.read_pickle(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    #
    # out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/PoolCompare20210519/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
    for each in record:
        helper.record[each] = record[each]
    # helper.evaluat_signal_by_stk(2260)
    # out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)

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
each = ()

import itertools
para_list = list(itertools.product([0.5,0.6,0.7,0.8,0.9],[0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6]))+[(1,1)]

from xquant.compute.aimr import AIMR
d_threshold,s_ratio = para_list[0]#eval(AIMR.getParam())#(0.2,1)

calc_back_test_record(0.05, 0.005, 2e8, 600, 0.1, 'XGBMonthlyV4_Cat_Light_Val', 'CS_XGB_OLS_condition_style_rank_ex20',
                      down_signal_ratio=d_threshold, signal_threshold=s_ratio)





