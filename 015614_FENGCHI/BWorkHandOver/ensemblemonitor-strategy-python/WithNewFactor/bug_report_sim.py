# @Time : 2021/8/10 18:03
# @Author : Zhichen Lu
# @File : bug_report.py
import pandas as pd
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
from FactorCalculator.RealTime import MinFactorCalculator
from dataApi.getData import trans_windcode2int

bar_list = [1000,1030,1100,1300,1330,1400,1430]
def compare_factor(date,local_config_path):

    fix_online_df, min5_online_df = [], []
    for time_point in bar_list:
        bar_factor = pd.read_pickle(f'{local_config_path}/daily_output/{date}/factor_{time_point}.pkl')
        fix_online_df.append(bar_factor['fix'].rename(index={x: (trans_windcode2int(x), time_point) for x in bar_factor['fix'].index}))
        min5_online_df.append(bar_factor['5min'].rename(index={x: (trans_windcode2int(x), time_point) for x in bar_factor['5min'].index}))
    fix_online_df, min5_online_df = pd.concat(fix_online_df), pd.concat(min5_online_df)
    fix_online_df.index = pd.MultiIndex.from_tuples(fix_online_df.index.tolist())
    min5_online_df.index = pd.MultiIndex.from_tuples(min5_online_df.index.tolist())
    return fix_online_df, min5_online_df

def get_factor_5min_online(date):
    mfc = MinFactorCalculator(date)
    factor = {}
    for bar in [1000,1030,1100,1130,1330,1400,1430]:
        mfc.calc_bar_data(bar,0,threads=10)
        if bar==1130:
            bar[1300] = mfc.factor.copy()
        else:
            factor[bar] = mfc.factor.copy()
    return factor

# factor = get_factor_5min_online(20210802)


