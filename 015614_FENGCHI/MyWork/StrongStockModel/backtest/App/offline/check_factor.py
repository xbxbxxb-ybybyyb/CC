# @Time : 2021/1/15 9:38
# @Author : Zhichen Lu
# @File : check_factor.py
import pandas as pd
import os
from online_conf import local_config_path
from StrongStockModel.conf.path_config import root_path

local_config_path = local_config_path.replace('2/', '/')
path = local_config_path + 'check/'

mae_daily = pd.read_pickle(path + 'MAE_raw.pkl')
corr_daily = pd.read_pickle(path + 'CORR_raw.pkl')
corr, corr_min = corr_daily.mean(), corr_daily.min()
mae, mae_max = mae_daily.mean(), mae_daily.max()
count = corr_daily.count()

compare = pd.DataFrame({'corr_mean': corr, 'corr_min': corr_min, 'mae_mean': mae, 'mae_max': mae_max})
compare = compare[count > 0]
compare = compare.sort_values('mae_mean', ascending=False)
# os.mkdir('/data/user/015664/AFuckingTrigger/online_validation/')
compare.to_excel('/data/user/015664/AFuckingTrigger/online_validation/因子统计对比.xlsx')
sing_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path/using_fix_list.pkl')
factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)

using_factor = factor_evaluation.loc[sing_factor_list]
filtered_factor = factor_evaluation.loc[compare.query('mae_mean<0.005 & corr_mean>0.99').index]

# indicator = 'ic_all_d'

# using_factor[indicator].apply(abs).sort_values(ascending=False)[:400].mean(),filtered_factor[indicator].apply(abs).sort_values(ascending=False)[:400].mean()

for indicator in ['ic_all_d', 'ic_all_t', 'ic_all_c']:
    factor_list = sorted(filtered_factor[indicator].apply(abs).sort_values(ascending=False)[:400].index.tolist())
    pd.to_pickle(factor_list, local_config_path + f'{indicator}_400_factor_list_FilterByRawDifference.pkl')

offline_fix_path = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
os.listdir(offline_fix_path)
check = pd.read_pickle(f'{offline_fix_path}Fix1000_RS_mean.pkl')

offline = pd.read_pickle('/data/group/800319/strategy_local_path/daily_output_offline/20201026//pred_signal_1000.pkl')
online = pd.read_pickle('/data/group/800319/strategy_local_path/daily_output/20201026//pred_signal_1000.pkl')

len(offline[1])
len(online[1])

online[0]
offline[0]
len(set(online[1].index).intersection(set(offline[1].index)))
compare = pd.DataFrame({'online': online[1], 'offline': offline[1]})
check = online[0] - offline[0]
mae = abs(check).mean()

