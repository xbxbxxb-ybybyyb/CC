# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
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

    'XGBWithCrossFactor_Cat_Light': [
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
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl', ],

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

    ###########################

    'XGBOnlySWSHIFTMeanFixMIX_Cat_Light20211115': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_d_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_t_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBWithSWSHIFTMeanFixMIX_Cat_Light20211115': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_d_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_t_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnly20211115/XGBV4FactorListMixCrossSWMeanOnly20211115_ic_c_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBWithSWSHIFTMeanWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_c_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBWithSWSHIFTMeanOnly_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBSWMean_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGB_lightGBM_CatBoost_XGBFix': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossAppend1117_ic_c_train200_test10_factor_num0.pkl'
    ],

    'XGBFixMixWithCross1120_lightGBM_CatBoost': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossSelectFI20211119_ic_d_train200_test10_factor_num200.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossSelectFI20211119_ic_t_train200_test10_factor_num200.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossSelectFI20211119_ic_c_train200_test10_factor_num200.pkl',
    ],

    'XGB800_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/Extra/XGBV4FactorList_ic_d_train200_test10_factor_num800.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/Extra/XGBV4FactorList_ic_t_train200_test10_factor_num800.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/Extra/XGBV4FactorList_ic_c_train200_test10_factor_num800.pkl',
    ],

    'XGBAppendCrossFactor1122_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossAppend1121_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossAppend1121_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor/XGBV4WithCrossAppend1121_ic_c_train200_test10_factor_num400.pkl',

    ],

    ##################20211123

    'XGBWithSWNoSHIFReSaveTWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBWithSWNoSHIFReSaveTOnly_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBWithSWSHIFReSaveTOnly_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

    ],

    'XGBWithSW_S_M_N_T_TWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGBWithSW_S_M_N_T_ReSaveTOnly_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyNoShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyOldModelNewFeature20211123_ic_c_train200_test10_factor_num400.pkl',

    ],

    'Cat': ['/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'],
    'Light': ['/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'XGB_C': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_D': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XBG_T': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl'],

    'Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'
    ],

    'XGB_OldDTC_CatLight': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'
    ],

    'XGB_D_HalfYear': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_T_HalfYear': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_C_HalfYear': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGBNoEarlyStoping_lightGBM_CatBoost': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_c_train200_test10_factor_num400.pkl',
    ],
    'XGB_D_NoEarlyStoping': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_d_train200_test10_factor_num400.pkl'],
    'XGB_T_NoEarlyStoping': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_t_train200_test10_factor_num400.pkl'],
    'XGB_C_NoEarlyStoping': ['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4NoEarlyStop_ic_c_train200_test10_factor_num400.pkl'],

    ############################

    'fix因子400模型|fix200和fix矩阵200|fix200和5分钟矩阵处理200': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],

    'fix200和5分钟矩阵处理200': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],

    'fix因子400模型|fix200和5分钟矩阵处理200': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],

    'fix因子400模型|fix200和fix矩阵200|fix200和5分钟矩阵处理200|fix因子和5分钟因子': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],

    'fix因子400模型|fix200和5分钟矩阵处理200|fix因子和5分钟因子': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraDataWithMatrix20211129/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
        '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
    ],
    # 'XGBWithSWSHIFReSaveWithOrigin_SW5min_Cat_Light','XGBWithSW5minOnly_Cat_Light','XGBSW5minWithOrigin_Cat_Light'
    'XGB_Cat_Light_GNN': [
        '/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix_ic_c.pkl',
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    'XGB_Resave_Only': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedReSave/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedReSave/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedReSave/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

    '矩阵因子再集成残差处理': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/XGBV4ReversalRes_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/XGBV4ReversalRes_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/XGBV4ReversalRes_ic_c_train200_test10_factor_num400.pkl',
    ],

    '残差处理替换时序处理': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/XGBV4ReversalRes_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/XGBV4ReversalRes_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/XGBV4ReversalRes_ic_c_train200_test10_factor_num400.pkl',

    ],

    '矩阵因子再集成残差处理(重选)': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400.pkl',

    ],

    '残差处理替换时序处理(重选)': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400.pkl',

    ],



    '矩阵因子再集成1日残差处理': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400.pkl',
    ],

'最新版本+截面因子1': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor2022/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/XGBV4ReversalRes_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/XGBV4ReversalRes_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/XGBV4ReversalRes_ic_c_train200_test10_factor_num400.pkl',
    ],

    '最新版本+截面因子2': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor2022/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor2022/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor2022/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_d_train200_test10_factor_num400/XGBV4ReversalRes_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_t_train200_test10_factor_num400/XGBV4ReversalRes_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes_ic_c_train200_test10_factor_num400/XGBV4ReversalRes_ic_c_train200_test10_factor_num400.pkl',
    ],