# fix_factor_list = ['AbnormalReturnPVCorrBias20d', 'AbnormalVolumePVCorr', 'AbsRet30Mean_5', 'AccelerateStd', 'AccelerateStdRE_std10', 'AggressionNMean_3_5',
#                    'AmountGrowthDuringLowRet', 'AmountMktDiff', 'AmtPcg_regrmse', 'AmtRatio_Mean_5', 'AmtSkew3', 'AmtStdRet_mean10', 'AmtStdStd5d', 'AmtStd_Mean_1',
#                    'AmtStd_Mean_5', 'AmtStd_Std_5', 'AvgClose2Vwap_Std_5', 'AvgPriceVwapRateStd5d', 'AvgStdRatioRE_regrmse10', 'AvgStdRatio_max5', 'AvgStdRatio_mean5',
#                    'AvgStdRatio_min5', 'BAStrength', 'BI500Std5', 'BestWorstReSharpe5d', 'Beta300', 'Beta500d3', 'BiasStd3_5Std', 'BigSmallRetCloseDiff3_trans0p25',
#                    'BotTopCumSwingStdRatio', 'BottomTopPriceSwingRatio', 'CGO', 'CRCS_raw_rank_ms10', 'CRCS_raw_rank_skew10', 'CSAD5mean', 'CSAD5std', 'Close2BarHigh',
#                    'Close2High', 'CloseCorrVolume_5', 'CloseExcessPercent_1', 'CloseOneOrderTwoOrder', 'CloseSkew_Mean_5', 'CloseVolumeCorrBias20d', 'CloseVwapRetKurt',
#                    'CloseVwapRetSkew', 'ConsRetStd3std', 'Cor300Up5mean', 'Cor500D3', 'CorAmtMeanMean5', 'CorAmtMeanSKew5', 'CorAmtStdSKew5', 'CorAmtStdStd5', 'CorPV5',
#                    'CorrAmpRet_5', 'CorrAmpVwap_1', 'CorrAmpVwap_5', 'CorrCloseVol_Mean2DStd_5', 'CorrCloseVol_Mean_1', 'CorrCloseVol_Mean_5', 'CorrDelVolumePriceMean',
#                    'CorrHighLowAvgToAmt_Mean_1', 'CorrHighLowAvgToAmt_Mean_5', 'CorrHighVol', 'CorrLowVol_mean5', 'CorrMaxRePriceRank', 'CorrPVLowLiquidity',
#                    'CorrRankCloseVolume_5', 'CorrRankOpenVolume_10', 'CorrResisVWAP', 'CorrRetVol_5', 'CorrVWAPdt', 'CorrVWAPstd', 'CorrVolumePriceRankSharpe',
#                    'CorrVwapCVPriceLast60', 'CorrVwapVol_1', 'CorrVwapVol_5', 'CorrWRPriceRank', 'CumPVRatioCorr', 'CyqHhi', 'DIFMaxPct_1_5', 'DIFMaxRaw_1_5', 'DIFMeanRaw_5_30',
#                    'DIFMeanRaw_5_5', 'DIFMeanRegbeta_5_30', 'DIFMeanSr_5_5', 'DIFSkewRank_5_1', 'DisNMean_1', 'DisNMean_5', 'DisNRaw_5', 'DisNSkew_5', 'DisNStd_1', 'DisPMean_5',
#                    'DisPRaw_5', 'DisPRegbeta_5', 'DisPSr_5', 'DisPStd_1', 'DivergWinLossRDifStd_1_5', 'DivergWinLossRKurtRegrmse_5_5', 'DivergWinLossRMeanRank_5_5',
#                    'DivergWinLossRMinStd_1_5', 'DivergWinLossRSkewRegrmse_5_5', 'DivergWinLossRStdRegrmse_1_5', 'DivergWinLossRStdRegrmse_5_5', 'DivergWinLossRStdStd_5_15',
#                    'DrawdownSkew', 'EVolChgBetaAbs_1_1', 'EVolChgStd_5_5', 'Excess300High5', 'Excess500High5', 'FIX_lly_8', 'FWRMin', 'FactorAlpha007', 'FactorAlpha024',
#                    'FactorAlpha027', 'FactorMin10_meandivstd', 'FactorMin117_mean', 'FactorMin118_mean', 'FactorMin118_meandivstd', 'FactorMin124_diff', 'FactorMin129_diff',
#                    'FactorMin137_mean', 'FactorMin13_diff', 'FactorMin13_diffdivstd', 'FactorMin13_mean', 'FactorMin14_diff', 'FactorMin150_diff', 'FactorMin150_mean',
#                    'FactorMin155_mean', 'FactorMin155_meandivstd', 'FactorMin157_diff', 'FactorMin157_diffdivstd', 'FactorMin157_mean', 'FactorMin157_meandivstd',
#                    'FactorMin15_mean', 'FactorMin160_mean', 'FactorMin168_std', 'FactorMin18_meandivstd', 'FactorMin193_mean_re', 'FactorMin199_meandivstd',
#                    'FactorMin1_diff_div_std', 'FactorMin1_mean', 'FactorMin201_mean', 'FactorMin215_mean', 'FactorMin215_meandivstd', 'FactorMin217_mean_re', 'FactorMin235_std',
#                    'FactorMin236_std', 'FactorMin26_mean', 'FactorMin285_self_re', 'FactorMin289_mean_re', 'FactorMin28_mean', 'FactorMin33_mean', 'FactorMin33_std',
#                    'FactorMin343_mean_re', 'FactorMin343_self_re', 'FactorMin353_std_re', 'FactorMin35_diff', 'FactorMin35_mean', 'FactorMin370_std_re',
#                    'FactorMin383_mean_div_std_re', 'FactorMin403_mean_div_std_re', 'FactorMin403_mean_re', 'FactorMin405_mean_div_std_re', 'FactorMin412_mean_div_std_re',
#                    'FactorMin417_std_re', 'FactorMin42_mean', 'FactorMin430_mean_div_std_re', 'FactorMin43_std', 'FactorMin450_mean_re', 'FactorMin453_std_re', 'FactorMin45_std',
#                    'FactorMin66_mean', 'FactorMin70_diff', 'FactorMin70_mean', 'FactorMin80_diff', 'FactorMin81_diff_div_std', 'FactorMin81_mean', 'FactorMin87_diff',
#                    'FactorMin87_mean_div_std', 'FactorMin89_diff', 'FactorMin89_std', 'FactorMin8_mean', 'FactorMin93_diff', 'FactorMin94_mean', 'FactorMin95_mean',
#                    'FactorMinKdayShortCut_std', 'FactorMinVaR_regrmse_05_10', 'Factor_Fix_zhy_101', 'Factor_Fix_zhy_15', 'FreeTurn_Mean2Std_5', 'FreeTurn_Mean_1',
#                    'FreeTurn_Mean_5', 'FreeTurn_Std_5', 'GDZQ4std3', 'GTJA14_std5', 'GTJA16_max5', 'GTJA17_bias5', 'GTJA1_6', 'GTJA2', 'GTJA20_std5', 'GTJA27_max12',
#                    'GTJA27_weight12', 'GTJA32', 'GTJA40', 'GTJA41', 'GTJA43', 'GTJA43_min5', 'GTJA48', 'GTJA5', 'GTJA53_ts_rank5', 'GTJA54G', 'GTJA54_N', 'GTJA62', 'GTJA7_mean5',
#                    'GTJA8', 'GTJA8_mean5', 'HFPSCorr', 'HFPTSCorrBias', 'HFPTSCorrMinAdj', 'HFPTSCorrStdAdj', 'HFPVCorr', 'HFPVCorrBias', 'HFPVCorrStdAdj',
#                    'HF_5mRePosVolVolatilityStable', 'HF_Amt10mSkew20d', 'HF_AmtDeg1', 'HF_AmtStdStrengthCloseBias', 'HF_AmtStdStrengthCloseChange_13h', 'HF_AmtStdStrengthDev_13h',
#                    'HF_AmtStrengthCloseChange_13h', 'HF_AmtVolatilityPriceCorr5D_13h', 'HF_AmtVolatilityPriceCorr_13h', 'HF_CMExcessRetWeightSkew_13h',
#                    'HF_CloseLowHighStdVolumeRatio_13h', 'HF_CorrBuyStrength_13h', 'HF_CorrMaxVolumeZScore_13h', 'HF_DVwapDVolumeCorrZscore_13h', 'HF_ForecastEPDelta40d',
#                    'HF_HighPinZscore_13h', 'HF_HighVwapSkew_13h', 'HF_Hl2OStrength_13h', 'HF_HmL2CVwapCorrZscore_13h', 'HF_HmL2CVwapCorr_13h', 'HF_LinearDiffStdRatio_13h',
#                    'HF_LinearHighDiffSkew_13h', 'HF_LowReBiasSelfCorrStable_13h', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h',
#                    'HF_MeanIntradayReturnAcrossProfitableInvestors_13h', 'HF_NormRePriceCorrSharpe_13h', 'HF_OpenVwapSkew', 'HF_OverBuy', 'HF_OverBuySell_13h', 'HF_PriceDiffRatio',
#                    'HF_PriceDiffStdRatio', 'HF_PriceVolIndustryDelta', 'HF_RSRS', 'HF_RSRSZScore', 'HF_RetHHIZscore', 'HF_RetTopVwapAmtCorrBias', 'HF_ReverseVolRatioVWAP',
#                    'HF_Shortcut2CloseCloseCorrZscore', 'HF_TurnoverrateStd', 'HF_TwapRetWeightSkew', 'HF_UpReaturnRealStdZScore', 'HF_UpRetTurnDiffSharpe',
#                    'HF_VmL2HmVDiffStdRatio', 'HF_VmL2HmVStdRatio', 'HF_VolumeSharpe', 'HF_VolumeStdStrengthCloseChangePct', 'HF_VolumeStrengthDeg1', 'HF_VolumeTopVwapRatio',
#                    'HF_VwapAmtUpCorrInLowVolatility_13h', 'HF_VwapBollingUp_13h', 'HF_VwapLowCorrZscore_13h', 'HF_VwapRetSkew_13h', 'HF_VwapTailTopTRRatio_13h',
#                    'HF_VwapTailTopVolumeDiffRatio_13h', 'HF_VwapTailTurnRatioZscore', 'HF_VwapTailVolumeRatio_13h', 'HF_VwapTopTRRatio_13h', 'HF_VwapTopTailAmtRatio_13h',
#                    'HF_VwapTopTailTurnRatioZscore', 'HF_VwapTopTailVolumeStdRatio_13h', 'HF_VwapTopTailVolume_13h', 'HF_VwapTopVolumeRatioZscore_13h', 'HF_WR2d', 'HLLength5',
#                    'HLStd1mean', 'HLStdRatio', 'HLStdRatio_max5', 'HLStdRatio_min5', 'HLTR_mean5_intraday', 'HfAmtSpaceSkewMean_13h', 'HfHalfDayCloseRtnCountDiffBias_13h',
#                    'HfHalfDayCloseRtnCountDiff_13h', 'HfLast120CloseVolumeStdCorrBias_13h', 'HfLast120HighLowDiffAmtCloseCorrDelta_13h', 'HfLast120HighLowDiffAmtCloseCorrPreBias',
#                    'HfLast120HighLowDiffAmtCloseCorrSharpe', 'HfLast120MaxRtnCloseCorrBias_13h', 'HfLast120MinRtnCloseCorrBias', 'HfLast120RtnPerAmtVolCorr',
#                    'HfLast120RtnPerAmtVolPre1minCorr', 'HfLast120RtnStdCloseCorrBias', 'HfSwingCloseCorr', 'HfTopRtnVolumeRatioMean', 'HfTurnMaSkew', 'HfVolClosePre5minCorr10d',
#                    'HfVolSkew', 'High2LowVolDown', 'High2Low_1', 'High2Low_5', 'HighCloseDistance', 'HighFreqDownSpeed', 'HighFreqDrawBack', 'HighFreqDrawBackMeanBias',
#                    'HighFreqDrawBackStdBias', 'HighFreqRelativeClose', 'HighFreqRetRefStd', 'HighFreqSwingStdCmp', 'HighFreqTurnRetCorr', 'HighFreqWaveRetStd',
#                    'HighLowHitFreqRatio', 'HighLowMeanVwapRetSharpe', 'HighLowStdBias20d', 'HighLowStdLowDistance10d', 'HighLowVwapDiffStdRatio', 'HighLowVwapRatio',
#                    'HighSkew_Mean_5', 'HighTurnVwap', 'IdeaVStd', 'IdeaVStdMax', 'IdeaVStdReg', 'IdealRev2', 'IdealSwingMin2D', 'IndustryExcessPVCorrBias5d',
#                    'IndustryExcessReturnStd5d', 'InstitutionalVolumeRatio2min', 'L2C5', 'LargeSmallVolumeVWAPRatio', 'Last30MaxClimbBias20d', 'Last30MaxDrawdownBias20d',
#                    'LatestRetRatio', 'LogAmt_1', 'LogAmt_5', 'LogDeltaVol', 'LogFreeTurn_1', 'LogRtn2Amt5', 'LowHighRetStdRatio', 'LowHighStdRatio', 'LowSharpeAmountStdRatio',
#                    'LowStdRatio_max5', 'MACDEChgStd_5_1', 'MACDNumDiffBeta_5_1', 'MACDNumDiffBeta_5_5', 'MACDNumDiffMean_1_1', 'MACDNumDiffMean_5_5', 'MACDNumDiff_5_5',
#                    'MaVolDistance10', 'MaxAmtStdRatio', 'MaxDrawDown', 'MeanRatio_min5', 'Min10ReUpLast5Min', 'Min1WeightedFlow_1', 'Min1WeightedFlow_5', 'MinCapitalGainAutoCorr',
#                    'MinCapitalGainBetaEwm', 'MinCapitalGainBetaZscore', 'MinCapitalGainOverhang', 'MinCapitalGainRH', 'MinCorrAbsRePriceRank2D', 'MinCorrExcessPriceRank',
#                    'MinCorrVolumePrice_1', 'MinCorrVolumeRetUp_1', 'MinDirectedVol', 'MinExtremRet', 'MinMaxRet', 'MinPVCorr', 'MinPrePVCorr', 'MinPrePriceAutoCorr',
#                    'MinPrePriceRate', 'MinPreVolRet', 'MinPriceAutoCorr', 'MinPriceBeta', 'MinUpDownVolRet', 'MinVRCExcess_13h', 'MinVwapHLRateBetaBias', 'MinVwapHLRateBetaDelta',
#                    'MinuteTVRtnRank', 'MinuteVolatilityPriceCorr', 'NetworkDegree3Net', 'NetworkPremium3', 'NewCorrHighVol', 'OpenDivClose_5', 'OverBuySellSkewRegbeta_5_5',
#                    'OverBuySell_Mean_5', 'OverBuy_Mean_1', 'OverBuy_Mean_5', 'OverBuy_Sell_3', 'OverflowPerAmtMean5d', 'PDS', 'PDSS', 'PVRatioCorr', 'PVSwingCorr',
#                    'PriceDeviationBias10d', 'PriceMktDiff', 'PriceRange_5', 'PriceSkew', 'PriceVolume_5', 'RSIMeanRegbeta_5_15', 'RSIMinMean_1_15', 'RSJT', 'RSRS_Mean_1',
#                    'RS_mean', 'RawAmtStdRatio', 'ReLow_13h', 'Ret30Mean2Std_10', 'Ret30RankMean_5', 'RetAdjVolDifStd_1_1', 'RetAdjVolMaxMean_1_5', 'RetAdjVolMaxRaw_1_1',
#                    'RetAdjVolMeanRank_3_5', 'RetAdjVolMeanRegrmse_1_1', 'RetAdjVolMeanSr_1_5', 'RetAdjVolSkewMean_1_1', 'RetAdjVolSkewRaw_1_1', 'RetAdjVolStdRegrmse_3_5',
#                    'RetAdjVolStdRegrmse_5_1', 'RetBigStdResAmt5', 'RetGather0p9mean5', 'RetMean_Rank', 'RetStd_Mean_1', 'RetStd_Mean_5', 'RetToStd', 'RetToVolSke', 'RetToVolabs',
#                    'RetUpWeightedByVolSR', 'RetVolCVMultiple', 'RetVolMaxRaw_1_5', 'RetVolMeanSr_1_1', 'RetVolMeanSr_5_1', 'RetVolSkewMean_1_5', 'RetVolSkewRaw_5_1',
#                    'RevExclu4mean', 'RollingCloseOpenWeightedCorr_10', 'RollingCloseOpenWeightedCorr_5', 'RollingSignDownWick', 'Rsrs', 'SharpeDuringStdDrop', 'ShortTurn',
#                    'SignDownWick', 'SkewDuringAmountHike', 'SkewUpDown', 'Smartmoney_close_max0505_rolling1', 'Smartmoney_close_max0505_rolling3',
#                    'Smartmoney_close_max_005_05_rolling3', 'Smartmoney_close_max_02_05_rolling1', 'Smartmoney_hlratio_max_02_05_rolling3', 'Smartmoney_hlratio_max_05_05_rolling1',
#                    'Smartmoney_ret_mean_02_05_rolling1', 'Smartmoney_ret_min_02_05_rolling3', 'SplitStdRatio', 'SplitVolumeRatio', 'StableRet20', 'StableVol20', 'StableVol5',
#                    'StdMaxAmountRatio', 'StdRatio_min5', 'StdUpDown', 'StructedRev5', 'SwingPriceCorr', 'SwingReturn', 'TemporalVolumePriceCorr', 'TopAmountRatioVolumeDiffSharpe',
#                    'TurnFree_3', 'TurnHighKurt', 'TurnHighSkew', 'TurnHighStd_meandivstd', 'TurnStdPure3mean', 'TurnStdPure5std', 'TurnVolatilityStd5d', 'TurnWeiRet10slope',
#                    'TurnWeiRet3max', 'TurnWeiRet3mean', 'TurnWeiRet3min', 'TurnWeiRet5max', 'TurnWeiRet5mean', 'TurnWeiRet5min', 'TwapSkewToVwap', 'UDContrast5mean',
#                    'UpCountLowDistance10d', 'UpDownAmtRatioStdRegrmse_5_5', 'UpDownVolRatioStdRaw_1_1', 'UpDownVolRatioStdRegbeta_5_1', 'UpToRetValue', 'UpVolatilityRate',
#                    'UpVolatilityRateStd5d', 'VWMidReurnSharpe5d', 'VarResampleMeanL', 'VarResampleMean_max10', 'VolBurstReturn', 'VolCorr', 'VolGather0p9mean5',
#                    'VolMeanSharpeUp2Down', 'VolMeanSharpeUp_13h', 'VolSkew', 'VolaDownward20', 'VolaRatio10Mean', 'VolaRatio5Std', 'VolumeDownChange_13h', 'VolumeMax10min2All_13h',
#                    'VolumeStd_Mean_1', 'VolumeStd_Mean_5', 'VolumeStd_Std_5', 'VolumeUpPVCorr_13h', 'Vwap2Twap5mean', 'VwapAmtCorrMean5d_13h', 'VwapBollingerBand30min_13h',
#                    'VwapBollingerBand_13h', 'VwapStdCorrBias20d_13h', 'VwapStdCorrDistanceLow10d_13h', 'VwapStdRatio_max5', 'VwapStdRatio_mean5', 'VwapStdRatio_min5',
#                    'VwapSwingCorr', 'VwapmaLowDiffSkew_13h', 'WAPResistBackTop_13h', 'WR2d_13h', 'WRMean5d_13h', 'WR_13h', 'WeightedFlow_1', 'WeightedFlow_5', 'WilliamUp_diffstd5',
#                    'WilliamsIndicator_13h', 'WilliamsPriceVolCorrMultiple_13h', 'adjEMAbc_intraday5', 'adjdmstdcpt_intraday_5', 'adjstdsd_intraday_5', 'adjstdstm_intraday_5',
#                    'adjstdwms_intraday_5', 'amtavg_mktstate_amt_std_topskew_5_3', 'amtavg_mktstate_ret_topskew_5_3', 'amtavg_ntmeankurt_20_10', 'amtavg_ntmeanskew_60_10',
#                    'cummaxdd_ntmaxstd_20_3', 'cummaxdd_nttrbmean_20_10', 'cummaxdd_nttrbmean_20_3', 'cummaxdd_nttrbskew_20_10', 'dailyms_intraday_5', 'dretvolnew_ntdmstd_60_10',
#                    'dretvolnew_ntmeanskew_20_10', 'dretvolnew_ntminstd_20_10', 'dretvvolnew_ntmeanskew_60_10', 'dretvvolnew_ntmsmean_60_3', 'dretvvolnew_nttbskew_20_10',
#                    'hfCPVCorrHD_13h', 'hfCPVCorrHDbias_13h', 'hfCPVCorrHDmean_13h', 'hfCapStdRatioMin', 'hfDownPVcorrbias', 'hfDownStrength', 'hfHVR5', 'hfHVRbias',
#                    'hfHighVolPVcorr', 'hfHighVolPVcorr5', 'hfHighVolPVcorrbias', 'hfIdxCorr', 'hfIdxCorr5', 'hfLowCapRetMax', 'hfLowCapRetMin', 'hfMktLSCap', 'hfMktLSCapMR5',
#                    'hfMktLSCapSR', 'hfPVcorrHD', 'hfRST', 'hfTurnStdHD', 'hfUBstd', 'hfUpPVcorr5', 'hfUpRRC', 'hfUpRRCbias', 'sistdwfiavg2_3_re', 'sistdwfiavg_re',
#                    'subrr2adjwms_intraday_5', 'subrradjwms_intraday_5', 'uretvolnew_ntdmstd_20_10', 'uretvolnew_ntmaxstd_60_10', 'uretvvolnew_ntmsmean_60_10',
#                    'uretvvolnew_ntmstb_60_10', 'zhy_fix_112', 'zhy_fix_146', 'zhy_fix_5', 'zhy_fix_73']