##############存因子
availabel = factor_list = ['HighFreqDrawBack', 'MovingAverageStd', 'VolumeStd_Mean_1', 'AmtStd_Mean_1', 'VolumeVarianceRatio_13',
                           'PriceSkew', 'Volatility_13h', 'MinDirectedVol', 'HighCloseDistance', 'LowHighRetStdRatio',
                           'SplitStdRatio', 'FactorAlpha043', 'zhy_fix_65', 'AmountRatioGrowthSharpe', 'Min10ReUpLast5Min',
                           'SplitVolumeRatio', 'hfPVcorrHD', 'Factor_Fix_zhy_52', 'Fix_DealnumSharpe', 'zhy_fix_112',
                           'HF_LinearDiffStdRatio_13h', 'TurnFree_3', 'HF_LinearHighDiffSkew_13h', 'TopAmountRatioVolumeDiffSharpe',
                           'HF_RSRS', 'VolSkew', 'WilliamsIndicator_13h', 'VolMeanSharpeUp_13h', 'HF_VolumeAmtSkewRatio',
                           'HF_HDeg1_13h', 'HF_AmtDeg1', 'Factor_Fix_zhy_251', 'FactorAlpha066', 'HF_AmtVolatilityPriceCorr_13h',
                           'FreeTurn_Mean_1', 'SwingPriceCorr', 'HF_LowHighStdRatio_13h', 'SplitVolumeStdDownRatio', 'EWMSwing',
                           'TwapSkewToVwap', 'HF_Pcf5dSharpe', 'CloseVwapRetSkew', 'hfCapSkewRatio_13h', 'hfMktLSCap',
                           'WilliamsPriceVolCorrMultiple_13h', 'VolSharpeUp_13h', 'LowStdAmountRatio', 'HF_OverBuySell_13h',
                           'SwingReturn', 'BottomTopPriceRetStdRatio', 'Factor_Fix_zhy_116', 'CorrMaxRePriceRank', 'MinPriceBeta',
                           'VolumeUpPVCorr_13h', 'HFPVCorr', 'MinPriceAutoCorr', 'CorrAbsWRPrice5min', 'HighLowMeanVwapRetSharpe',
                           'DrawdownSkew', 'RetTurnCorr', 'VwapmaLowDiffSkew_13h', 'TemporalVolumePriceCorr', 'Factor_Fix_zhy_135',
                           'SplitStdUpRatio', 'StdAmountDiff', 'HighLowVwapDiffStdRatio', 'HF_IlliqShortcut_13h',
                           'HF_VwapLowVR_13h', 'HighFreqRelativeClose', 'AmountGrowthDuringLowRet', 'HF_VwapTailVolumeRatio_13h',
                           'HF_HmL2CVwapCorr_13h', 'HF_OverBuy', 'VwapBollingerBand30min_13h', 'HF_ReverseVolRatioVWAP',
                           'HF_VwapBollingUp_13h', 'hfHighVolPVcorr', 'LowSharpeAmountStdRatio', 'HFPSCorr', 'FactorAlpha054',
                           'MaxDrawDown', 'VwapBollingerBand_13h', 'WAPResistBackStd_13h', 'HF_VolSwing5mToAll',
                           'BotTopCumSwingStdRatio', 'HfTurnMaSkew', 'HF_PriceDiffStdRatio', 'VolumeStd_Mean_5', 'hfIdxCorr',
                           'MAStd', 'WAPResistBackRatio_13h', 'LogFreeTurn_1', 'hfDownStrength', 'HF_VolumeSharpe',
                           'HfLast120VolumeStdSkew', 'HF_VmL2HmVDiffStdRatio', 'Factor_Fix_zhy_260', 'HighFreqVolumeMACmp',
                           'HfHalfDayCloseRtnCountDiff_13h', 'AmtStd_Mean_5', 'hfTurnStdHD', 'AmountMktDiff', 'hfRST',
                           'HighFreqTurn', 'CorrPVLowLiquidity', 'HfLast120LongTurnSkew_13h', 'LogAmt_5', 'SkewUpDown',
                           'UpCountLowDistance10d', 'hfCPVCorrHD_13h', 'ExcessBollingUpRateMean5d', 'HfLast60TurnVolCorr',
                           'Factor_Fix_zhy_253', 'Std_Volume5', 'HighFreqSwingStdCmp', 'AmtStdStd5d', 'HfLast120RangeMeanRatio',
                           'LowHighStdRatio', 'VolumeMax10min2All_13h', 'MinExtremRet', 'WAPResistBackTop_13h', 'AmtStd_Mean2Std_5',
                           'CumPVRatioCorr', 'VolumeStd_Mean2Std_5', 'VolBurstReturn', 'StdUpDown', 'High2LowVolDown', 'VolCorr',
                           'HfSwingCloseCorr', 'Rsrs', 'CWI_skew_hs300_rollingmean_3', 'HF_Last30mBiasVolumeCorr_13h',
                           'MinCorrAbsRePriceRank2D', 'Factor_Fix_zhy_279', 'RWIV_300_retstd_tail_std', 'CWI_skew_szzz_rollingms_3',
                           'HfHalfDayCloseRtnCountDiffBias_13h', 'MinPre30mAutoCorr', 'WI_VSSC_zz500',
                           'HfLast120RtnPerAmtVolPre1minCorr', 'HF_WR2d', 'HF_TurnoverrateSharp', 'WeightedFlow_1',
                           'HfLast120RtnPerAmtVolCorr', 'LargeSmallVolumeVWAPRatio', 'LogFreeTurn_5', 'BAStrength',
                           'Factor_Fix_zhy_76', 'MinPVCorr', 'ReLow_13h', 'StableVol5', 'UpVolatilityRate', 'TrendStrength',
                           'HighFreqRetRefMax', 'PVRatioCorr', 'MinPrePriceAutoCorr', 'VolumeDownChange_13h', 'FreeTurn_Mean2Std_5',
                           'CorrVwapVol_1', 'HF_TurnoverrateStd', 'AbnormalPriceDiff', 'StdDelayRatio', 'HighFreqVolumeSwingCmp',
                           'HighTurnVwap', 'HfLast120HighLowStdRatioMin_13h', 'HfRtnPerAmtVolCorr', 'LogDeltaVol', 'VRS',
                           'WR2d_13h', 'RetMean_Rank', 'MinMaxRet', 'RawAmtStdRatio', 'AmtSkew3', 'HfLast120RangeMeanRatioBias',
                           'RWIV_500_volumestd_top_min', 'Fix_AmtRetRolling', 'LogAmt_1', 'VRSS', 'FactorMin296_self_re',
                           'RetToStd', 'hml_CloseStd', 'HfVolSkew', 'HighLowVwapRatio', 'HfLast120HighLowDiffAmtCloseCorrDelta_13h',
                           'RollingCorrCloseVolume', 'VwapmaDiffVolCorr_13h', 'Min1WeightedFlow_1', 'CorrVWAPdt', 'WR_13h',
                           'RS_mean', 'AmtRatio_Mean_5', 'HF_UpRetAmtSkew', 'MinCapitalGainOverhang', 'BottomTopPriceSwingRatio',
                           'PriceMktDiff', 'BestWorstReSharpe5d', 'AmtStd_Std_5', 'HighLowStdRatio', 'VolumeStd_Std_5',
                           'StdMaxAmountRatio', 'MinPre5mSkew', 'HighFreqTurnRetCorr', 'AccelerateStd', 'HF_UpRetTurnDiffSharpe',
                           'RWI_sifastrisedrop_rollingstd_3', 'LowRetAmountSkewRatio', 'DIFMaxRaw_1_5', 'hfDownPVcorr5',
                           'hfCPVCorrHDmean_13h', 'SwingPerDeal', 'CorrVwapVol_5', 'MinCorrVolumePrice_1',
                           'HF_CMExcessRetWeightSkew_13h', 'CWI_skew_szzz_rollingmax_5', 'hfIdxCorr5', 'OTC5std', 'hfUpPVcorr5',
                           'HF_VwapAmtUpCorrInLowVolatility_13h', 'FreeTurn_Mean_5', 'HF_VwapTailTopVolumeDiffRatio_13h',
                           'FreeTurn_Std_5', 'Factor_Fix_zhy_119', 'CorrDelVolumePriceMean', 'Factor_Fix_zhy_138',
                           'HF_LowReBiasSelfCorrStable_13h', 'Close2High', 'HF_VwapTopTailVolume_13h', 'CorrResisVWAP',
                           'RWIV_300_illq_top_avg', 'HF_RSRSZScore', 'HF_TwapVwapDiffSharpe', 'MinPreVolRet', 'sistdwfiavg_re',
                           'PVSwingCorr', 'MaVolDistance10', 'HF_HighPinZscore_13h', 'SignDownWick', 'PriceUpDownRatio',
                           'adjstdwms_intraday_5', 'HighFreqLowRetCorr', 'adjstdsd_intraday_5', 'RetVolMaxRaw_1_5',
                           'HF_AmtVolatilityPriceCorr5D_13h', 'amtavg_bwskewmean_60_3', 'HF_NormRePriceCorrSharpe_13h',
                           'adjstdstm_intraday_5', 'UpVolatilityRateStd5d', 'Rtn2VolumeMeanAbs1', 'amtavg_ntskewmean_60_3',
                           'dailyms_intraday_5', 'RetVolCVMultiple', 'CorrVolumePriceRankSharpe', 'PDS', 'AvgPriceVwapRateStd5d',
                           'WI_CVSC_zz500', 'PriceDeviationBias10d', 'CorAbsRetVol3', 'HF_PriceDiffRatio', 'CorrHighVol',
                           'CorrAmpAmt_1', 'WI_RMCorr_zz500_rollingms_3', 'VNSPRaw_1_5', 'Excess300High5', 'HF_CloseVwapSkew_13h',
                           'Excess500Low5', 'amtavg_bwmaxskew_60_3', 'HighFreqRetRefStd', 'MinVRCExcess_13h',
                           'VWI_amt_mean_tail_skew300', 'MinPrePVCorr', 'HF_VwapLowCorrZscore_13h', 'WRMean5d_13h',
                           'Excess500High5', 'AmtPct_Mean_1', 'HF_CorrCloseVolumeSharp_13h', 'HfLast120CloseVolumeStdCorrBias_13h',
                           'High2Low_1', 'amtavg_ntskewmean_20_3', 'FactorAlpha045max', 'HfLast120RtnStdCloseCorrBias',
                           'FactorAlpha075', 'amtavg_bwstdskew_20_3', 'amtavg_ntmeanskew_60_3', 'HighSkew_Mean_5',
                           'CloseSkew_Mean_5', 'DisPRaw_5', 'HF_HighVwapSkew_13h', 'CloseOpenSkew2Abs', 'Ret30RankMean_5',
                           'MinCorrVolumeRetUp_1', 'AvgClose2Vwap_Std_5', 'HFPVCorrMin', 'HfLast120MaxRtnCloseCorrBias_13h',
                           'hfCapStdRatioMin', 'AvgPriceVwapRateSharpe5d', 'HfLast120MinRtnCloseCorrSharpe', 'SmartVwapSharpe5d',
                           'HighFreqVHFCorrBias', 'Factor_Fix_zhy_208', 'DisNRaw_5', 'Factor_Fix_zhy_15', 'amtavg_ntmsmean_60_3',
                           'HFPTSCorrMinAdj', 'FactorMin295_mean_div_std_re', 'HfLast120MinRtnCloseCorrBias',
                           'HF_AmtStdStrengthCloseBias', 'lowidx_rollingmax_5', 'Close2BarHigh', 'EVolChgBetaAbs_1_1',
                           'close_tooriginal_price', 'HF_AmtStdStrengthCloseChange_13h', 'HFPVCorrStdAdj',
                           'HfLast120MaxRtnCloseCorrSharpe', 'amtavg_bwmaxskew_60_10', 'HFPVCorrBias', 'HFPSCorrStdAdj',
                           'Beta500d3', 'amtavg_bwmstb_60_10', 'MinCapitalGainBetaZscore', 'firstintraretskew5_re',
                           'hfDownPVcorrbias', 'hfUpRRC', 'CloseExcessPercent_1', 'RetStd_Mean_1', 'CorAmtMeanMean5',
                           'shortbeta_zz500_rollingms_3', 'HfAmtSpaceSkewMean_13h', 'ShortTurn', 'DIFMeanRaw_5_30', 'HFPTSCorrBias',
                           'MinAmtStdRatio', 'FactorMin98_mean_div_std', 'sistdwfiavg2_3_re', 'Factor_Fix_zhy_220',
                           'HighFreqDuoKongSharp', 'Factor_Fix_zhy_268', 'RWIsi_skew_rollingmax_5', 'HighLowStdRatio_mean5d',
                           'HFPSCorrMinAdj', 'MaxAmtStdRatio', 'CWI_skew_zz500_rollingmax_3', 'amtkrt_nttbmean_20_3',
                           'AmtPct_Mean_5', 'amtavg_ntskewmean_60_10', 'hfUpPVcorrbias', 'IdealRev2', 'HFPVCorrMinAdj',
                           'CorrAmpVwap_1', 'amtavg_ntdmkurt_20_10', 'amtavg_ntmeankurt_20_10', 'FactorAlpha043dif',
                           'amtavg_ntminkurt_60_10', 'amtavg_ntminskew_60_10', 'Factor_Fix_zhy_267', 'amtavg_bwskewmean_20_10',
                           'Cor500D3', 'HfVolClosePre5minCorr10d', 'HF_ForecastEPDelta40d', 'HLStd1mean', 'VWMidReurnSharpe5d',
                           'AbsRet30Mean_5', 'amtkrt_bwmeantb_20_10', 'amtavg_ntdmkurt_60_10', 'UpDownVolRatioStdRaw_1_1',
                           'RevExclu4mean', 'HFPSCorrMean', 'amtavg_ntmeanskew_60_10', 'HFPTSCorrStdAdj', 'CloseOneOrderTwoOrder',
                           'amtavg_bwtbkurt_60_10', 'FIX_lly_5', 'HFPSCorrMin', 'Ret30Mean2Std_10', 'CorAmtStdStd5', 'AmtKurt',
                           'hfHighCapRetMean', 'FactorMin370_std_re', 'HF_Shortcut2CloseCloseCorrZscore', 'FactorCorr09',
                           'FactorAlpha045mean', 'FactorCorr12', 'MinCapitalGainBetaEwm', 'WI_RStd_kurt_rollingmean_3',
                           'Factor_Fix_zhy_101', 'hfCPVCorrHDbias_13h', 'amtavg_ntstdskew_20_10', 'amtavg_bwskewmean_60_10',
                           'amtkrt_bwmaxmean_20_10', 'DIFMeanRaw_5_5', 'TurnoverHighRetSharpe', 'hfMktLSCapMR5', 'FactorAlpha074',
                           'AggressionPRaw_3_5', 'HF_VwapRetSkew_13h', 'FactorAlpha047meandivstd', 'TurnStd', 'hfDownTurnSharpe',
                           'HFPSCorrBias', 'HF_RetHHIZscore', 'amtavg_bwscmskew_20_10', 'L2C5', 'amtavg_nttrbskew_60_10',
                           'CorAmtMeanSKew5', 'FactorAlpha007', 'MinuteVolatilityPriceCorr', 'FIX_lly_7', 'MinUpDownVolRet',
                           'HfLast120HighLowDiffAmtCloseCorrPreBias', 'VolaRatio5Std', 'uretvolnew_bwskewmean_20_3',
                           'VwapStdCorrDistanceLow10d_13h', 'VolRatio10min', 'amtavg_bwskewtb_20_10', 'PDSS',
                           'HfSwingCloseCorrSharpe', 'Factor_Fix_zhy_211', 'BSPowerSkew3mean', 'RSIStdRank_5_5', 'CorAmtStdSKew5',
                           'amtavg_bwstdkurt_20_10', 'amtavg_ntminskew_20_10', 'amtavg_ntscmmean_60_10',
                           'HfLast120HighLowDiffAmtCloseCorrSharpe', 'Rtn2VolumeStd5', 'amtavg_bwkurtskew_20_10', 'IbsLast15Min',
                           'amtavg_ntkurtskew_20_10', 'PriceRange_5', 'AggressionPRaw_5_1', 'amtkrt_ntrdmmean_20_10',
                           'OverBuySellKurtRank_1_5', 'amtavg_ntskewtb_20_10', 'IndexCloseCorr', 'TurnWeiRet3max',
                           'amtkrt_ntrdmmean_60_10', 'MinCorrExcessPriceRank', 'CorrAmpVwap_5', 'DIFSkewRank_5_1',
                           'amtkrt_nttbstd_20_10', 'HighFreqAmpRetStd', 'LowStdRatio_max5', 'hfHVR5', 'RetSmallKurt5', 'CorPV5',
                           'FactorCorr01_F1', 'TimeID_volume_std_top_std_rollingmin_5', 'FactorAlpha054dif', 'amtkrt_bwtbstd_20_10',
                           'AggressionNRank_5_1', 'HF_VwapTopTRRatio_13h', 'dretvolnew_bwtrbmean_60_3', 'FIX_lly_24',
                           'MeanRatio_min5', 'CorrVWAPTrendHigh', 'RetVolSkewRaw_5_1', 'TurnWeiRet3mean', 'CorrAmpAmt_5',
                           'Factor_Fix_zhy_228', 'VolMeanSharpeUp2Down', 'HfLongVwapSwingCorrBias', 'Factor_Fix_zhy_244',
                           'AvgClose2Vwap_Mean2Std_5', 'CorrRetVol_5', 'MACDNumChgSignRank_5_1', 'HighFreqDrawBackMeanBias',
                           'FactorAlpha066min', 'FIX_lly_39', 'dretvvolnew_ntskewmean_20_3', 'RetToVolSke', 'MinCapitalGainAbs',
                           'adjEMAbc_intraday5', 'Factor_Fix_zhy_197', 'Fix_CloseAmtStdCorr_mean', 'CorrVWAPstd', 'StructedRev5',
                           'hfHighVolPVcorr5', 'HighFreqHighMARetCorr', 'FIX_lly_19', 'IntradayAmountRatio', 'FactorMin215_mean',
                           'uretvvolnew_ntskewmean_20_3', 'HighStdRatio_min5', 'AccelerateKurt', 'RetVolKurtRank_5_1',
                           'MinCapitalGainAutoCorr', 'uretvvolnew_ntskewmean_60_3', 'AggressionNRank_5_5', 'FIX_lly_2',
                           'LogRtn2Amt5', 'StdRatio_max5', 'HfLongVwapSwingCorr5d', 'FactorSp002', 'HighFreqDrawBackStdBias',
                           'TurnStdPure3mean', 'dretvvolnew_ntmsmean_60_3', 'TimeID_hl_top_std_rollingmin_5',
                           'dretvolnew_ntrdmmean_60_3', 'WL350_5', 'Beta300', 'closedrawdownspeed_rollingstd_3', 'RetKurt5',
                           'OverflowPerAmtMean5d', 'FactorMin384_mean_re', 'GDZQ4std3', 'CorrWRPriceRank', 'High2Low_5',
                           'FactorMin549_mean_div_std_re', 'StdRatio_min5', 'HighKurt5mean', 'hfTurnSharpeHD', 'HighStdRatio_max5',
                           'TurnWeiRet3min', 'FactorMin217_mean_re', 'RWIsibeta_rollingms_5', 'BI500Std5', 'HighFreqDownSpeed',
                           'uretvvolnew_bwskewmean_60_3', 'HighKurt5std', 'HLLength5', 'HF_HmL2CVwapCorrZscore_13h',
                           'UpDownVolRatioSkewRank_1_1', 'CorrVwapCVPriceLast60', 'Ret30Std_5', 'HF_UpReaturnRealStdZScore',
                           'CorrExcessRank2', 'FactorMin117_mean', 'CloseVolumeCorrBias20d', 'UpDownVolRatioSkewRank_3_5',
                           'Factor_Fix_zhy_205', 'GTJA2', 'HF_Amt10mSkew20d', 'BiasStd3_5Std', 'HLWI_kurt_cybz_rollingmax_3',
                           'FIX_lly_18', 'DisPSr_1', 'FactorMin378_std_re', 'HF_VwapTailTopTRRatioMin_13h', 'FIX_lly_51',
                           'CorrMaxRePrice5minSharpe', 'WI_CVCorr_zz500_rollingstd_5', 'PVRatio10trans0p5',
                           'FactorMin215_meandivstd', 'AmtPcg_regrmse', 'CorrAmpRet_5',
                           'HF_MeanIntradayReturnAcrossProfitableInvestors_13h', 'IndustryExcessReturnStd5d',
                           'FactorMin224_meandivstd', 'FactorMin289_std_re', 'CorrOpenVol_min5', 'RollingRetCorrPctg_5',
                           'FIX_lly_1', 'FIX_lly_9', 'FactorMin417_std_re', 'hfUBstd', 'CWI_std_cybz_rollingms_5', 'TurnWeiRet5min',
                           'GTJA54_N', 'RollingSignDownWick', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h',
                           'OverBuySellKurtRank_5_15', 'OCKurt3mean', 'FIX_lly_26', 'AccelerateSkew', 'TurnWeiRet5mean',
                           'CorrVWAPBollingUpDown', 'DisNStd_1', 'FactorMin31_std', 'RetVolKurtMean_1_5', 'FWRM',
                           'CWI_skew_cybz_rollingmean_5', 'OpenDivClose_5', 'HF_PVVCorrIndusRank',
                           'HF_VwapTopTailVolumeStdRatio_13h', 'CWI_kurt_zz500_rollingstd_5', 'StdRatio_meandivstd5',
                           'DivergenceMeanRaw_1_5', 'dretvolnew_bwskewmean_20_3', 'MinDailyCorrCloseVol', 'DIFSkewMean_1_1',
                           'CorrRankCloseVolume_5', 'RetGather0p9mean5', 'FactorMin32_mean', 'BigSmallRetCloseDiff3_trans0p25',
                           'GTJA32', 'VolaRatio10Mean', 'hfHVRbias', 'FactorAlpha061', 'subrradjwms_intraday_5', 'HLOKurt3',
                           'Factor_Fix_zhy_274', 'FactorAlpha045meandivstd', 'EVolChgSkew_1_1', 'RWI_kurt_zz500_rollingstd_5',
                           'Cor300Down5mean', 'RetBigStdResAmt5', 'FactorMin28_mean', 'hfHighVolPVcorrbias', 'RSIMeanRegrmse_1_15',
                           'DisPStd_1', 'hfLowCapRetMin', 'RSIMinMean_1_15', 'DIFDifSr_1_5', 'HF_VwapTopVolumeRatioZscore_13h',
                           'HF_TwapRetWeightSkew', 'uretvolnew_ntskewmean_60_10', 'hfLowCapRetMax', 'RetVolMinSr_1_1',
                           'RetVolMaxSr_1_1', 'FIX_lly_21', 'uretvolnew_ntmaxstd_60_10', 'TurnWeiRet5max', 'FIX_lly_6', 'FWRMin',
                           'FactorMin11_std', 'VwapSkew5mean', 'dretvolnew_ntminskew_60_10', 'FactorMin42_mean',
                           'Factor_Fix_zhy_255', 'FactorMin124_diff', 'FactorMin6_mean', 'DIFMaxSr_1_5', 'RSISkewStd_1_5',
                           'HighLowStdRatio_min5', 'FactorMin111_std', 'Cor300Up5mean', 'FactorMin45_std', 'AmtStdRet_mean10',
                           'subrr2adjwms_intraday_5', 'RetVolStdSr_1_1', 'uretvolnew_bwmaxskew_60_10', 'UDContrast5mean',
                           'uretvolnew_bwskewmean_60_10', 'RegAccelerateStd', 'FactorMin59_mean', 'DIFMaxSr_1_1',
                           'dretvolnew_ntrdmkurt_60_10', 'GTJA1_6', 'uretvolnew_ntstdskew_60_10', 'FactorMin61_mean_div_std',
                           'uretvolnew_ntminskew_20_10', 'DIFDifSr_1_1', 'hfDownPVcorrsharpe', 'MinCapitalGainRH',
                           'uretvolnew_ntmeanskew_60_10', 'dretvolnew_bwminskew_20_10', 'FactorMin25_std',
                           'dretvolnew_ntkurtmean_20_10', 'FactorMin36_mean', 'FactorMin15_mean', 'FactorMin108_std',
                           'FactorMin47_std', 'dretvolnew_ntkurtskew_20_10', 'FactorMin118_meandivstd',
                           'HF_DVwapDVolumeCorrZscore_13h', 'RetVolMeanSr_1_1', 'uretvolnew_ntminskew_60_10', 'FIX_lly_20',
                           'uretvolnew_ntkurtmean_20_10', 'uretvolnew_bwstdskew_60_10', 'uretvolnew_bwskewtb_20_10',
                           'FactorMin76_std', 'FactorMin118_mean', 'FIX_lly_12', 'WeightedTurn_10', 'dretvolnew_ntskewmean_60_10',
                           'FactorMin33_std', 'FactorMin564_diff_re', 'uretvolnew_bwmstb_60_10', 'dretvolnew_ntminstd_20_10',
                           'DIFKurtMean_1_1', 'uretvolnew_ntdmstd_20_10', 'StableVol20', 'uretvolnew_ntskewstd_60_10',
                           'FactorMin33_mean', 'CorrHighVol_std5', 'FIX_lly_8', 'RWIV_300_illq_top_avg_rollingstd',
                           'uretvolnew_bwtbkurt_60_10', 'DIFMaxPct_1_5', 'VwapStdRatio_min5', 'VolGather0p9mean5', 'SMUp0p9Vol5',
                           'uretvolnew_ntstdskew_20_10', 'DisPSkew_1', 'FactorAlpha035', 'HF_PriceVolIndustryDelta', 'GTJA8',
                           'FactorMin54_std', 'HighFreqDuoKongMeanBias', 'HLStd5std', 'FactorMin124_meandivstd', 'FactorMin19_mean',
                           'FactorMin48_mean_div_std', 'FactorMin564_self_re', 'FactorMin27_std', 'HLSkew5std',
                           'CloseOpenKurt2Mean5', 'dretvolnew_bwskewmean_60_10', 'FactorMin43_std', 'RetVolSkewMean_1_5',
                           'FactorMin3_std', 'uretvolnew_bwskewtb_60_10', 'HLTR_mean5_intraday', 'VwapStdRatio_mean5',
                           'LogRtn2Amt1Res', 'FactorMin37_mean', 'uretvolnew_nttbkurt_60_10', 'FactorMin59_diff', 'RSIMeanSr_1_5',
                           'FactorMin541_mean_div_std_re', 'dretvolnew_ntmeanskew_20_10', 'FactorMin8_mean', 'GTJA62',
                           'uretvolnew_ntminstd_20_10', 'amtavg_mktstate_amt_std_topskew_5_3', 'VNSPRegrmse_1_5', 'RSIMeanSr_1_15',
                           'FactorMin7_mean', 'FactorMin12_std', 'Factor_Fix_zhy_79', 'dretvolnew_ntdmstd_60_10',
                           'dretvolnew_bwkurtmean_20_10', 'TurnStdPure5std', 'Last30MaxDrawdownBias20d', 'RSIMinSr_1_15',
                           'VNSPMean_1_5', 'HLSkew5mean', 'dretvolnew_bwskewtb_20_10', 'FactorMin112_std',
                           'dretvvolnew_ntminkurt_60_10', 'FactorMin26_std', 'FactorMin77_std', 'FIX_lly_49',
                           'dretvvolnew_bwminskew_60_10', 'FactorMin50_diff', 'FactorMin116_std', 'FactorMin1_std',
                           'HighLowStdBias20d', 'CyqHhi', 'FactorMin109_std', 'amtavg_mktstate_ret_skew_tailskew_5_3',
                           'FactorMin32_mean_div_std', 'CorrLowVol_min', 'FactorMin221_std', 'FactorMin2_std', 'VHighKurt',
                           'VwapStdRatio_max5', 'LogRtnAbs2Amt1Res', 'dretvvolnew_bwmeanskew_60_10', 'FactorMin115_std',
                           'dretvvolnew_ntmeanskew_60_10', 'RollingRetCorrPctg_10', 'uretvvolnew_bwmeanskew_60_10',
                           'uretvvolnew_ntminkurt_20_10', 'uretvvolnew_ntkurtmean_60_10', 'FactorMin22_std',
                           'dretvvolnew_bwstdkurt_60_10', 'dretvvolnew_ntskewmean_20_10', 'uretvvolnew_ntkurtskew_20_10',
                           'HF_PriceVolCorrIndusRank', 'CorrLowVol_mean5', 'FactorMin513_mean_div_std_re', 'FIX_lly_42',
                           'dretvvolnew_ntminskew_20_10', 'FactorMin13_mean', 'uretvvolnew_ntmsmean_60_10',
                           'HF_AmtStrengthCloseSharp_13h', 'uretvolnew_bwkurtmean_20_10', 'hfUpRRCbias', 'FactorMin13_std',
                           'HF_AmtStrengthCloseChange_13h', 'Last30MaxClimbBias20d', 'RetVolStdSr_1_5', 'RetVolMaxSr_1_5',
                           'HighLowStdLowDistance10d', 'dretvvolnew_ntkurtmean_60_10', 'dretvvolnew_ntskewmean_60_10',
                           'uretvvolnew_ntminskew_60_10', 'dretvvolnew_ntkurtskew_20_10', 'HF_VwapTailTurnRatioZscore',
                           'uretvvolnew_ntmeanskew_20_10', 'Vwap2Twap5mean', 'RetVolKurtSr_1_1', 'FactorMin26_mean',
                           'uretvvolnew_ntskewmean_60_10', 'dretvvolnew_ntminskew_60_10', 'FIX_lly_71',
                           'amtavg_mktstate_ret_topskew_5_3', 'dretvvolnew_ntstdkurt_20_10', 'uretvvolnew_ntmstb_60_10',
                           'FactorMin1_mean', 'uretvvolnew_bwskewmean_20_10', 'uretvvolnew_bwminskew_60_10', 'FactorMin487_mean_re',
                           'uretvvolnew_bwmstb_20_10', 'SignedVolume', 'HLStdRatio', 'NetworkDegree3', 'RSRS_Mean_1',
                           'uretvvolnew_bwmaxskew_20_10', 'Vwap2TwapKurt5std', 'uretvvolnew_bwkurtskew_20_10',
                           'uretvvolnew_ntkurtstd_20_10', 'FactorMin112_meandivstd', 'dretvvolnew_ntskewskew_60_10',
                           'uretvvolnew_ntminkurt_60_10', 'FactorMin249_std_re', 'FactorMin494_mean_re', 'RetUpWeightedByVolSR',
                           'NetworkDegree3Net', 'uretvvolnew_ntdmkurt_20_10', 'FactorMin28_std', 'uretvvolnew_ntmsmean_20_10',
                           'FactorMin56_mean_div_std', 'FactorMin80_std', 'uretvvolnew_bwskewmean_60_10', 'CorrRankOpenVolume_10',
                           'dretvvolnew_bwskewmean_60_10', 'FactorMin565_mean_re', 'FactorMin405_std_re',
                           'dretvvolnew_ntstdskew_20_10', 'StableRet20', 'adjdmstdcpt_intraday_5', 'FactorMin403_mean_re',
                           'CORA_A_3', 'dretvvolnew_ntscmskew_20_10', 'DisNMean_5', 'FactorMinCor4_diff_div_std_re',
                           'MACDNumDiffMean_1_1', 'ConsRetStd3std', 'dretvvolnew_nttbkurt_20_10', 'dretvvolnew_nttbskew_20_10',
                           'FactorMin50_diff_div_std', 'dretvvolnew_ntscmmean_60_10', 'uretvvolnew_nttbkurt_20_10',
                           'HLWI_kurt_hs300_rollingmax_5', 'ConsVol0p7Std5', 'uretvvolnew_bwtbkurt_20_10',
                           'dretvolnew_bwmeanskew_20_10', 'VwapStdCorrBias20d_13h', 'VWI_hl_tail_kurt500',
                           'FactorMin214_mean_div_std_re', 'FSmartMin', 'FactorMin14_diff', 'FactorMin82_mean', 'zhy_fix_73',
                           'DisNRegbeta_5', 'FactorMin13_diff', 'GTJA14_std5', 'GTJA41', 'CORA_R_3', 'AggressionNMean_1_1',
                           'LiqUp5', 'DisPMean_5', 'DisPRegbeta_5', 'FIX_lly_72', 'FactorMin85_std', 'FactorMin496_std_re',
                           'FactorMin124_diffdivstd', 'HighLowStdRatio_meandivstd5', 'FIX_lly_33', 'CorrCloseVol_Mean_1',
                           'FactorMin380_std_re', 'FactorMinCor4_mean_div_std_re', 'FactorMin339_std_re',
                           'IndustryExcessIlliqSharpe5d', 'TurnHighKurt', 'dretvolnew_ntkurtmean_60_10', 'RetAdjVolMeanRaw_5_30',
                           'RetVolMaxSkew_1_1', 'cummaxdd_nttrbmean_20_3', 'WeightedFlow_5', 'hfCapStdRatioBias_13h',
                           'HF_VolumeStdStrengthCloseChangePct', 'NetworkPremium3', 'SharpeDuringStdDrop',
                           'FactorMin216_mean_div_std_re', 'OverBuy_Sell_3', 'HF_RetTopVwapAmtCorrBias',
                           'FactorMinKdayShortCut_regrmse', 'CumAmountVarKurt', 'HF_CorrBuyStrength_13h', 'DisNMean_1',
                           'RetVolStdSkew_1_1', 'VolChg1Mean', 'InstitutionalVolumeRatio2min', 'FactorCorr08', 'PVComb5',
                           'MACDNumDiffBeta_5_5', 'RetVolMeanSr_5_1', 'VDailyChange_ret_std_top_avg_rollingstd_5',
                           'Factor_Fix_zhy_164', 'GTJA20_std5', 'CloseVwapRetKurt', 'Factor_Fix_zhy_147', 'FIX_lly_16',
                           'HF_VwapTopTailAmtRatio_13h', 'IdealSwingMin2D', 'UpDownAmtRatioStdMean_1_5', 'HF_OpenVwapSkew',
                           'hfUpTurnSharpe', 'Min1WeightedFlow_5', 'FSmartMax', 'VwapSwingCorr', 'RetVolDifSkew_1_5',
                           'VolaDownward20', 'FactorMin86_mean_div_std', 'DivergenceStdRaw_5_15', 'OverMean_Std',
                           'IndustryExcessPVCorrBias5d', 'TurnHighSkew', 'FactorMin79_std', 'cummaxdd_bwrdmkurt_20_10',
                           'CumSwingCumAmountDiffSharpe', 'zhy_fix_270', 'cummaxdd_bwkurtmean_20_10', 'DisPSr_5', 'OverBuy_Mean_1',
                           'FactorMinCor21_self_re', 'cummaxdd_nttrbskew_20_10', 'RetVolMaxSkew_1_5', 'RetVolKurtRegbeta_5_1',
                           'DIFMeanRegbeta_5_30', 'DIFSkewMean_5_5', 'TopAmountTradingCostRatio', 'AbnormalVolumePVCorr',
                           'Last30minReVolumeCorrMean5d', 'FactorAlpha061meandivstd', 'FactorSp017max', 'MinPre30mAutoCorrDelta',
                           'FactorMin129_diff', 'FactorMin343_mean_re', 'FactorAlpha032', 'Factor_Fix_zhy_66', 'Factor_Fix_zhy_43',
                           'LatestRetRatio', 'SharpeDuringAmountDrop', 'cummaxdd_nttrbmean_20_10', 'RSIMeanRegbeta_5_15',
                           'FactorAlpha032mean', 'FactorMin412_std_re', 'MACDNumDiff_5_5', 'DivergWinLossRMeanRank_5_5',
                           'TurnVolatilitySharpe5d', 'RetAdjVolSkewRank_5_30', 'RetUpSR', 'zhy_fix_281', 'FactorAlpha033',
                           'AbnormalReturnPVCorrMean20d', 'OverBuySellKurtMean_1_5', 'zhy_fix_96', 'FactorAlpha041max',
                           'FactorMin558_mean_div_std_re', 'FactorAlpha035max', 'AbsRetDivFreeTurn_5', 'RetAdjVolMeanRank_3_5',
                           'DIFMeanSr_5_5', 'UpDownAmtRatioSkewSr_1_5', 'FactorMin80_diff', 'VNSPStd_5_30',
                           'cummaxdd_bwrdmkurt_60_10', 'StdHmL_20', 'DIFStdRegbeta_5_1', 'FactorSp004max', 'FactorAlpha033max',
                           'AggressionPMean_5_5', 'MACDNumDiffMean_5_5', 'OverBuySellSkewRegrmse_1_15', 'MinVwapHLRateBetaDelta',
                           'FIX_lly_31', 'FactorAlpha039max', 'HighLowHitFreqRatio', 'GTJA27_max12', 'MinPrePriceRate',
                           'cummaxdd_nttrbkurt_60_10', 'GTJA40', 'FactorMin309_std_re', 'OverBuySellSkewRegrmse_1_5',
                           'FactorAlpha041mean', 'AbnormalReturnPVCorrBias20d', 'CRCS_raw_raw_kurt50', 'FactorMin1_diff_div_std',
                           'FactorMinKdayShortCut_std', 'FactorMinCor21_diff_div_std_re', 'cummaxdd_nttrbkurt_20_10', 'CSAD5std',
                           'HfLast120CloseSwingStdCorrSharpe_13h', 'cummaxdd_bwmaxstd_20_10', 'SkewDuringAmountHike', 'GTJA8_mean5',
                           'DIFKurtMean_5_30', 'FactorMin89_std', 'FactorAlpha027', 'Factor_Fix_zhy_3', 'UpToRetValue',
                           'AggressionPMean_3_5', 'FactorMin311_std_re', 'FactorMin95_mean', 'RetAdjVolMaxRaw_1_1', 'DisNSkew_5',
                           'AggressionNMean_3_5', 'UpDownVolRatioSkewMean_1_1', 'RetAdjVolMaxRank_1_5', 'UpDownAmtRatioSkewSr_5_30',
                           'RetVolKurtRaw_5_5', 'FactorMin93_mean_div_std', 'FactorMin103_std', 'WilliamUp_diffstd5',
                           'OverBuySellStdStd_5_15', 'FIX_lly_73', 'UpDownAmtRatioStdRegrmse_5_5', 'FactorAlpha077',
                           'UpDownAmtRatioSkewMean_5_30', 'cummaxdd_ntmaxstd_20_3', 'RetVolKurtRegbeta_5_5', 'CautionLongStd_5_5',
                           'FIX_lly_46', 'HfTopRtnVolumeRatioMean', 'FIX_lly_32', 'FIX_lly_68', 'IdeaVL', 'RetVolSkewSr_5_30',
                           'FactorMin94_mean', 'UpDownVolRatioStdRegbeta_5_5', 'CorrHighLowAvgToAmt_Mean_1', 'RetToVolabs',
                           'GTJA7_mean5', 'MACDEChgStd_5_1', 'FactorMin70_mean', 'hfMktLSCapSR', 'CPV10', 'RetVolSkewSr_5_1',
                           'HighFreqHighMARetCorrSharp', 'FactorMin530_mean_div_std_re', 'FactorMin383_mean_div_std_re',
                           'FactorMin168_std', 'CSAD5mean', 'zhy_fix_146', 'DIFStdSr_5_1', 'FIX_lly_35', 'AggressionPStd_5_1',
                           'FactorMin532_mean_re', 'HF_Last30minUpVolumeRetZscore_13h', 'FactorAlpha032min',
                           'MinDailyCorrCloseVol_min5', 'FactorMin89_diff', 'HF_VolumeStrengthCloseStdBias', 'Factor_Fix_zhy_275',
                           'FactorMin507_mean_div_std_re', 'FactorMin532_self_re', 'VarResampleMeanL', 'FactorMin343_self_re',
                           'Smartmoney_amt_kurt_02_05_rolling1', 'GTJA7_std5', 'UpDownAmtRatioKurtSr_5_5',
                           'LogDeltaVol_meandivstd10', 'MACDNumDiffBeta_5_1', 'HF_VwapHighStdVolumeRatioZscore_13h',
                           'DivergWinLossRStdRegrmse_1_5', 'Ret10Max_SR5', 'OverBuySellKurtSr_5_5', 'RetVolSkewMean_5_5',
                           'RetStd_Mean_5', 'Smartmoney_close_max_02_05_rolling1', 'Smartmoney_hlratio_max_02_05_rolling3',
                           'HF_VwapTopTailTurnRatioZscore', 'FactorMin93_diff', 'FactorMin193_std', 'GTJA43',
                           'DivergWinLossRMinStd_1_5', 'Smartmoney_close_dm_02_05_rolling3', 'FactorMin571_std_re',
                           'Smartmoney_close_max_005_05_rolling3', 'HF_VolumeTopVwapRatio', 'DivergWinLossRMaxStd_1_15',
                           'FactorMin505_mean_div_std_re', 'GTJA17_bias5', 'Smartmoney_hlratio_kurt_05_05_rolling1',
                           'DivergWinLossRMeanStd_1_15', 'TurnVolatilityStd5d', 'VwapAmtCorrMean5d_13h',
                           'Smartmoney_volume_skew_02_05_rolling3', 'FactorMin497_std_re', 'GTJA27_weight12', 'HF_Hl2OStrength_13h',
                           'MaxRetToSR', 'FactorMin87_mean_div_std', 'DivergWinLossRMaxMean_1_15', 'HF_UpVolumeSkewSeasonalBias',
                           'FactorMin353_mean_div_std_re', 'hfCapStdRatioCMax_13h', 'FactorMin406_std_re', 'AvgStdRatio_min5',
                           'FactorAlpha007Dif', 'HF_VmL2HmVStdRatio10minBias', 'FactorMin70_diff', 'DivergWinLossRStdRegbeta_5_15',
                           'DivergWinLossRMinStd_1_15', 'Smartmoney_ret_std_05_05_rolling3', 'Smartmoney_close_max0505_rolling3',
                           'RetAdjVolMeanRegrmse_1_1', 'Smartmoney_amt_ms005_05_rolling3', 'FactorMin189_std',
                           'FactorMin227_mean_div_std_re', 'UpDownAmtRatioStdStd_3_5', 'FactorAlpha024', 'FactorMinCor23_std_re',
                           'IdeaVStd', 'AccelerateStdRE_meandivstd10', 'HLM4_zhy', 'HF_LDeg1_13h', 'FactorAlpha075meandivstd',
                           'Smartmoney_ret_mean_02_05_rolling1', 'FactorMin353_std_re', 'Smartmoney_volume_skew_005_05_rolling1',
                           'Smartmoney_close_dm_05_05_rolling1', 'FIX_lly_30', 'FactorMin10_std', 'FactorMin193_mean_re',
                           'Smartmoney_amt_ms05_05_rolling1', 'DivergWinLossRDifStd_1_5', 'HF_VwapStdSwingCorrZscore_13h',
                           'DivergWinLossRMaxStd_1_5', 'FactorMin157_diff', 'FactorMin405_mean_div_std_re', 'FactorMin450_mean_re',
                           'FactorMin403_mean_div_std_re', 'DivergWinLossRDifSkew_1_5', 'FactorMin81_mean', 'HLStdRatio_min5',
                           'HF_VwapLowHighStdVolumeRatio_13h', 'UpDownAmtRatioKurtSr_3_5', 'TurnHighKurtRollingStd',
                           'InflowOutflowDiff', 'CloseCorrVolume_5', 'FactorAlpha058regrmse', 'FactorMin137_mean',
                           'hfCapStdRatioCBias_13h', 'FIX_lly_23', 'DivergWinLossRStdSkew_1_5', 'hfCapStdRatioCMean',
                           'FactorMin130_mean', 'FactorAlpha022regrmse', 'Smartmoney_hlratio_max_05_05_rolling1',
                           'TurnHighSkewRollingStd', 'DivergWinLossRStdSr_1_5', 'Smartmoney_ret_min_05_05_rolling3',
                           'FactorMin10_meandivstd', 'MinPreTopVolRate', 'OverBuySellStdStd_5_5', 'GTJA54_N_std5',
                           'FactorMin409_mean_div_std_re', 'FactorMin151_std', 'FactorMin75_mean', 'FactorMin150_mean',
                           'Smartmoney_amt_skew_05_05_rolling3', 'OverBuySellSkewRegbeta_5_5', 'RetAdjVolSkewRaw_1_1',
                           'FactorMin127_std', 'HF_VolumeStrengthDeg1', 'Smartmoney_amt_kurt_05_05_rolling1', 'FactorMin227_mean',
                           'FactorMin87_diff', 'HF_5mRePosVolVolatilityStable', 'Smartmoney_ret_min_02_05_rolling3',
                           'FactorMin124_mean_div_std_re', 'FactorMin412_mean_div_std_re', 'FactorMin229_mean_div_std_re',
                           'FactorMin35_std', 'FactorAlpha024meandivstd', 'FactorMin159_std', 'Smartmoney_ret_min_02_05_rolling1',
                           'RetUpSkew_Mean5', 'FactorMin283_std_re', 'FactorMin13_diffdivstd', 'TurnHighSkewRollingReg',
                           'FactorMinCor18_mean_re', 'GTJA16_min5', 'HF_VwapTailTopTRRatio_13h', 'OverBuy_Mean_5',
                           'FactorMin285_std_re', 'FactorMin564_mean_re', 'DivergWinLossRMinMean_1_5', 'Factor_Fix_zhy_117',
                           'AvgStdRatio_max5', 'Smartmoney_ret_mean_02_05_rolling3', 'FactorMin483_self_re',
                           'Smartmoney_close_max0505_rolling1', 'AvgStdRatio_mean5', 'CorrCloseVol', 'FactorMin320_std_re',
                           'DivergWinLossRSkewRegrmse_5_5', 'DivergWinLossRKurtRegrmse_5_5', 'SwingPriceLongCorr',
                           'FactorMin200_meandivstd', 'HF_CorrMaxVolumeZScore_13h', 'SwingPriceShortCorr', 'FactorMin40_std',
                           'FactorAlpha041diff', 'FactorAlpha027regrmse', 'CorrCloseVol_Mean2DStd_5', 'AmtPct_regrmse',
                           'HLStdRatio_max5', 'FIX_lly_29', 'FactorMin325_self_re', 'GTJA48', 'CorrCloseVol_Std_5', 'FIX_lly_17',
                           'RetAdjVolMeanSkew_1_1', 'MinDailyCorrHighVol_max5', 'FactorMin289_mean_re', 'FactorAlpha007Reg',
                           'FactorMin143_meandivstd', 'UpDownVolRatioStdRegbeta_5_1', 'OverBuySellStdRegbeta_5_5',
                           'FactorMin359_mean_div_std_re', 'FactorMin430_mean_div_std_re', 'FactorMin429_mean_div_std_re',
                           'RetAdjVolStdRegrmse_5_1', 'FactorAlpha024dif', 'AccelerateStdRE_std10', 'DivergWinLossRStdRegrmse_5_5',
                           'RetAdjVolMinRegrmse_3_5', 'RetAdjVolMeanSkew_1_5', 'UpDownCutSum', 'FIX_lly_43', 'FactorMin514_self_re',
                           'FactorMin53_mean_div_std', 'FactorMin441_self_re', 'DivergWinLossRMaxSkew_1_5',
                           'HighFreqRelativeTurnoverStd', 'HF_AmtStdStrengthDev_13h', 'GTJA16_max5', 'FactorMin446_mean_div_std_re',
                           'FactorAlpha006Reg', 'hfHighVolPVcorrsharpe', 'FactorMin177_mean_div_std_re', 'FactorMin126_std',
                           'FactorMin150_diff', 'RetAdjVolMeanSr_1_5', 'RetAdjVolMinStd_1_1', 'FactorMin199_meandivstd',
                           'FactorMin227_meandivstd', 'FactorMin126_mean', 'PriceVolume_10', 'FIX_lly_28',
                           'MinDailyCorrHighVol_std5', 'CRCS_raw_raw_std10', 'HF_VmL2HmVStdRatio', 'FactorMin285_self_re',
                           'CorrHighLowAvgToAmt_Mean_5', 'EVolChgStd_5_5', 'EVolChgSkew_1_30', 'FIX_lly_47', 'RetAdjVolStdSkew_1_5',
                           'FactorMin447_self_re', 'FactorAlpha061regrmse', 'RetAdjVolStdSr_3_5', 'RetAdjVolSkewRegbeta_5_5',
                           'FactorMin18_mean', 'DivergWinLossRMeanStd_5_5', 'MinuteTVRtnRank', 'FactorMin453_std_re',
                           'RetAdjVolKurtRaw_3_5', 'FactorMin76_mean', 'RetAdjVolSkewSr_3_5', 'RetAdjVolMinMean_1_5', 'CGO',
                           'FactorMin155_mean', 'FactorMin192_std_re', 'pureretrawms_rollingstd_5', 'FactorMin499_mean_div_std_re',
                           'FactorMinCor17_mean_re', 'FactorMinVaR_regrmse_05_10', 'RetAdjVolKurtRegbeta_3_5', 'FactorMin157_mean',
                           'FactorMin242_std_re', 'FactorMin155_meandivstd', 'FactorMin153_std', 'FactorMin362_std_re',
                           'FactorMinCor17_mean_div_std_re', 'FactorMin134_std', 'NewCorrHighVol', 'FactorAlpha040mean',
                           'FactorMin130_meandivstd', 'FIX_lly_22', 'RetRightTail', 'FactorMin165_mean',
                           'FactorMin361_mean_div_std_re', 'UpdownToStd', 'FactorMin416_mean_div_std_re', 'FactorMin335_std_re',
                           'FactorMin162_mean', 'FactorMin561_mean_div_std_re', 'FactorMin505_std_re', 'RetAdjVolSkewMean_1_1',
                           'FactorMin133_std', 'FactorMin218_meandivstd', 'RetAdjVolDifStd_1_1', 'FactorMinCor18_mean_div_std_re',
                           'FIX_lly_70', 'FactorMin75_std', 'HighV_meandivstd10', 'FactorMin83_mean', 'FactorMin81_std',
                           'FactorMin73_std', 'DivergWinLossRStdStd_5_15', 'FactorMin35_mean', 'FactorMin72_std',
                           'FactorMin157_meandivstd', 'GTJA53_ts_rank5', 'CRCS_raw_rank_ms10', 'GTJA43_min5',
                           'RollingCloseOpenWeightedCorr_5', 'GTJA54G', 'HighVStd_meandivstd10', 'PriceVolume_5', 'zhy_fix_5',
                           'RSRS_Mean_5', 'FactorMin201_mean', 'RetAdjVolMeanRegbeta_5_30', 'OverBuySell_Mean_5',
                           'FactorMin53_meandivstd', 'RetAdjVolMaxMean_1_5', 'FactorMin157_diffdivstd', 'FactorMin218_diffdivstd',
                           'HighFreqWaveRetStd', 'DivergWinLossRSkewMean_5_5', 'HFPVCorrMean', 'Beta5HighLow_Mean3',
                           'FactorMin166_std', 'DivergWinLossRStdSr_5_5', 'FIX_lly_34', 'RetAdjVolStdRegrmse_3_5',
                           'RollingCloseOpenWeightedCorr_10', 'FactorMin72_mean', 'IdeaVSkewMean', 'IdeaVStdReg', 'IdeaVStdMax',
                           'FactorMin66_mean', 'RetAdjVolMaxSr_3_5', 'FactorMin160_mean', 'FIX_lly_50', 'FactorAlpha079max',
                           'TurnHighStd_meandivstd', 'FactorMin164_std', 'HF_CloseLowHighStdVolumeRatio_13h', 'FactorMin35_diff',
                           'CorrCloseVol_Mean_5', 'HF_VwapTailTRRatio_13h', 'FactorMin81_diff_div_std', 'MinVwapHLRateBetaBias',
                           'FactorMin503_std_re', 'pureretrawskew_rollingstd_5', 'NormalCloseAmtCorrDecay10d', 'IdeaVKurtReg',
                           'VarResampleMean_max10', 'FactorMin165_std', 'FactorMin161_std', 'FactorMin18_meandivstd',
                           'FactorMin164_mean', 'AvgStdRatioRE_regrmse10', 'FactorMin171_meandivstd', 'CRCS_raw_rank_skew10',
                           'GTJA5', 'TurnWeiRet10slope', 'FactorMin162_std', 'FactorMin163_mean', 'pureretraw_rollingstd5',
                           'er_percrank_raw_std_short', 'RSJT', 'UBL10std', 'IdeaVStdL_mean10', 'FactorMin235_std',
                           'FactorMin236_std', 'IdeaVStdL_meandivstd10', 'er_percrank_raw_std', 'NewCorrHighVol_meandivstd5',
                           'CResidualMoment']
