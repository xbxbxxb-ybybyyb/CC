# @Time : 2021/3/15 8:35
# @Author : Zhichen Lu
# @File : RegIntegration.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time, datetime
from tqdm import tqdm
from multiprocessing import Process
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
from sklearn.externals import joblib
import configparser
import tensorflow as tf
from tensorflow.python.ops import math_ops
from sklearn.linear_model import LinearRegression
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

def get_fix_factor_evaluation(num, end_index, eval_indicator):
    using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
    factor_evaluation = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/ic_half.pkl')
    factor_evaluation = pd.DataFrame(factor_evaluation)
    if not eval_indicator in factor_evaluation.index.levels[0]:
        raise Exception('Unavailable indicator')
    factor_evaluation = factor_evaluation.loc[eval_indicator]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index)))
    factor_evaluation = factor_evaluation.loc[target_date]
    inter_col = list(set(factor_evaluation.index).intersection(set(using_factor_list)))
    factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
    return sorted(factor_list)


def load_model_xgb(path, param={}):
    booster = xgb.Booster(param)
    booster.load_model(path)
    return booster


def load_model_sklearn(path):
    clf = joblib.load(path)
    return clf


def load_model_NN(path, param={}):
    def Network(param={}):
        # TODO:define your network structure and param
        return

    model = Network(param)
    model.load_weight(path)
    return model


def load_linear_v2(file):
    def ic_all(y_true, y_pred):
        yn_true = y_true - tf.keras.backend.mean(y_true)
        yn_true = yn_true / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_true))), 1e-7)
        yn_pred = y_pred - tf.keras.backend.mean(y_pred)
        yn_pred = yn_pred / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_pred))), 1e-7)
        return tf.keras.backend.sum(yn_true * yn_pred)

    def mae(y_true, y_pred):
        return tf.keras.backend.mean(tf.keras.backend.abs(y_pred - y_true))

    def mix_loss(y_true, y_pred):
        yn_true = y_true - tf.keras.backend.mean(y_true)
        yn_true = yn_true / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_true))), 1e-7)
        yn_pred = y_pred / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(y_pred))), 1e-7)
        return - tf.keras.backend.sum(yn_true * yn_pred)

    def small_tanh(x):
        return tf.keras.backend.tanh(x) / 10

    custom_objects = {'ic_all': ic_all, 'mae': mae, 'mix_loss': mix_loss,
                      'small_tanh': small_tanh}

    model = tf.keras.models.load_model(file, custom_objects=custom_objects)
    return model

model_conf = {

    'HX_D': '/data/user/015836/HFmodel/share/20210121/D400.pkl',
    'HX_T': '/data/user/015836/HFmodel/share/20210121/T400.pkl',
    'HX_C': '/data/user/015836/HFmodel/share/20210121/C400.pkl',
    'XGB_C': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    'XGB_D': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    'XGB_T': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    'Cat_T': '/data/group/800319/wyl/model_record/catboosts/catboostnew2_ic_all_t.pkl',
    'Light_T': '/data/group/800319/wyl/model_record/lightgbm_record/lightgbmnew_ic_all_t.pkl',
    'XGB_Cov': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl',
    'XGB_W': '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_weight.pkl',
    'XGB_G':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGBAllFactor_train400_test10_factornum400_eval_cover.pkl'
}

# import shutil,os
#
# for tag in ['D','T','C']:
#     if not os.path.exists(model_conf['HX_%s'%tag].replace('.pkl','/')):
#         os.mkdir(model_conf['HX_%s'%tag].replace('.pkl','/'))
#     for i in range(73):
#         shutil.copy(f'/data/user/015836/HFmodel/NewFixImprove/Linear/20210120/{tag}/predict/{i}',model_conf['HX_%s'%tag].replace('.pkl',f'/{para_list[i][1][1]}.pkl'))