# code_list = [9, 12, 36, 59, 63, 153, 155, 301, 403, 422, 504, 516, 554, 560, 567, 568, 596, 615, 625, 633, 636, 661, 666, 678, 683, 691, 692, 702, 739, 762, 799, 807, 818, 821,
#              828, 830, 848, 858, 862, 875, 892, 893, 906, 915, 918, 923, 933, 936, 959, 996, 1965, 2010, 2025, 2026, 2028, 2036, 2045, 2049, 2050, 2062, 2066, 2074, 2080, 2109,
#              2116, 2125, 2126, 2129, 2135, 2139, 2141, 2154, 2169, 2179, 2191, 2193, 2198, 2201, 2206, 2223, 2240, 2245, 2250, 2274, 2282, 2291, 2292, 2304, 2309, 2311, 2312, 2313,
#              2326, 2344, 2353, 2377, 2386, 2408, 2409, 2416, 2418, 2430, 2436, 2438, 2448, 2459, 2460, 2472, 2484, 2497, 2517, 2518, 2539, 2541, 2556, 2559, 2563, 2566, 2568, 2571,
#              2585, 2594, 2597, 2598, 2614, 2623, 2625, 2627, 2633, 2636, 2637, 2642, 2643, 2644, 2645, 2648, 2651, 2667, 2675, 2676, 2685, 2691, 2709, 2715, 2723, 2724, 2727, 2728,
#              2729, 2732, 2738, 2739, 2741, 2747, 2753, 2756, 2760, 2763, 2769, 2780, 2785, 2790, 2791, 2812, 2817, 2821, 2824, 2830, 2843, 2850, 2851, 2856, 2860, 2866, 2871, 2873,
#              2876, 2877, 2883, 2890, 2891, 2895, 2896, 2899, 2906, 2912, 2913, 2922, 2932, 2949, 2957, 2960, 2967, 2968, 2975, 2979, 2985, 300001, 300005, 300014, 300015, 300034,
#              300035, 300039, 300045, 300049, 300054, 300069, 300073, 300079, 300080, 300081, 300091, 300092, 300093, 300101, 300113, 300119, 300121, 300122, 300125, 300138, 300142,
#              300143, 300144, 300150, 300158, 300166, 300171, 300182, 300183, 300191, 300196, 300207, 300211, 300233, 300244, 300252, 300256, 300262, 300266, 300274, 300279, 300294,
#              300295, 300298, 300305, 300316, 300319, 300324, 300327, 300335, 300344, 300346, 300354, 300358, 300363, 300365, 300366, 300369, 300373, 300374, 300375, 300377, 300378,
#              300379, 300382, 300384, 300385, 300390, 300391, 300394, 300395, 300404, 300408, 300409, 300410, 300413, 300415, 300421, 300430, 300438, 300440, 300447, 300450, 300451,
#              300452, 300453, 300454, 300456, 300457, 300458, 300470, 300472, 300474, 300482, 300487, 300490, 300493, 300496, 300497, 300505, 300508, 300517, 300529, 300535, 300548,
#              300555, 300557, 300558, 300567, 300568, 300570, 300573, 300577, 300585, 300586, 300587, 300590, 300593, 300601, 300604, 300612, 300620, 300621, 300623, 300626, 300628,
#              300630, 300633, 300635, 300638, 300642, 300643, 300650, 300652, 300653, 300654, 300655, 300656, 300661, 300662, 300668, 300671, 300672, 300673, 300680, 300681, 300685,
#              300687, 300691, 300693, 300696, 300698, 300700, 300705, 300707, 300708, 300710, 300712, 300717, 300718, 300724, 300725, 300726, 300731, 300733, 300736, 300745, 300747,
#              300748, 300750, 300751, 300756, 300759, 300760, 300762, 300763, 300767, 300768, 300769, 300772, 300776, 300779, 300782, 300785, 300788, 300789, 300790, 300792, 300796,
#              300802, 300803, 300811, 300816, 300820, 300823, 300824, 300826, 300829, 600007, 600038, 600055, 600058, 600060, 600079, 600089, 600096, 600110, 600111, 600119, 600129,
#              600132, 600141, 600161, 600163, 600173, 600184, 600188, 600193, 600197, 600201, 600234, 600248, 600251, 600261, 600262, 600285, 600288, 600305, 600307, 600315, 600318,
#              600335, 600338, 600375, 600392, 600399, 600409, 600418, 600422, 600426, 600428, 600436, 600438, 600452, 600456, 600460, 600461, 600463, 600478, 600483, 600486, 600525,
#              600538, 600543, 600549, 600563, 600569, 600582, 600586, 600587, 600596, 600600, 600641, 600645, 600647, 600660, 600688, 600699, 600725, 600729, 600736, 600741, 600746,
#              600763, 600765, 600773, 600777, 600779, 600800, 600809, 600830, 600847, 600862, 600869, 600876, 600882, 600884, 600885, 600933, 600958, 600963, 600976, 600993, 600997,
#              601001, 601012, 601021, 601101, 601127, 601238, 601336, 601339, 601377, 601518, 601566, 601579, 601595, 601600, 601633, 601636, 601666, 601689, 601699, 601799, 601827,
#              601838, 601865, 601882, 601886, 601888, 601908, 601918, 601919, 603005, 603008, 603020, 603026, 603027, 603068, 603076, 603083, 603089, 603096, 603100, 603101, 603108,
#              603113, 603127, 603129, 603177, 603180, 603181, 603185, 603186, 603195, 603217, 603223, 603229, 603233, 603236, 603259, 603260, 603267, 603286, 603289, 603290, 603297,
#              603300, 603303, 603308, 603315, 603323, 603337, 603345, 603356, 603358, 603380, 603388, 603389, 603392, 603396, 603416, 603444, 603456, 603466, 603477, 603486, 603489,
#              603501, 603505, 603516, 603517, 603538, 603551, 603558, 603566, 603569, 603579, 603587, 603588, 603589, 603596, 603599, 603605, 603613, 603626, 603650, 603657, 603659,
#              603667, 603678, 603681, 603685, 603690, 603713, 603717, 603733, 603767, 603799, 603800, 603809, 603811, 603816, 603822, 603829, 603833, 603843, 603867, 603877, 603882,
#              603893, 603897, 603899, 603901, 603906, 603908, 603909, 603915, 603926, 603937, 603956, 603959, 603960, 603969, 603986, 603991, 603995, 605168]