factor_eval = pd.read_pickle(local_config_path + 'check/test_result_mv.pkl').set_index('name')
factor_eval = factor_eval.loc[list(set(factor_eval.index).intersection(set(availabel)))]
factor_eval.loc[:, ['ic_all_t', 'ic_all_d', 'ic_all_d']] = abs(factor_eval.loc[:, ['ic_all_t', 'ic_all_d', 'ic_all_d']])

factor_all = set([])
factor = {}
for each in ['ic_all_t', 'ic_all_d', 'ic_all_c']:
    factor[each] = sorted(factor_eval[each].sort_values(ascending=False).index.tolist()[:400])
    factor_all = factor_all.union(set(factor[each]))

for each in factor:
    pd.to_pickle(factor[each], local_config_path + '%s_400_factor_list14_20.pkl' % each)

pd.to_pickle(sorted(list(set(factor_all))), local_config_path + 'using_fix_list14_20.pkl')

check_factor_all = set([])
for each in factor:
    temp = pd.read_pickle(local_config_path + '%s_400_factor_list14_20.pkl' % each)
    check_factor_all = check_factor_all.union(set(temp))

d_ = set(pd.read_pickle('/data/group/800319/strategy_local_path/ic_all_d_400_factor_list14_20.pkl'))
t_ = set(pd.read_pickle('/data/group/800319/strategy_local_path/ic_all_t_400_factor_list14_20.pkl'))
c_ = set(pd.read_pickle('/data/group/800319/strategy_local_path/ic_all_c_400_factor_list14_20.pkl'))

d = set(pd.read_pickle('/data/group/800319/strategy_local_path2/ic_all_d_400_factor_list.pkl'))
t = set(pd.read_pickle('/data/group/800319/strategy_local_path2/ic_all_t_400_factor_list.pkl'))
c = set(pd.read_pickle('/data/group/800319/strategy_local_path2/ic_all_c_400_factor_list.pkl'))


def get_available_factor_list(path):
    import os
    file_list = os.listdir(path)
    file_list = [x[8:-4] for x in file_list]
    return file_list


set(factor_list) - set(get_available_factor_list('/data/group/800002/realtime/alpha//x_day_lib/20210115/1100/')) \
    (set(factor_list) - set(get_available_factor_list('/data/group/800002/realtime/alpha//x_day_lib/20201026/1100/')))