model_features = {
    'Cat_T': lambda x: ['AbnormalReturnPVCorrBias20d', 'AbnormalVolumePVCorr', 'AccelerateStd', 'AmountGrowthDuringLowRet', 'AmtStdStd5d', 'AmtStd_Mean_1', 'AmtStd_Mean_5',
                        'AmtStd_Std_5', 'BAStrength', 'BestWorstReSharpe5d', 'Beta300', 'BotTopCumSwingStdRatio', 'BottomTopPriceSwingRatio', 'CGO', 'CORA_R_3',
                        'CRCS_raw_rank_ms10', 'CRCS_raw_rank_skew10', 'Close2BarHigh', 'Close2High', 'CloseCorrVolume_5', 'CloseExcessPercent_1', 'CloseSkew_Mean_5',
                        'CloseVolumeCorrBias20d', 'CloseVwapRetSkew', 'Cor500D3', 'CorAmtMeanMean5', 'CorPV5', 'CorrAmpRet_5', 'CorrAmpVwap_1', 'CorrAmpVwap_5',
                        'CorrCloseVol_Mean2DStd_5', 'CorrCloseVol_Mean_1', 'CorrCloseVol_Mean_5', 'CorrDelVolumePriceMean', 'CorrHighLowAvgToAmt_Mean_1',
                        'CorrHighLowAvgToAmt_Mean_5', 'CorrHighVol', 'CorrLowVol_mean5', 'CorrRankCloseVolume_5', 'CorrRankOpenVolume_10', 'CorrResisVWAP', 'CorrRetVol_5',
                        'CorrVWAPdt', 'CorrVWAPstd', 'CorrVolumePriceRankSharpe', 'CorrVwapCVPriceLast60', 'CorrVwapVol_1', 'CorrVwapVol_5', 'CumPVRatioCorr', 'DIFMaxPct_1_5',
                        'DIFMaxRaw_1_5', 'DIFMeanRaw_5_5', 'DIFSkewRank_5_1', 'DisNMean_1', 'DisNRaw_5', 'DisNStd_1', 'DisPMean_5', 'DisPRaw_5', 'DisPRegbeta_5', 'DisPStd_1',
                        'DivergWinLossRMeanRank_5_5', 'FIX_lly_8', 'FactorAlpha027', 'FactorMin10_meandivstd', 'FactorMin117_mean', 'FactorMin118_mean', 'FactorMin118_meandivstd',
                        'FactorMin129_diff', 'FactorMin137_mean', 'FactorMin13_diff', 'FactorMin13_diffdivstd', 'FactorMin13_mean', 'FactorMin14_diff', 'FactorMin150_diff',
                        'FactorMin150_mean', 'FactorMin155_mean', 'FactorMin155_meandivstd', 'FactorMin157_diff', 'FactorMin157_diffdivstd', 'FactorMin15_mean',
                        'FactorMin160_mean', 'FactorMin18_meandivstd', 'FactorMin193_mean_re', 'FactorMin199_meandivstd', 'FactorMin1_diff_div_std', 'FactorMin1_mean',
                        'FactorMin201_mean', 'FactorMin215_mean', 'FactorMin215_meandivstd', 'FactorMin217_mean_re', 'FactorMin26_mean', 'FactorMin289_mean_re', 'FactorMin28_mean',
                        'FactorMin343_mean_re', 'FactorMin343_self_re', 'FactorMin35_diff', 'FactorMin35_mean', 'FactorMin383_mean_div_std_re', 'FactorMin403_mean_div_std_re',
                        'FactorMin403_mean_re', 'FactorMin405_mean_div_std_re', 'FactorMin412_mean_div_std_re', 'FactorMin42_mean', 'FactorMin430_mean_div_std_re',
                        'FactorMin450_mean_re', 'FactorMin453_std_re', 'FactorMin66_mean', 'FactorMin70_diff', 'FactorMin70_mean', 'FactorMin80_diff', 'FactorMin81_diff_div_std',
                        'FactorMin81_mean', 'FactorMin87_diff', 'FactorMin87_mean_div_std', 'FactorMin89_diff', 'FactorMin93_diff', 'FactorMin94_mean', 'FactorMin95_mean',
                        'GTJA16_max5', 'GTJA1_6', 'GTJA2', 'GTJA27_max12', 'GTJA27_weight12', 'GTJA32', 'GTJA40', 'GTJA41', 'GTJA43', 'GTJA43_min5', 'GTJA48', 'GTJA5',
                        'GTJA53_ts_rank5', 'GTJA54G', 'GTJA54_N', 'GTJA62', 'GTJA8', 'GTJA8_mean5', 'HFPTSCorrBias', 'HFPTSCorrMinAdj', 'HFPTSCorrStdAdj',
                        'HF_5mRePosVolVolatilityStable', 'HF_AmtDeg1', 'HF_AmtStdStrengthCloseBias', 'HF_AmtStdStrengthCloseChange_13h', 'HF_AmtStdStrengthDev_13h',
                        'HF_AmtStrengthCloseChange_13h', 'HF_AmtVolatilityPriceCorr5D_13h', 'HF_AmtVolatilityPriceCorr_13h', 'HF_CMExcessRetWeightSkew_13h',
                        'HF_CloseLowHighStdVolumeRatio_13h', 'HF_CorrBuyStrength_13h', 'HF_CorrMaxVolumeZScore_13h', 'HF_DVwapDVolumeCorrZscore_13h', 'HF_ForecastEPDelta40d',
                        'HF_HighPinZscore_13h', 'HF_HighVwapSkew_13h', 'HF_Hl2OStrength_13h', 'HF_HmL2CVwapCorrZscore_13h', 'HF_HmL2CVwapCorr_13h', 'HF_LinearDiffStdRatio_13h',
                        'HF_LinearHighDiffSkew_13h', 'HF_LowReBiasSelfCorrStable_13h', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h',
                        'HF_MeanIntradayReturnAcrossProfitableInvestors_13h', 'HF_OpenVwapSkew', 'HF_OverBuy', 'HF_PriceDiffStdRatio', 'HF_PriceVolIndustryDelta',
                        'HF_RetHHIZscore', 'HF_RetTopVwapAmtCorrBias', 'HF_ReverseVolRatioVWAP', 'HF_Shortcut2CloseCloseCorrZscore', 'HF_TwapRetWeightSkew',
                        'HF_UpReaturnRealStdZScore', 'HF_UpRetTurnDiffSharpe', 'HF_VmL2HmVDiffStdRatio', 'HF_VmL2HmVStdRatio', 'HF_VolumeStdStrengthCloseChangePct',
                        'HF_VolumeStrengthCloseStdBias', 'HF_VolumeStrengthDeg1', 'HF_VolumeTopVwapRatio', 'HF_VwapAmtUpCorrInLowVolatility_13h', 'HF_VwapBollingUp_13h',
                        'HF_VwapLowCorrZscore_13h', 'HF_VwapRetSkew_13h', 'HF_VwapTailTopVolumeDiffRatio_13h', 'HF_VwapTailTurnRatioZscore', 'HF_VwapTailVolumeRatio_13h',
                        'HF_VwapTopTailAmtRatio_13h', 'HF_VwapTopTailTurnRatioZscore', 'HF_VwapTopTailVolume_13h', 'HF_VwapTopVolumeRatioZscore_13h', 'HF_WR2d', 'HLLength5',
                        'HLStd1mean', 'HLStdRatio', 'HLTR_mean5_intraday', 'HfHalfDayCloseRtnCountDiffBias_13h', 'HfHalfDayCloseRtnCountDiff_13h',
                        'HfLast120CloseVolumeStdCorrBias_13h', 'HfLast120HighLowDiffAmtCloseCorrDelta_13h', 'HfLast120HighLowDiffAmtCloseCorrPreBias',
                        'HfLast120HighLowDiffAmtCloseCorrSharpe', 'HfLast120LongTurnSkew_13h', 'HfLast120MaxRtnCloseCorrBias_13h', 'HfLast120MinRtnCloseCorrBias',
                        'HfLast120RtnPerAmtVolCorr', 'HfLast120RtnPerAmtVolPre1minCorr', 'HfLast120RtnStdCloseCorrBias', 'HfRtnPerAmtVolCorr', 'HfSwingCloseCorr',
                        'HfTopRtnVolumeRatioMean', 'HfVolClosePre5minCorr10d', 'High2LowVolDown', 'High2Low_1', 'High2Low_5', 'HighCloseDistance', 'HighFreqDownSpeed',
                        'HighFreqDrawBack', 'HighFreqDrawBackMeanBias', 'HighFreqRelativeClose', 'HighFreqRetRefStd', 'HighFreqSwingStdCmp', 'HighFreqTurnRetCorr',
                        'HighFreqWaveRetStd', 'HighLowHitFreqRatio', 'HighLowMeanVwapRetSharpe', 'HighLowStdBias20d', 'HighLowStdLowDistance10d', 'HighLowVwapRatio',
                        'HighSkew_Mean_5', 'HighTurnVwap', 'IdeaVL', 'IdeaVStd', 'IdealRev2', 'IdealSwingMin2D', 'IndustryExcessPVCorrBias5d', 'InflowOutflowDiff',
                        'InstitutionalVolumeRatio2min', 'L2C5', 'LargeSmallVolumeVWAPRatio', 'Last30MaxClimbBias20d', 'Last30MaxDrawdownBias20d', 'LatestRetRatio', 'LogAmt_1',
                        'LogAmt_5', 'LogFreeTurn_1', 'LogRtn2Amt5', 'LowHighRetStdRatio', 'LowHighStdRatio', 'LowSharpeAmountStdRatio', 'MACDNumDiffBeta_5_1',
                        'MACDNumDiffBeta_5_5', 'MACDNumDiffMean_1_1', 'MACDNumDiffMean_5_5', 'MACDNumDiff_5_5', 'MaxDrawDown', 'MeanRatio_min5', 'Min10ReUpLast5Min',
                        'Min1WeightedFlow_1', 'MinCapitalGainAutoCorr', 'MinCapitalGainOverhang', 'MinCapitalGainRH', 'MinCorrAbsRePriceRank2D', 'MinCorrExcessPriceRank',
                        'MinCorrVolumePrice_1', 'MinCorrVolumeRetUp_1', 'MinExtremRet', 'MinPVCorr', 'MinPrePVCorr', 'MinPrePriceAutoCorr', 'MinPrePriceRate', 'MinPriceAutoCorr',
                        'MinPriceBeta', 'MinUpDownVolRet', 'MinuteTVRtnRank', 'MinuteVolatilityPriceCorr', 'NewCorrHighVol', 'OverBuySellSkewRegbeta_5_5', 'OverBuySell_Mean_5',
                        'OverBuy_Mean_1', 'OverBuy_Sell_3', 'PDS', 'PDSS', 'PVRatioCorr', 'PriceRange_5', 'PriceSkew', 'PriceVolume_5', 'RSIMeanRegbeta_5_15', 'RSIMinMean_1_15',
                        'RSJT', 'RS_mean', 'RawAmtStdRatio', 'ReLow_13h', 'Ret30Mean2Std_10', 'Ret30RankMean_5', 'RetAdjVolMaxMean_1_5', 'RetAdjVolMaxRaw_1_1',
                        'RetAdjVolMeanRank_3_5', 'RetAdjVolMeanSr_1_5', 'RetAdjVolSkewMean_1_1', 'RetAdjVolSkewRaw_1_1', 'RetGather0p9mean5', 'RetMean_Rank', 'RetStd_Mean_1',
                        'RetToStd', 'RetToVolSke', 'RetUpWeightedByVolSR', 'RetVolCVMultiple', 'RetVolMaxRaw_1_5', 'RetVolMeanSr_1_1', 'RetVolMeanSr_5_1', 'RetVolSkewMean_1_5',
                        'RetVolSkewRaw_5_1', 'RevExclu4mean', 'RollingSignDownWick', 'Rsrs', 'SharpeDuringStdDrop', 'SignDownWick', 'SkewDuringAmountHike',
                        'Smartmoney_ret_mean_02_05_rolling1', 'SplitStdRatio', 'SplitVolumeRatio', 'StdUpDown', 'StructedRev5', 'TemporalVolumePriceCorr',
                        'TopAmountRatioVolumeDiffSharpe', 'TurnFree_3', 'TurnHighKurt', 'TurnHighSkew', 'TurnStdPure3mean', 'TurnWeiRet10slope', 'TurnWeiRet3max',
                        'TurnWeiRet3mean', 'TurnWeiRet3min', 'TurnWeiRet5max', 'TurnWeiRet5mean', 'TurnWeiRet5min', 'TwapSkewToVwap', 'UDContrast5mean', 'UpCountLowDistance10d',
                        'UpDownVolRatioStdRaw_1_1', 'UpDownVolRatioStdRegbeta_5_1', 'UpVolatilityRate', 'VWMidReurnSharpe5d', 'VarResampleMeanL', 'VolBurstReturn',
                        'VolGather0p9mean5', 'VolMeanSharpeUp2Down', 'VolaDownward20', 'VolumeDownChange_13h', 'VolumeMax10min2All_13h', 'VolumeStd_Mean_1', 'VolumeStd_Mean_5',
                        'VolumeUpPVCorr_13h', 'Vwap2Twap5mean', 'VwapAmtCorrMean5d_13h', 'VwapBollingerBand30min_13h', 'VwapBollingerBand_13h', 'VwapmaLowDiffSkew_13h',
                        'WAPResistBackTop_13h', 'WR2d_13h', 'WR_13h', 'WeightedFlow_1', 'WilliamUp_diffstd5', 'WilliamsIndicator_13h', 'adjEMAbc_intraday5',
                        'adjdmstdcpt_intraday_5', 'adjstdsd_intraday_5', 'adjstdstm_intraday_5', 'adjstdwms_intraday_5', 'cummaxdd_ntmaxstd_20_3', 'cummaxdd_nttrbmean_20_10',
                        'cummaxdd_nttrbmean_20_3', 'cummaxdd_nttrbskew_20_10', 'dailyms_intraday_5', 'dretvvolnew_ntmsmean_60_3', 'dretvvolnew_nttbskew_20_10', 'hfCPVCorrHD_13h',
                        'hfCPVCorrHDbias_13h', 'hfCPVCorrHDmean_13h', 'hfCapStdRatioMin', 'hfHVR5', 'hfHVRbias', 'hfHighVolPVcorr', 'hfHighVolPVcorr5', 'hfHighVolPVcorrbias',
                        'hfIdxCorr', 'hfLowCapRetMax', 'hfLowCapRetMin', 'hfMktLSCap', 'hfMktLSCapMR5', 'hfMktLSCapSR', 'hfPVcorrHD', 'hfTurnStdHD', 'hfUpPVcorr5', 'hfUpRRC',
                        'hfUpRRCbias', 'subrr2adjwms_intraday_5', 'subrradjwms_intraday_5', 'zhy_fix_5'],
    'Light_T': lambda x: ['AbnormalReturnPVCorrBias20d', 'AbnormalVolumePVCorr', 'AccelerateStd', 'AmountGrowthDuringLowRet', 'AmtStdStd5d', 'AmtStd_Mean_1', 'AmtStd_Mean_5',
                          'AmtStd_Std_5', 'BAStrength', 'BestWorstReSharpe5d', 'Beta300', 'BotTopCumSwingStdRatio', 'BottomTopPriceSwingRatio', 'CGO', 'CORA_R_3',
                          'CRCS_raw_rank_ms10', 'CRCS_raw_rank_skew10', 'Close2BarHigh', 'Close2High', 'CloseCorrVolume_5', 'CloseExcessPercent_1', 'CloseSkew_Mean_5',
                          'CloseVolumeCorrBias20d', 'CloseVwapRetSkew', 'Cor500D3', 'CorAmtMeanMean5', 'CorPV5', 'CorrAmpRet_5', 'CorrAmpVwap_1', 'CorrAmpVwap_5',
                          'CorrCloseVol_Mean2DStd_5', 'CorrCloseVol_Mean_1', 'CorrCloseVol_Mean_5', 'CorrDelVolumePriceMean', 'CorrHighLowAvgToAmt_Mean_1',
                          'CorrHighLowAvgToAmt_Mean_5', 'CorrHighVol', 'CorrLowVol_mean5', 'CorrRankCloseVolume_5', 'CorrRankOpenVolume_10', 'CorrResisVWAP', 'CorrRetVol_5',
                          'CorrVWAPdt', 'CorrVWAPstd', 'CorrVolumePriceRankSharpe', 'CorrVwapCVPriceLast60', 'CorrVwapVol_1', 'CorrVwapVol_5', 'CumPVRatioCorr', 'DIFMaxPct_1_5',
                          'DIFMaxRaw_1_5', 'DIFMeanRaw_5_5', 'DIFSkewRank_5_1', 'DisNMean_1', 'DisNRaw_5', 'DisNStd_1', 'DisPMean_5', 'DisPRaw_5', 'DisPRegbeta_5', 'DisPStd_1',
                          'DivergWinLossRMeanRank_5_5', 'FIX_lly_8', 'FactorAlpha027', 'FactorMin10_meandivstd', 'FactorMin117_mean', 'FactorMin118_mean',
                          'FactorMin118_meandivstd', 'FactorMin129_diff', 'FactorMin137_mean', 'FactorMin13_diff', 'FactorMin13_diffdivstd', 'FactorMin13_mean', 'FactorMin14_diff',
                          'FactorMin150_diff', 'FactorMin150_mean', 'FactorMin155_mean', 'FactorMin155_meandivstd', 'FactorMin157_diff', 'FactorMin157_diffdivstd',
                          'FactorMin15_mean', 'FactorMin160_mean', 'FactorMin18_meandivstd', 'FactorMin193_mean_re', 'FactorMin199_meandivstd', 'FactorMin1_diff_div_std',
                          'FactorMin1_mean', 'FactorMin201_mean', 'FactorMin215_mean', 'FactorMin215_meandivstd', 'FactorMin217_mean_re', 'FactorMin26_mean',
                          'FactorMin289_mean_re', 'FactorMin28_mean', 'FactorMin343_mean_re', 'FactorMin343_self_re', 'FactorMin35_diff', 'FactorMin35_mean',
                          'FactorMin383_mean_div_std_re', 'FactorMin403_mean_div_std_re', 'FactorMin403_mean_re', 'FactorMin405_mean_div_std_re', 'FactorMin412_mean_div_std_re',
                          'FactorMin42_mean', 'FactorMin430_mean_div_std_re', 'FactorMin450_mean_re', 'FactorMin453_std_re', 'FactorMin66_mean', 'FactorMin70_diff',
                          'FactorMin70_mean', 'FactorMin80_diff', 'FactorMin81_diff_div_std', 'FactorMin81_mean', 'FactorMin87_diff', 'FactorMin87_mean_div_std',
                          'FactorMin89_diff', 'FactorMin93_diff', 'FactorMin94_mean', 'FactorMin95_mean', 'GTJA16_max5', 'GTJA1_6', 'GTJA2', 'GTJA27_max12', 'GTJA27_weight12',
                          'GTJA32', 'GTJA40', 'GTJA41', 'GTJA43', 'GTJA43_min5', 'GTJA48', 'GTJA5', 'GTJA53_ts_rank5', 'GTJA54G', 'GTJA54_N', 'GTJA62', 'GTJA8', 'GTJA8_mean5',
                          'HFPTSCorrBias', 'HFPTSCorrMinAdj', 'HFPTSCorrStdAdj', 'HF_5mRePosVolVolatilityStable', 'HF_AmtDeg1', 'HF_AmtStdStrengthCloseBias',
                          'HF_AmtStdStrengthCloseChange_13h', 'HF_AmtStdStrengthDev_13h', 'HF_AmtStrengthCloseChange_13h', 'HF_AmtVolatilityPriceCorr5D_13h',
                          'HF_AmtVolatilityPriceCorr_13h', 'HF_CMExcessRetWeightSkew_13h', 'HF_CloseLowHighStdVolumeRatio_13h', 'HF_CorrBuyStrength_13h',
                          'HF_CorrMaxVolumeZScore_13h', 'HF_DVwapDVolumeCorrZscore_13h', 'HF_ForecastEPDelta40d', 'HF_HighPinZscore_13h', 'HF_HighVwapSkew_13h',
                          'HF_Hl2OStrength_13h', 'HF_HmL2CVwapCorrZscore_13h', 'HF_HmL2CVwapCorr_13h', 'HF_LinearDiffStdRatio_13h', 'HF_LinearHighDiffSkew_13h',
                          'HF_LowReBiasSelfCorrStable_13h', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h', 'HF_MeanIntradayReturnAcrossProfitableInvestors_13h',
                          'HF_OpenVwapSkew', 'HF_OverBuy', 'HF_PriceDiffStdRatio', 'HF_PriceVolIndustryDelta', 'HF_RetHHIZscore', 'HF_RetTopVwapAmtCorrBias',
                          'HF_ReverseVolRatioVWAP', 'HF_Shortcut2CloseCloseCorrZscore', 'HF_TwapRetWeightSkew', 'HF_UpReaturnRealStdZScore', 'HF_UpRetTurnDiffSharpe',
                          'HF_VmL2HmVDiffStdRatio', 'HF_VmL2HmVStdRatio', 'HF_VolumeStdStrengthCloseChangePct', 'HF_VolumeStrengthCloseStdBias', 'HF_VolumeStrengthDeg1',
                          'HF_VolumeTopVwapRatio', 'HF_VwapAmtUpCorrInLowVolatility_13h', 'HF_VwapBollingUp_13h', 'HF_VwapLowCorrZscore_13h', 'HF_VwapRetSkew_13h',
                          'HF_VwapTailTopVolumeDiffRatio_13h', 'HF_VwapTailTurnRatioZscore', 'HF_VwapTailVolumeRatio_13h', 'HF_VwapTopTailAmtRatio_13h',
                          'HF_VwapTopTailTurnRatioZscore', 'HF_VwapTopTailVolume_13h', 'HF_VwapTopVolumeRatioZscore_13h', 'HF_WR2d', 'HLLength5', 'HLStd1mean', 'HLStdRatio',
                          'HLTR_mean5_intraday', 'HfHalfDayCloseRtnCountDiffBias_13h', 'HfHalfDayCloseRtnCountDiff_13h', 'HfLast120CloseVolumeStdCorrBias_13h',
                          'HfLast120HighLowDiffAmtCloseCorrDelta_13h', 'HfLast120HighLowDiffAmtCloseCorrPreBias', 'HfLast120HighLowDiffAmtCloseCorrSharpe',
                          'HfLast120LongTurnSkew_13h', 'HfLast120MaxRtnCloseCorrBias_13h', 'HfLast120MinRtnCloseCorrBias', 'HfLast120RtnPerAmtVolCorr',
                          'HfLast120RtnPerAmtVolPre1minCorr', 'HfLast120RtnStdCloseCorrBias', 'HfRtnPerAmtVolCorr', 'HfSwingCloseCorr', 'HfTopRtnVolumeRatioMean',
                          'HfVolClosePre5minCorr10d', 'High2LowVolDown', 'High2Low_1', 'High2Low_5', 'HighCloseDistance', 'HighFreqDownSpeed', 'HighFreqDrawBack',
                          'HighFreqDrawBackMeanBias', 'HighFreqRelativeClose', 'HighFreqRetRefStd', 'HighFreqSwingStdCmp', 'HighFreqTurnRetCorr', 'HighFreqWaveRetStd',
                          'HighLowHitFreqRatio', 'HighLowMeanVwapRetSharpe', 'HighLowStdBias20d', 'HighLowStdLowDistance10d', 'HighLowVwapRatio', 'HighSkew_Mean_5', 'HighTurnVwap',
                          'IdeaVL', 'IdeaVStd', 'IdealRev2', 'IdealSwingMin2D', 'IndustryExcessPVCorrBias5d', 'InflowOutflowDiff', 'InstitutionalVolumeRatio2min', 'L2C5',
                          'LargeSmallVolumeVWAPRatio', 'Last30MaxClimbBias20d', 'Last30MaxDrawdownBias20d', 'LatestRetRatio', 'LogAmt_1', 'LogAmt_5', 'LogFreeTurn_1',
                          'LogRtn2Amt5', 'LowHighRetStdRatio', 'LowHighStdRatio', 'LowSharpeAmountStdRatio', 'MACDNumDiffBeta_5_1', 'MACDNumDiffBeta_5_5', 'MACDNumDiffMean_1_1',
                          'MACDNumDiffMean_5_5', 'MACDNumDiff_5_5', 'MaxDrawDown', 'MeanRatio_min5', 'Min10ReUpLast5Min', 'Min1WeightedFlow_1', 'MinCapitalGainAutoCorr',
                          'MinCapitalGainOverhang', 'MinCapitalGainRH', 'MinCorrAbsRePriceRank2D', 'MinCorrExcessPriceRank', 'MinCorrVolumePrice_1', 'MinCorrVolumeRetUp_1',
                          'MinExtremRet', 'MinPVCorr', 'MinPrePVCorr', 'MinPrePriceAutoCorr', 'MinPrePriceRate', 'MinPriceAutoCorr', 'MinPriceBeta', 'MinUpDownVolRet',
                          'MinuteTVRtnRank', 'MinuteVolatilityPriceCorr', 'NewCorrHighVol', 'OverBuySellSkewRegbeta_5_5', 'OverBuySell_Mean_5', 'OverBuy_Mean_1', 'OverBuy_Sell_3',
                          'PDS', 'PDSS', 'PVRatioCorr', 'PriceRange_5', 'PriceSkew', 'PriceVolume_5', 'RSIMeanRegbeta_5_15', 'RSIMinMean_1_15', 'RSJT', 'RS_mean', 'RawAmtStdRatio',
                          'ReLow_13h', 'Ret30Mean2Std_10', 'Ret30RankMean_5', 'RetAdjVolMaxMean_1_5', 'RetAdjVolMaxRaw_1_1', 'RetAdjVolMeanRank_3_5', 'RetAdjVolMeanSr_1_5',
                          'RetAdjVolSkewMean_1_1', 'RetAdjVolSkewRaw_1_1', 'RetGather0p9mean5', 'RetMean_Rank', 'RetStd_Mean_1', 'RetToStd', 'RetToVolSke', 'RetUpWeightedByVolSR',
                          'RetVolCVMultiple', 'RetVolMaxRaw_1_5', 'RetVolMeanSr_1_1', 'RetVolMeanSr_5_1', 'RetVolSkewMean_1_5', 'RetVolSkewRaw_5_1', 'RevExclu4mean',
                          'RollingSignDownWick', 'Rsrs', 'SharpeDuringStdDrop', 'SignDownWick', 'SkewDuringAmountHike', 'Smartmoney_ret_mean_02_05_rolling1', 'SplitStdRatio',
                          'SplitVolumeRatio', 'StdUpDown', 'StructedRev5', 'TemporalVolumePriceCorr', 'TopAmountRatioVolumeDiffSharpe', 'TurnFree_3', 'TurnHighKurt',
                          'TurnHighSkew', 'TurnStdPure3mean', 'TurnWeiRet10slope', 'TurnWeiRet3max', 'TurnWeiRet3mean', 'TurnWeiRet3min', 'TurnWeiRet5max', 'TurnWeiRet5mean',
                          'TurnWeiRet5min', 'TwapSkewToVwap', 'UDContrast5mean', 'UpCountLowDistance10d', 'UpDownVolRatioStdRaw_1_1', 'UpDownVolRatioStdRegbeta_5_1',
                          'UpVolatilityRate', 'VWMidReurnSharpe5d', 'VarResampleMeanL', 'VolBurstReturn', 'VolGather0p9mean5', 'VolMeanSharpeUp2Down', 'VolaDownward20',
                          'VolumeDownChange_13h', 'VolumeMax10min2All_13h', 'VolumeStd_Mean_1', 'VolumeStd_Mean_5', 'VolumeUpPVCorr_13h', 'Vwap2Twap5mean', 'VwapAmtCorrMean5d_13h',
                          'VwapBollingerBand30min_13h', 'VwapBollingerBand_13h', 'VwapmaLowDiffSkew_13h', 'WAPResistBackTop_13h', 'WR2d_13h', 'WR_13h', 'WeightedFlow_1',
                          'WilliamUp_diffstd5', 'WilliamsIndicator_13h', 'adjEMAbc_intraday5', 'adjdmstdcpt_intraday_5', 'adjstdsd_intraday_5', 'adjstdstm_intraday_5',
                          'adjstdwms_intraday_5', 'cummaxdd_ntmaxstd_20_3', 'cummaxdd_nttrbmean_20_10', 'cummaxdd_nttrbmean_20_3', 'cummaxdd_nttrbskew_20_10', 'dailyms_intraday_5',
                          'dretvvolnew_ntmsmean_60_3', 'dretvvolnew_nttbskew_20_10', 'hfCPVCorrHD_13h', 'hfCPVCorrHDbias_13h', 'hfCPVCorrHDmean_13h', 'hfCapStdRatioMin', 'hfHVR5',
                          'hfHVRbias', 'hfHighVolPVcorr', 'hfHighVolPVcorr5', 'hfHighVolPVcorrbias', 'hfIdxCorr', 'hfLowCapRetMax', 'hfLowCapRetMin', 'hfMktLSCap', 'hfMktLSCapMR5',
                          'hfMktLSCapSR', 'hfPVcorrHD', 'hfTurnStdHD', 'hfUpPVcorr5', 'hfUpRRC', 'hfUpRRCbias', 'subrr2adjwms_intraday_5', 'subrradjwms_intraday_5', 'zhy_fix_5'],
    'XGB_D': lambda x: get_fix_factor_evaluation(400, x, 'ic_half_d'),
    'XGB_T': lambda x: get_fix_factor_evaluation(400, x, 'ic_half_t'),
    'XGB_C': lambda x: get_fix_factor_evaluation(400, x, 'ic_half_c'),
    'HX_D': lambda x: pd.read_pickle('/data/user/015836/HFmodel/share/robust.pkl').sort_values('ic_all_d', ascending=False).head(400)['name'].tolist(),
    'HX_T': lambda x: pd.read_pickle('/data/user/015836/HFmodel/share/robust.pkl').sort_values('ic_all_t', ascending=False).head(400)['name'].tolist(),
    'HX_C': lambda x: pd.read_pickle('/data/user/015836/HFmodel/share/robust.pkl').sort_values('ic_all_c', ascending=False).head(400)['name'].tolist(),
    'XGB_G':lambda x : pd.read_pickle(model_conf['XGB_G'].replace('.pkl','feature_path/%d.pkl'%x)),
    'XGB_W':lambda x : pd.read_pickle(model_conf['XGB_W'].replace('.pkl','feature_path/%d.pkl'%x)),
    'XGB_Cov':lambda x : pd.read_pickle(model_conf['XGB_Cov'].replace('.pkl','feature_path/%d.pkl'%x)),
}