# factor_online = mfc.factor.T[min5_factor_list].copy()

#

def compare(start,end,check_date):

    local_config_path = '/data/group/800442/800319/strategy_local_path_sim/strategy_local_path3/'  # path_conf['local_config_path']
    min5_factor_list = pd.read_pickle(f'{local_config_path}/using_5min_list.pkl')
    desample_factor_list = []#pd.read_pickle(f'/data/group/800442/800319/strategy_HFfactor2/{check_date}/DateCode/desample_factor_list.pkl')
    desample_factor_path = '/arch1/group/800442/800319/MinFactor/FactorDpFixData/Factor/'
    desample_factor_list = [x[0][2:] for x in desample_factor_list]
    desample_factor_list = [x[0][2:] for x in desample_factor_list]

    X_fix_online, X_5min_online = compare_factor(check_date,local_config_path)
    fix_factor_list = X_fix_online.columns.tolist()
    X_5min_online = X_5min_online[min5_factor_list]
    code_list = sorted(list(set(x[0] for x in X_5min_online.index)))
    X_5min, y_5min, nolimit_5min, idx_date_5min, idx_code_5min, idx_time_5min = load_fix_data(start_date=start, end_date=end, factor_list=min5_factor_list,
                                                                                              address='/arch1/group/800442/800319/MinFactor/FactorFixData/Factor/')
    X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix = load_fix_data(start_date=start, end_date=end, factor_list=fix_factor_list)

    # X_desample, y_desample, nolimit_desample, idx_date_desample, idx_code_desample, idx_time_desample = load_fix_data(start_date=start, end_date=end, factor_list=desample_factor_list,
    #                                                                                           address=desample_factor_path)

    X_fix, y_fix, idx_date_fix, idx_code_fix, idx_time_fix = feature_engineering(X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix,limit=1)
    X_5min, y_5min, idx_date_5min, idx_code_5min, idx_time_5min = feature_engineering(X_5min, y_5min, nolimit_fix, idx_date_5min, idx_code_5min, idx_time_5min,limit=1)
    # X_desample, y_desample, idx_date_desample, idx_code_desample, idx_time_desample = feature_engineering(X_desample, y_desample, nolimit_fix, idx_date_desample, idx_code_desample, idx_time_desample,limit=1)

    index_fix = pd.MultiIndex.from_tuples(list(zip(idx_date_fix, idx_code_fix, idx_time_fix)))
    index_5min = pd.MultiIndex.from_tuples(list(zip(idx_date_5min, idx_code_5min, idx_time_5min)))
    # index_desample = pd.MultiIndex.from_tuples(list(zip(idx_date_desample, idx_code_desample, idx_time_desample)))

    X_fix = pd.DataFrame(X_fix, index=index_fix, columns=fix_factor_list)
    X_5min = pd.DataFrame(X_5min, index=index_5min, columns=min5_factor_list)
    # X_desample = pd.DataFrame(X_desample, index=index_desample, columns=desample_factor_list)

    X_fix_offline = X_fix.loc[check_date].loc[code_list]
    X_5min_offline = X_5min.loc[check_date].loc[code_list]
    # X_desample_offline = X_desample.loc[check_date].loc[code_list]
    # X_desample_offline.columns = X_desample_offline.columns.map(lambda x : f'M5{x}')
    # X_5min_offline = pd.concat([X_5min_offline,X_desample_offline],axis=1)



    if check_date<=20210813:
        factor_direction = pd.read_pickle('/data/group/800319/strategy_local_path3_ForMix20210715/factor_direction.pkl')
        X_fix_offline = X_fix_offline * factor_direction.loc[X_fix_offline.columns]

    # X_5min_online.columns = [x[2:] for x in X_5min_online.columns]
    set(X_5min_offline.columns) - set(X_5min_online.columns)


    fix_eval = pd.DataFrame(dict(
        mae=abs(X_fix_online - X_fix_offline).mean(),
        corr=X_fix_online.corrwith(X_fix_offline)
    ))

    min_5_eval = pd.DataFrame(dict(
        mae=abs(X_5min_online - X_5min_offline).mean(),
        corr=X_5min_online.corrwith(X_5min_offline)
    ))

    return fix_eval,min_5_eval
