# @Time : 2020/12/14 13:03
# @Author : Zhichen Lu
# @File : ts_factor_reload.py

import numpy as np
import pandas as pd
import os
import time
factor_list = ['CorrMaxRePriceRank', 'TwapSkewToVwap', 'hfCPVCorrHD_13h', 'HFPSCorr', 'CorrCloseVol_Mean_1', 'CRCS_raw_rank_ms10', 'dailyms_intraday_5', 'CorrDelVolumePriceMean', 'subrr2adjwms_intraday_5', 'VwapSwingCorr', 'SplitVolumeRatio', 'WRMean5d_13h', 'TemporalVolumePriceCorr', 'hfMktLSCapSR', 'LogDeltaVol', 'WR_13h', 'MinVwapHLRateBetaDelta', 'HF_PriceDiffRatio', 'Min1WeightedFlow_1', 'PDS', 'GTJA2', 'MinuteVolatilityPriceCorr', 'CorrAmpVwap_1', 'VolBurstReturn', 'StdUpDown', 'MinCorrAbsRePriceRank2D', 'L2C5', 'FactorAlpha027', 'WilliamsPriceVolCorrMultiple_13h', 'MinPriceAutoCorr', 'HF_OpenVwapSkew', 'MinMaxRet', 'HF_MeanIntradayReturnAcrossLosingInvestors_13h', 'Ret30RankMean_5', 'FactorMin129_diff', 'HFPVCorr', 'FWRMin', 'MinCapitalGainOverhang', 'HFPVCorrStdAdj', 'HF_VwapTopTRRatio_13h', 'hfPVcorrHD', 'HighCloseDistance', 'VolaDownward20', 'Close2BarHigh', 'sistdwfiavg2_3_re', 'adjstdstm_intraday_5', 'CorrHighLowAvgToAmt_Mean_1', 'HF_RetHHIZscore', 'HF_RSRSZScore', 'HLTR_mean5_intraday', 'FactorMin87_diff', 'MinVwapHLRateBetaBias', 'PVSwingCorr', 'HF_VwapAmtUpCorrInLowVolatility_13h', 'WR2d_13h', 'Close2High', 'HF_DVwapDVolumeCorrZscore_13h', 'MinPre30mAutoCorr', 'VwapStdCorrDistanceLow10d_13h', 'HighLowVwapRatio', 'MinCapitalGainBetaEwm', 'HighLowMeanVwapRetSharpe', 'LogRtn2Amt5', 'PriceDeviationBias10d', 'CloseExcessPercent_1', 'FactorMin450_mean_re', 'FactorMin70_diff', 'WilliamUp_diffstd5', 'VolumeUpPVCorr_13h', 'HfSwingCloseCorr', 'WilliamsIndicator_13h', 'HF_WR2d', 'CGO', 'CorrVWAPdt', 'adjEMAbc_intraday5', 'PriceRange_5', 'MinExtremRet', 'ReLow_13h', 'SwingPriceCorr', 'VwapBollingerBand30min_13h', 'HF_ForecastEPDelta40d', 'HFPSCorrStdAdj', 'MaxDrawDown', 'HighFreqRelativeClose', 'hfMktLSCap', 'FactorMin215_mean', 'Ret30Mean2Std_10', 'RevExclu4mean', 'WAPResistBackTop_13h', 'HF_RSRS', 'HF_CorrMaxVolumeZScore_13h', 'MinCorrVolumePrice_1', 'VwapStdCorrBias20d_13h', 'GTJA27_weight12', 'HF_VmL2HmVStdRatio', 'DrawdownSkew', 'RSRS_Mean_1', 'SignDownWick', 'MinPrePriceAutoCorr', 'HighLowStdBias20d', 'VwapmaLowDiffSkew_13h']

path = '/data/group/800319/LittleJunkFix/'
out_path = '/data/group/800319/TSLittleJunkFix/'

idx_address = path
idx_date = np.load('%s/idx_date.npy' % idx_address).tolist()
idx_time = np.load('%s/idx_time.npy' % idx_address).tolist()
idx_code = np.load('%s/idx_code.npy' % idx_address).tolist()
idx_len = len(idx_date)

factor_name = factor_list[0]

factor = np.load('%s/%s.npy'%(path,factor_name))

e = time.time()
factor_df = pd.DataFrame([idx_date,idx_time,idx_time,factor.tolist()],index=['date','time','code',factor_name])
factor_df = pd.DataFrame([idx_date,idx_time,idx_time])
print(time.time() - e)
# factor_df = factor_df.pivot_table(index=['date','time'],columns='code',values=factor_name)