'最新截面因子版本1_1':[        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor2022/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl',
],


    '矩阵因子1日残差处理替换': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400.pkl',
    ],


'矩阵_残差_DE': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400/XGBV4ReversalRes1Day_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_DEGain_train200_test10_factorNum400/XGB_DEGain_train200_test10_factorNum400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_corr_diff_train200_test10_factorNum400/XGB_corr_diff_train200_test10_factorNum400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_mae_diff_train200_test10_factorNum400/XGB_mae_diff_train200_test10_factorNum400.pkl',

    ],

'矩阵_DE': [

        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_DEGain_train200_test10_factorNum400/XGB_DEGain_train200_test10_factorNum400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_corr_diff_train200_test10_factorNum400/XGB_corr_diff_train200_test10_factorNum400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/DoubleEnsembleSelect/XGB_mae_diff_train200_test10_factorNum400/XGB_mae_diff_train200_test10_factorNum400.pkl',

    ],

'SW矩阵+MidCap': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/Barra/XGBV4_MidCapMeanOnly/XGBV4_MidCapMeanOnly_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/Barra/XGBV4_MidCapMeanOnly/XGBV4_MidCapMeanOnly_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/Barra/XGBV4_MidCapMeanOnly/XGBV4_MidCapMeanOnly_ic_c_train200_test10_factor_num400.pkl',

    ],


'最新截面因子版本1_2':['/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl',
],

'当前线上版本20220126+截面因子1':[
    '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
    '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl'


],

'当前线上版本20220126+截面因子2':[
    '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
    '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200.pkl',

],
'当前线上版本20220126+截面因子3':[
    '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
    '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
    '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',

'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl',

]

}
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_d_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_t_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200/XGBMixByFeatureImportance_ic_c_train200_test10_factor_num200.pkl',
'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFactor20220125/XGBOnlyCross_ic_c_train200_test10_factor_num0/XGBOnlyCross_ic_c_train200_test10_factor_num0.pkl',



def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag):
    file_list = para[tag]
    print(file_list)
    start = 20170101
    end = 20210531
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    tag = tag + 'WithoutMax5'  # +'WithMax5threshold' #
    # /data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_XGB_DCMultiFreq_T_Light_CatWithMax5threshold_0.05.pkl
    if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)):

        print(pct_threshold, 'signal exist')
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
        print('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
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
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))

    # pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
    tag = tag+'FIX' +alpha_pool_tag+ 'RevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))

    signal.index,pred_ret.index = pd.MultiIndex.from_tuples(signal.index.tolist()),pd.MultiIndex.from_tuples(pred_ret.index.tolist())

    alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}')#.loc[start:end].rank(ascending=False, axis=1) < pool_num
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]

    if not isinstance(alpha_pool.index[0],tuple):
        # alpha_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl')
        alpha_pool = alpha_pool.shift(1).rank(ascending=False, axis=1) < pool_num
        alpha_pool = pd.concat([alpha_pool, original_pool.drop(alpha_pool.index, axis=0)]).sort_index().reindex(signal.columns, axis=1)
        alpha_pool_arr = np.repeat(alpha_pool.values[:, None, :], 7, 1).reshape(alpha_pool.shape[0] * 7, alpha_pool.shape[1])
        index = pd.MultiIndex.from_tuples(list(itertools.product(alpha_pool.index.tolist(), [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
        alpha_pool = pd.DataFrame(alpha_pool_arr, index=index, columns=alpha_pool.columns)>0.5


    # alpha_pool = alpha_pool[signal.columns]
    pred_ret = pred_ret.loc[start:end][signal.loc[start:end]&alpha_pool.loc[start:end]]
    # pred_ret[~signal.fillna(False)] = np.nan
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]

    tag = tag + f'start{start}_end{end}'

    if not os.path.exists(
            '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
        instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=original_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                                 stk_min_amt=stk_min_amt)

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
    file_name = '%sVolConsider_UpBuy100_%dbp_cost' % (tag, int(10000 * cost))
    # if len(file_name)>200:
    #     file_name = file_name[:-127]
    out_path = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/Upgrade/{file_name}.xlsx'
    for each in record:
        helper.record[each] = record[each]
    # helper.evaluat_signal_by_stk(2260)
    # out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)


import itertools, gc

total = 18

from dataApi.ConceptApi import get_basic_values
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_pre_trade_date


pool_dict = {

    'FixEndV2':'FixEndV2.pkl',
'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
}

each = (0.05, 0.005, 2e8, 600)

calc_back_test_record(*(each + (0.1, 'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1, 'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light', 'FixEndV2')))