# start = 20210813
# end = 20210824

from dataApi.tradeDate import get_date_range

# check_date = 20210818
fix_compare,min5_compare = {},{}
for day in get_date_range(20210818,20210825):
    fix_compare[day],min5_compare[day] = compare(20210813,20210824,day)

fix_compare,min5_compare = pd.Panel(fix_compare),pd.Panel(min5_compare)


fix_compare.minor_xs('mae')

with pd.ExcelWriter('./仿真期间差异统计.xlsx') as wirter:
    fix_compare.mean().to_excel(wirter,sheet_name='FIX综合')
    min5_compare.mean().to_excel(wirter,sheet_name='5min综合')
    for each in min5_compare.minor_axis:
        min5_compare.minor_xs(each).to_excel(wirter,sheet_name='5min'+each)
    for each in fix_compare.minor_axis:
        fix_compare.minor_xs(each).to_excel(wirter,sheet_name='FIX'+each)

wirter.close()

from dataApi.sendInfo import send_file

send_file(['015664'],'./仿真期间差异统计.xlsx')

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor',
#                  '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel',
#                  '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
#                  '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading'])

import os
import pandas as pd

offline_path = '/data/group/800442/simulate_data/%d/%d/stock/'
realtime_data_path =  '/data/group/800442/realtime_data/%d/%d/stock/'

