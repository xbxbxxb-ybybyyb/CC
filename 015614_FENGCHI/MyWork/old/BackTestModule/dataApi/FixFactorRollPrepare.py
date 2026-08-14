from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from tqdm import tqdm
import numpy as np
import time

class FixFactorRollPrepare(object):

    def __init__(self, start_date=20140801, end_date=20201031, freq=7, model_time_len=7, factor_list=None,
                 load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):

        idx_date = np.load('%s/idx_date.npy' % load_address)
        idx_time = np.load('%s/idx_time.npy' % load_address)
        idx_code = np.load('%s/idx_code.npy' % load_address)

        _select = (idx_date >= start_date) & (idx_date <= end_date)
        idx_date = idx_date[_select]
        idx_code = idx_code[_select]
        idx_len = idx_date.shape[0]
        time_len = idx_time.shape[0]

        date_list = get_date_range(start_date, end_date)
        start_date = max(date_list[0], idx_date[0])
        end_date = min(date_list[-1], idx_date[-1])
        date_list = get_date_range(start_date, end_date)

        date_list_index = (np.r_[1, np.diff(idx_date)] > 0) & (idx_date >= start_date) & (
                idx_date <= get_pre_trade_date(end_date, -1))
        date_list_index = np.arange(date_list_index.shape[0])[date_list_index]
        date_list_index = date_list_index if date_list[-1] < idx_date[-1] else np.r_[
            date_list_index, len(idx_date)]

        if not isinstance(factor_list, list):
            raise ValueError("Factor list must be given.")
        factor_num = len(factor_list)

        self.idx_date = idx_date
        self.idx_time = idx_time
        self.idx_code = idx_code
        self.idx_len = idx_len
        self.time_len = time_len
        self.date_list = date_list
        self.start_date = start_date
        self.end_date = end_date
        self.freq = freq
        self.model_time_len = model_time_len
        self.factor_list = factor_list
        self.factor_num = factor_num
        self.load_address = load_address
        self.date_list_index = date_list_index

    def load_data(self, start_date, end_date=0, future_end=True, return_idx=False):

        start_idx = self.date_list_index[self.date_list.index(start_date)]
        end_idx = self.date_list_index[self.date_list.index(end_date) + 1]
        future_end_idx = end_idx if future_end else self.date_list_index[self.date_list.index(end_date)]
        future_idx_len = self.idx_date[self.idx_date <= end_date].shape[
            0] if future_end else self.idx_date[self.idx_date < end_date].shape[0]
        X = np.empty((self.factor_num, end_idx - start_idx, self.freq + self.model_time_len - 1), dtype=np.float32)

        # for idx in range(self.factor_num):
        for idx in tqdm(range(self.factor_num), desc='Factor_loading...'):
            fp = np.memmap('%s/%s.npy' % (self.load_address, self.factor_list[idx]),
                           dtype='float32', mode='r', shape=(self.idx_len, self.time_len), offset=128)
            X[idx] = fp[start_idx: end_idx, 1 - self.freq - self.model_time_len:]
            del fp

        y = np.memmap('%s/%s.npy' % (self.load_address, 'future'),
                      dtype='float32', mode='r', shape=(future_idx_len, self.freq), offset=128)
        y = y[start_idx: future_end_idx]

        nolimit = np.memmap('%s/%s.npy' % (self.load_address, 'nolimit'), dtype='bool', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        nolimit = nolimit[start_idx: end_idx]

        if not return_idx:
            return X, y, nolimit
        else:
            idx_date = self.idx_date[start_idx: end_idx, None].repeat(self.freq, axis=1)
            idx_code = self.idx_code[start_idx: end_idx, None].repeat(self.freq, axis=1)
            idx_time = self.idx_time[None, -self.freq:].repeat(idx_date.shape[0], axis=0)
            return X, y, nolimit, idx_date, idx_time, idx_code

    def load_custom_pool(self, pool_name, start_date, end_date=0):

        if pool_name[0] != '_':
            raise ValueError('Name of custom pool must start with _ to be different from normal factors.')

        start_idx = self.date_list_index[self.date_list.index(start_date)]
        end_idx = self.date_list_index[self.date_list.index(end_date) + 1]

        custom_pool = np.memmap('%s/%s.npy' % (self.load_address, pool_name), dtype='bool', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        custom_pool = custom_pool[start_idx: end_idx]

        return custom_pool

    def feature_engineering(self, X, y, nolimit, *args, limit=0.2, custom_pool=None):

        if self.model_time_len > 1:

            X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], self.freq, X.shape[2] - self.freq + 1),
                                                strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)

        else:
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], self.model_time_len).transpose(1, 2, 0)

        y = y.flatten()
        nolimit = nolimit.flatten()
        valid = (np.isclose(X, 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y) & nolimit

        if custom_pool:
            valid &= custom_pool

        valid_samples = valid.sum()
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
            valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

        X = X[valid]
        y = y[valid]

        dic = {}
        for arg in range(len(args)):
            dic[arg] = args[arg].flatten()[valid]

        if self.model_time_len == 1:
            X = X[:, 0]

        return (X, y) + tuple(dic.values())


def load_fix_data(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                  model_time_len=1, freq=7, address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'):

    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    idx_time = np.load('%s/idx_time.npy' % address)

    time_len = idx_time.shape[0]

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_code = idx_code[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_time = idx_time[None, 1 - freq - model_time_len:].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // freq - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(factor_list), len(choose), freq + model_time_len - 1), dtype=np.float32)
    y = np.empty((len(choose), freq), dtype=np.float32)
    nolimit = np.empty((len(choose), freq), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[j] = fp[choose, 1 - freq - model_time_len:]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, :]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{address}/nolimit.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, :]
        nolimit[real_y_shape:] = False

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit


def load_fix_mv(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                address='/data/group/800319/HFfactor/RealTimeFixRollRobust/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/data/idx_date.npy' % address)
    idx_code = np.load('%s/data/idx_code.npy' % address)

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose]
        idx_code = idx_code[choose]

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    mean = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    std = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/mean/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        mean[j] = fp[choose]
        del fp

        fp = np.memmap(f'{address}/std/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        std[j] = fp[choose]
        del fp

    if return_idx:
        return mean, std, idx_date, idx_code
    else:
        return mean, std

def feature_engineering(X, y, nolimit, *args, limit=0.2, model_time_len=1, freq=7):

    if model_time_len > 1:
        X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], freq, X.shape[2] - freq + 1),
                                            strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)

    else:
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], model_time_len).transpose(1, 2, 0)

    y = y.flatten()
    nolimit = nolimit.flatten()
    valid = ((X == 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y) & nolimit

    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

    X = X[valid]
    y = y[valid]

    dic = {}
    for arg in range(len(args)):
        dic[arg] = args[arg].flatten()[valid]

    if model_time_len == 1:
        X = X[:, 0]

    return (X, y) + tuple(dic.values())


# if __name__ == '__main__':
#     # end_date = min(get_recent_trade_date(None), get_pre_trade_date(dividing_point=19))
#     # self = FixFactorRollPrepare(20140801, 20140901, 7, 1, ['AbnormVVolClosemean_rollingmax_3'])
#     # self.load_data(20140801, 20140901)
#     # start_date = 20210310
#     # end_date = 20210310
#     # future_end = False


# factor_list = ['AbnormalPriceDiff', 'AggressionNMean_1_1', 'AggressionNRank_5_1', 'AggressionNRank_5_5', 'AggressionPRaw_3_5',
#  'AmtPct_Mean_1', 'AvgPriceVwapRateSharpe5d', 'BAStrength', 'BSPowerSkew3mean', 'BestWorstReSharpe5d', 'Beta300',
#  'Beta500d3', 'CGO', 'CRCS_raw_rank_ms10', 'CSAD5mean', 'Close2BarHigh', 'Close2High', 'CloseExcessPercent_1',
#  'CloseSkew_Mean_5', 'CloseVolumeCorrBias20d', 'CloseVwapRetSkew', 'ConsRetStd3std', 'Cor300Down5mean', 'Cor500D3',
#  'CorPV5', 'CorrAbsWRPrice5min', 'CorrAmpAmt_1', 'CorrAmpAmt_5', 'CorrAmpRet_5', 'CorrAmpVwap_1', 'CorrAmpVwap_5',
#  'CorrCloseVol_Mean_1', 'CorrExcessRank2', 'CorrHighLowAvgToAmt_Mean_1', 'CorrHighLowAvgToAmt_Mean_5',
#  'CorrMaxRePriceRank', 'CorrPVLowLiquidity', 'CorrRetVol_5', 'CorrVWAPBollingUpDown', 'CorrVWAPTrendHigh',
#  'CorrVwapVol_1', 'CorrVwapVol_5', 'CorrWRPriceRank', 'DIFDifSr_1_5', 'DIFMeanRaw_5_5', 'DIFMeanRegbeta_5_30',
#  'DIFSkewMean_1_1', 'DIFSkewMean_5_5', 'DIFSkewRank_5_1', 'DIFStdSr_5_1', 'DisNMean_1', 'DisNRaw_5', 'DisNRegbeta_5',
#  'DisPRaw_5', 'DisPSr_1', 'DivergWinLossRKurtRegrmse_5_5', 'DivergWinLossRMeanRank_5_5', 'DivergWinLossRMeanStd_5_5',
#  'DivergWinLossRSkewRegrmse_5_5', 'DivergWinLossRStdRegbeta_5_15', 'DivergWinLossRStdRegrmse_5_5',
#  'DivergWinLossRStdStd_5_15', 'DrawdownSkew', 'EVolChgBetaAbs_1_1', 'Excess300High5', 'Excess500High5',
#  'ExcessBollingUpRateMean5d', 'FIX_lly_12', 'FIX_lly_8', 'FSmartMax', 'FSmartMin', 'FWRM', 'FWRMin',
#  'FactorAlpha007', 'FactorAlpha024', 'FactorAlpha024dif', 'FactorAlpha027', 'FactorAlpha040mean',
#  'FactorMin13_mean', 'FactorMin143_meandivstd', 'FactorMin14_diff', 'FactorMin150_diff', 'FactorMin155_meandivstd',
#  'FactorMin163_mean', 'FactorMin164_mean', 'FactorMin165_mean', 'FactorMin193_mean_re', 'FactorMin193_std',
#  'FactorMin1_diff_div_std', 'FactorMin217_mean_re', 'FactorMin285_std_re', 'FactorMin33_mean', 'FactorMin33_std',
#  'FactorMin343_mean_re', 'FactorMin343_self_re', 'FactorMin359_mean_div_std_re', 'FactorMin35_diff', 'FactorMin35_std',
#  'FactorMin383_mean_div_std_re', 'FactorMin384_mean_re', 'FactorMin3_std', 'FactorMin403_mean_re',
#  'FactorMin405_mean_div_std_re', 'FactorMin405_std_re', 'FactorMin409_mean_div_std_re', 'FactorMin412_mean_div_std_re',
#  'FactorMin42_mean', 'FactorMin430_mean_div_std_re', 'FactorMin450_mean_re', 'FactorMin453_std_re',
#  'FactorMin53_mean_div_std', 'FactorMin6_mean', 'FactorMin76_mean', 'FactorMin81_std', 'FactorMin82_mean',
#  'FactorMin87_diff', 'FactorMin93_diff', 'FactorMinKdayShortCut_regrmse', 'FactorMinKdayShortCut_std',
#  'FactorMinVaR_regrmse_05_10', 'Factor_Fix_zhy_101', 'Factor_Fix_zhy_208', 'Factor_Fix_zhy_66', 'GTJA14_std5',
#  'GTJA16_min5', 'GTJA17_bias5', 'GTJA2', 'GTJA20_std5', 'GTJA32', 'GTJA41', 'GTJA62', 'GTJA8', 'GTJA8_mean5',
#  'HFPSCorr', 'HFPSCorrBias', 'HFPSCorrMinAdj', 'HFPSCorrStdAdj', 'HFPTSCorrBias', 'HFPTSCorrStdAdj', 'HFPVCorr',
#  'HFPVCorrBias', 'HFPVCorrMinAdj', 'HFPVCorrStdAdj', 'HF_Amt10mSkew20d', 'HF_AmtDeg1', 'HF_AmtStdStrengthCloseBias',
#  'HF_AmtStdStrengthCloseChange_13h', 'HF_AmtStrengthCloseChange_13h', 'HF_AmtVolatilityPriceCorr_13h',
#  'HF_CorrMaxVolumeZScore_13h', 'HF_HighVwapSkew_13h', 'HF_Hl2OStrength_13h', 'HF_HmL2CVwapCorrZscore_13h',
#  'HF_HmL2CVwapCorr_13h', 'HF_IlliqShortcut_13h', 'HF_LDeg1_13h', 'HF_LowHighStdRatio_13h',
#  'HF_MeanIntradayReturnAcrossLosingInvestors_13h', 'HF_NormRePriceCorrSharpe_13h', 'HF_OpenVwapSkew',
#  'HF_RSRS', 'HF_RSRSZScore', 'HF_RetHHIZscore', 'HF_RetTopVwapAmtCorrBias', 'HF_UpRetAmtSkew',
#  'HF_VmL2HmVStdRatio', 'HF_VmL2HmVStdRatio10minBias', 'HF_VolumeStrengthCloseStdBias', 'HF_VolumeStrengthDeg1',
#  'HF_VolumeTopVwapRatio', 'HF_VwapAmtUpCorrInLowVolatility_13h', 'HF_VwapBollingUp_13h',
#  'HF_VwapHighStdVolumeRatioZscore_13h', 'HF_VwapLowVR_13h', 'HF_VwapStdSwingCorrZscore_13h',
#  'HF_VwapTailVolumeRatio_13h', 'HF_VwapTopTailAmtRatio_13h', 'HF_VwapTopTailTurnRatioZscore',
#  'HF_VwapTopTailVolumeStdRatio_13h', 'HF_VwapTopTailVolume_13h', 'HF_VwapTopVolumeRatioZscore_13h',
#  'HLLength5', 'HLOKurt3', 'HLStd1mean', 'HLStdRatio', 'HfHalfDayCloseRtnCountDiffBias_13h',
#  'HfHalfDayCloseRtnCountDiff_13h', 'HfLast120HighLowDiffAmtCloseCorrPreBias', 'HfLast120LongTurnSkew_13h',
#  'HfLast120MaxRtnCloseCorrBias_13h', 'HfLast120MinRtnCloseCorrSharpe', 'HfLast120RtnPerAmtVolCorr',
#  'HfLast60TurnVolCorr', 'HfLongVwapSwingCorr5d', 'HfLongVwapSwingCorrBias', 'HfRtnPerAmtVolCorr',
#  'HfSwingCloseCorr', 'HfTopRtnVolumeRatioMean', 'HfVolSkew', 'High2LowVolDown', 'High2Low_5', 'HighCloseDistance',
#  'HighFreqDownSpeed', 'HighFreqDrawBackMeanBias', 'HighFreqDrawBackStdBias', 'HighFreqHighMARetCorr',
#  'HighFreqRelativeClose', 'HighFreqSwingStdCmp', 'HighFreqVHFCorrBias', 'HighLowMeanVwapRetSharpe',
#  'HighLowStdLowDistance10d', 'HighLowVwapDiffStdRatio', 'HighLowVwapRatio', 'HighSkew_Mean_5', 'IdeaVStdL_mean10',
#  'IdealRev2', 'IndustryExcessPVCorrBias5d', 'L2C5', 'LargeSmallVolumeVWAPRatio', 'Last30MaxDrawdownBias20d',
#  'Last30minReVolumeCorrMean5d', 'LatestRetRatio', 'LiqUp5', 'LogAmt_1', 'LogAmt_5', 'LogDeltaVol_meandivstd10',
#  'LogFreeTurn_1', 'LogFreeTurn_5', 'LogRtn2Amt5', 'LowSharpeAmountStdRatio', 'LowStdRatio_max5', 'MACDEChgStd_5_1',
#  'MACDNumDiff_5_5', 'MaxDrawDown', 'MeanRatio_min5', 'MinCapitalGainAbs', 'MinCapitalGainBetaEwm',
#  'MinCapitalGainBetaZscore', 'MinCapitalGainOverhang', 'MinCapitalGainRH', 'MinCorrAbsRePriceRank2D',
#  'MinCorrExcessPriceRank', 'MinCorrVolumePrice_1', 'MinDailyCorrCloseVol', 'MinDailyCorrCloseVol_min5',
#  'MinDirectedVol', 'MinExtremRet', 'MinMaxRet', 'MinPVCorr', 'MinPre30mAutoCorr', 'MinPre30mAutoCorrDelta',
#  'MinPre5mSkew', 'MinPreTopVolRate', 'MinVwapHLRateBetaBias', 'MinVwapHLRateBetaDelta', 'MinuteTVRtnRank',
#  'MinuteVolatilityPriceCorr', 'NetworkDegree3', 'NetworkDegree3Net', 'NetworkPremium3', 'OTC5std',
#  'OverBuySellSkewRegbeta_5_5', 'OverflowPerAmtMean5d', 'PDSS', 'PVSwingCorr', 'PriceDeviationBias10d',
#  'PriceRange_5', 'PriceSkew', 'PriceUpDownRatio', 'RSIMeanRegbeta_5_15', 'RSIMeanRegrmse_1_15', 'RSIMinMean_1_15',
#  'RSIStdRank_5_5', 'RSRS_Mean_1', 'RS_mean', 'ReLow_13h', 'Ret30Mean2Std_10', 'Ret30RankMean_5', 'RetAdjVolMaxMean_1_5',
#  'RetAdjVolMeanRank_3_5', 'RetAdjVolMeanSkew_1_5', 'RetAdjVolMeanSr_1_5', 'RetAdjVolSkewRaw_1_1',
#  'RetAdjVolSkewRegbeta_5_5', 'RetBigStdResAmt5', 'RetGather0p9mean5', 'RetTurnCorr', 'RetUpSR',
#  'RetUpWeightedByVolSR', 'RetVolCVMultiple', 'RetVolMeanSr_1_1', 'RetVolSkewMean_1_5', 'RevExclu4mean',
#  'RollingCloseOpenWeightedCorr_10', 'RollingCorrCloseVolume', 'Rtn2VolumeStd5', 'SharpeDuringAmountDrop',
#  'SharpeDuringStdDrop', 'ShortTurn', 'SignDownWick', 'SignedVolume', 'SplitVolumeStdDownRatio', 'StdAmountDiff',
#  'StdHmL_20', 'StdUpDown', 'SwingPriceCorr', 'TemporalVolumePriceCorr', 'TopAmountRatioVolumeDiffSharpe',
#  'TrendStrength', 'TurnHighKurtRollingStd', 'TurnStd', 'TurnStdPure3mean', 'TurnStdPure5std', 'TurnWeiRet10slope',
#  'TurnWeiRet3mean', 'TurnWeiRet3min', 'TurnWeiRet5min', 'TwapSkewToVwap', 'UDContrast5mean', 'UpDownAmtRatioKurtSr_5_5',
#  'UpDownAmtRatioStdMean_1_5', 'UpDownVolRatioStdRaw_1_1', 'UpDownVolRatioStdRegbeta_5_1', 'UpDownVolRatioStdRegbeta_5_5',
#  'UpToRetValue', 'VHighKurt', 'VNSPMean_1_5', 'VarResampleMean_max10', 'VolChg1Mean', 'VolMeanSharpeUp_13h',
#  'VolSharpeUp_13h', 'VolSkew', 'VolaDownward20', 'VolumeDownChange_13h', 'VolumeMax10min2All_13h', 'VwapAmtCorrMean5d_13h',
#  'VwapStdCorrBias20d_13h', 'VwapStdCorrDistanceLow10d_13h', 'VwapSwingCorr', 'VwapmaLowDiffSkew_13h',
#  'WAPResistBackRatio_13h', 'WAPResistBackStd_13h', 'WL350_5', 'WR2d_13h', 'WRMean5d_13h', 'WR_13h',
#  'WeightedFlow_1', 'WilliamUp_diffstd5', 'WilliamsIndicator_13h', 'WilliamsPriceVolCorrMultiple_13h',
#  'adjEMAbc_intraday5', 'adjdmstdcpt_intraday_5', 'adjstdsd_intraday_5', 'adjstdstm_intraday_5',
#  'adjstdwms_intraday_5', 'amtavg_mktstate_amt_std_topskew_5_3', 'amtavg_ntdmkurt_20_10', 'amtavg_ntdmkurt_60_10',
#  'amtkrt_ntrdmmean_20_10', 'amtkrt_ntrdmmean_60_10', 'cummaxdd_ntmaxstd_20_3', 'cummaxdd_nttrbmean_20_10',
#  'cummaxdd_nttrbmean_20_3', 'dailyms_intraday_5', 'dretvolnew_bwkurtmean_20_10', 'dretvolnew_bwmeanskew_20_10',
#  'dretvolnew_bwskewmean_20_3', 'dretvolnew_ntdmstd_60_10', 'dretvolnew_ntkurtmean_20_10',
#  'dretvolnew_ntkurtskew_20_10', 'dretvolnew_ntrdmmean_60_3', 'dretvvolnew_bwmeanskew_60_10',
#  'dretvvolnew_bwstdkurt_60_10', 'dretvvolnew_ntmeanskew_60_10', 'dretvvolnew_ntskewmean_20_10',
#  'dretvvolnew_ntstdkurt_20_10', 'hfCPVCorrHDmean_13h', 'hfDownPVcorr5', 'hfDownPVcorrbias', 'hfDownStrength',
#  'hfHVR5', 'hfHighVolPVcorr5', 'hfIdxCorr', 'hfIdxCorr5', 'hfLowCapRetMin', 'hfMktLSCapMR5', 'hfMktLSCapSR',
#  'hfPVcorrHD', 'hfRST', 'hfTurnSharpeHD', 'hfUpRRCbias', 'sistdwfiavg2_3_re', 'sistdwfiavg_re',
#  'subrr2adjwms_intraday_5', 'subrradjwms_intraday_5', 'uretvolnew_ntdmstd_20_10', 'uretvvolnew_ntdmkurt_20_10',
#  'uretvvolnew_ntmsmean_20_10', 'zhy_fix_146', 'zhy_fix_5']
#
# mean, std, idx_date, idx_code = load_fix_mv(20210415, 20210415, factor_list)
#
# import pandas as pd
# from dataApi.stockList import trans_windcode2int
# mean1 = pd.read_pickle('/data/group/800319/strategy_local_path3/factor_hyper_param/mean20210414.pkl')
# mean1.columns = mean1.columns.map(trans_windcode2int)
# mean1 = mean1.reindex(factor_list, idx_code).values
# X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(20200619, 20200619, factor_list)
# X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time)
#
# from dataApi.sendInfo import send_file
# send_file('015664', '/data/user/015836/HANXU/alphaResearch/dataUpdate/TSmodel/BaseModel/FixFactorRollPrepare.py')