model_load_func = {
    'XGB_D': lambda x: load_model_xgb(model_conf['XGB_D'].replace('.pkl', '_model_conf/%d.json' % x)),
    'XGB_T': lambda x: load_model_xgb(model_conf['XGB_T'].replace('.pkl', '_model_conf/%d.json' % x)),
    'XGB_C': lambda x: load_model_xgb(model_conf['XGB_C'].replace('.pkl', '_model_conf/%d.json' % x)),
    'Cat_T': lambda x : load_model_sklearn(model_conf['Cat_T'].replace('.pkl', '_model_conf/%d.pkl' % x)),
#    'Light_T': lambda x : load_model_sklearn(model_conf['Light_T'].replace('.pkl', '_model_conf/%d.pkl' % x)),
    'HX_D': lambda x : load_linear_v2(model_conf['HX_D'].replace('.pkl', '_model_conf/%d.h5' % x)),
    'HX_T': lambda x : load_linear_v2(model_conf['HX_T'].replace('.pkl', '_model_conf/%d.h5' % x)),
    'HX_C': lambda x : load_linear_v2(model_conf['HX_C'].replace('.pkl', '_model_conf/%d.h5' % x)),
    'XGB_G': lambda x: load_model_xgb(model_conf['XGB_G'].replace('.pkl', '_model_conf/%d.json' % x)),
    'XGB_W': lambda x: load_model_xgb(model_conf['XGB_W'].replace('.pkl', '_model_conf/%d.json' % x)),
    'XGB_Cov': lambda x: load_model_xgb(model_conf['XGB_Cov'].replace('.pkl', '_model_conf/%d.json' % x)),

}