factor_list = ['buyorderamt.pkl', 'buyordervol.pkl', 'high.pkl', 'activebuyorderamt.pkl', 'accamountbuy.pkl', 'selltradeamt.pkl', 'passivesellorderamt.pkl', 'numtrade.pkl', 'activebuyordervol.pkl', 'volume_adj.pkl', 'activesellordervol.pkl', 'limit_status.pkl', 'selltradevol.pkl', 'sellordervol.pkl', 'accamountsell.pkl', 'activesellorderamt.pkl', 'passivebuyorderamt.pkl', 'close.pkl', 'buyordercanceledamt.pkl', 'volume.pkl', 'sellorderamt.pkl', 'close_adj.pkl', 'passivebuyordervol.pkl', 'open.pkl', 'buytradeamt.pkl', 'sellordercanceledamt.pkl', 'buytradenum.pkl', 'sellordercanceledvol.pkl', 'passivesellordervol.pkl', 'low_adj.pkl', 'high_adj.pkl', 'buyordercanceledprice.pkl', 'buytradevol.pkl', 'selltradenum.pkl', 'amt.pkl', 'buyordercanceledvol.pkl', 'open_adj.pkl', 'low.pkl', 'tradenum.pkl']


date = 20210715

difference = {}

for factor_name in factor_list:
    offline_factor = pd.read_pickle(offline_path%(date,1430)+factor_name)
    online_factor = pd.read_pickle(realtime_data_path%(date,1430)+factor_name)
    difference[factor_name.replace('.pkl','')] = abs(offline_factor.fillna(0) - online_factor.fillna(0)).mean()

difference = pd.DataFrame(difference)