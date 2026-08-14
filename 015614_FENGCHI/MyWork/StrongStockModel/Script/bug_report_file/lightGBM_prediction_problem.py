# @Time : 2021/3/19 10:47
# @Author : Zhichen Lu
# @File : lightGBM_prediction_problem.py

import pandas as pd
import xgboost as xgb
import os, gc, time, datetime
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
from sklearn.externals import joblib
import configparser
import tensorflow as tf
from tensorflow.python.ops import math_ops
from sklearn.linear_model import LinearRegression
from lightgbm.sklearn import LGBMRegressor

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

i = 52
train_start, train_end, test_start, test_end = para_list[i][1]
date_list = get_date_range(train_start, train_end)
val_date_list = [date_list[-i] for i in [1, 3, 5, 7, 9]]

features = ['AbnormalReturnPVCorrBias20d', 'AbnormalVolumePVCorr', 'AccelerateStd', 'AmountGrowthDuringLowRet', 'AmtStdStd5d', 'AmtStd_Mean_1', 'AmtStd_Mean_5',
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
            'hfMktLSCapSR', 'hfPVcorrHD', 'hfTurnStdHD', 'hfUpPVcorr5', 'hfUpRRC', 'hfUpRRCbias', 'subrr2adjwms_intraday_5', 'subrradjwms_intraday_5', 'zhy_fix_5']
dp = FixFactorRollPrepare(start_date=date_list[0], end_date=test_end, freq=7, model_time_len=1,
                          factor_list=features, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
X, y, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=date_list[0], end_date=test_end, return_idx=True)
X, y, idx_date, idx_time, idx_code = dp.feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
indexes = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))
X, y = pd.DataFrame(X, index=indexes, columns=features), pd.DataFrame(y, index=indexes, columns=['actual_label'])
date_list = sorted((list(set(date_list) - set(val_date_list))))
temp_base_model = joblib.load('/data/group/800319/wyl/model_record/lightgbm_record/lightgbmnew_ic_all_t_model_conf/%d.pkl' % train_end)
base_model_res = temp_base_model.predict(X)