def fit_model(i, output_path):
    path_dict = dict(
        res_path=output_path+'/',
        val_path=output_path[:-1] + '_val_pred_path/',
        model_conf_path=output_path[:-1] + '_model_conf/',
        feature_path=output_path[:-1] + '_feature_path/',
        base_model_res_path='/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_Cat_Light_base_model_res/',
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    train_start, train_end, test_start, test_end = para_list[i][1]
    if os.path.exists(path_dict['res_path']+'%d.pkl'%train_end):
        print(train_end,'exist')
        return
    features_map = {}
    features = set()
    for each in model_features:
        features_map[each] = model_features[each](train_end)
        features = features.union(set(features_map[each]))
    features = sorted(list(features))

    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [1, 3, 5, 7, 9]]

    if not os.path.exists(path_dict['base_model_res_path']+'%d.pkl'%train_end):
        dp = FixFactorRollPrepare(start_date=date_list[0], end_date=test_end, freq=7, model_time_len=1,
                                  factor_list=features, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
        X, y, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date_list[0], end_date=test_end, return_idx=True)
        X, y, idx_date, idx_time, idx_code = dp.feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
        indexes = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
        X, y = pd.DataFrame(X, index=indexes, columns=features), pd.DataFrame(y, index=indexes, columns=['actual_label'])
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        base_model_res = {}
        for each in model_load_func:
            temp_base_model = model_load_func[each](train_end)
            temp_features = features_map[each]
            if isinstance(temp_base_model,xgb.Booster):
                temp_base_model.set_param('predictor', 'cpu_predictor')
                base_model_res[each] = temp_base_model.predict(xgb.DMatrix(X[temp_features]))
            elif isinstance(temp_base_model,tf.keras.models.Model):
                base_model_res[each] = temp_base_model.predict(X[temp_features].values)[:,0]
            else:
                base_model_res[each] = temp_base_model.predict(X[temp_features])
            del temp_base_model
            gc.collect()

        base_model_res = pd.DataFrame(base_model_res,index=X.index)
        pd.to_pickle([base_model_res,y],path_dict['base_model_res_path']+'%d.pkl'%train_end)
    else:
        base_model_res, y = pd.read_pickle(path_dict['base_model_res_path']+'%d.pkl'%train_end)
        base_model_res = base_model_res[[['XGB_D', 'XGB_T', 'XGB_C', 'HX_D', 'HX_T', 'HX_C',
       'XGB_G', 'XGB_W', 'XGB_Cov']]]


    stack_linear = LinearRegression()
    stack_linear.fit(base_model_res.loc[date_list],y.loc[date_list])
    joblib.dump(stack_linear, path_dict['model_conf_path'] + '%d.pkl' % train_end)

    test_date_list = get_date_range(test_start,test_end)

    ##################
    # pred_test = base_model_res.loc[test_date_list]
    # test_re_prediction = {}
    # for each in model_conf:
    #     test_re_prediction[each] = pd.read_pickle(model_conf[each].replace('.pkl',f'/{train_end}.pkl'))#
    #     if each.startswith('HX'):
    #         test_re_prediction[each] = test_re_prediction[each].set_index(['date','time','code']).loc[pred_test.index,'y_hat']
    #     else:
    #         test_re_prediction[each] = test_re_prediction[each].loc[pred_test.index,'prediction']
    # test_re_prediction = pd.DataFrame(test_re_prediction)
    ##################

    y_val,y_test = y.loc[val_date_list],y.loc[test_date_list]
    y_val['prediction'] = stack_linear.predict(base_model_res.loc[val_date_list])
    y_test['prediction'] = stack_linear.predict(base_model_res.loc[test_date_list])
    pd.to_pickle(y_val, path_dict['val_path'] + '%d.pkl' % train_end)
    pd.to_pickle(y_test, path_dict['res_path'] + '%d.pkl' % train_end)
    print(train_end,y_test.corr())
    return True


out_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/XGB_DTCGWC_HX_RegIntegration/'

from xquant.compute.aimr import AIMR
idx_list = list(range(73))
#i= int(AIMR.getParam())
#idx_list = idx_list[len(idx_list)*i//7:len(idx_list)*(i+1)//7]

bar = tqdm(total=len(idx_list))

def update(*p):
    bar.update()
    if bar.last_print_n>=bar.total:
        bar.close()

from multiprocessing import Pool


pool = Pool(8)

for idx in idx_list:
    pool.apply_async(fit_model,(idx, out_path),callback=update)
    # fit_model(idx, out_path)
    # process = Process(target=fit_model, args=(idx, out_path))
    # process.start()
    # process.join()
    gc.collect()
pool.close()
pool.join()