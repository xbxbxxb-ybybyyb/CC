import bottleneck
import pandas as pd
import numpy as np
from tqdm import tqdm
import xgboost as xgb
from sklearn import cross_validation, metrics
from sklearn.linear_model import LinearRegression, Lasso, Ridge, RidgeCV
from sklearn.model_selection import GridSearchCV
from dataApi.tradeDate import get_pre_trade_date
from dataApi.stockList import clean_stock_list
from dataApi.nonFactorTest1 import NonFactorTest
from model.preprocess import load_future, standardize, multiprocess
from model.select import factor_select


def get_metric(score, model_days, code_num, pool, ret):
    fit = np.full(model_days * code_num, np.nan)
    fit[pool.flatten()] = score
    fit = fit.reshape(model_days, code_num)
    fit = (bottleneck.nanrankdata(fit, axis=1).T / pool.sum(axis=1)).T
    ret_top = ret.copy()
    ret_top[fit <= 0.9] = np.nan
    weight = np.logspace(model_days, 0, model_days, base=0.99)
    weight /= weight.sum()
    metric = (np.nanmean(ret_top, axis=1) - np.nanmean(ret, axis=1)).dot(weight)
    return - metric


def get_score(alpha, feature, label):
    reg = Ridge(alpha=alpha).fit(feature, label)
    score = reg.predict(feature)
    return score


def single_param_search(feature, label, model_days, code_num, pool, ret, start=100., lr=100, tol=1e-10, max_iter=100):
    x0 = start
    score = get_score(x0, feature, label)
    metric = get_metric(score, model_days, code_num, pool, ret)
    print(x0, metric)
    y0 = metric

    x1 = start + lr
    score = get_score(x1, feature, label)
    metric = get_metric(score, model_days, code_num, pool, ret)
    print(x1, metric)
    y1 = metric

    while y1 <= y0:

        lr *= 2
        x2 = start + lr
        score = get_score(x2, feature, label)
        metric = get_metric(score, model_days, code_num, pool, ret)
        print(x2, metric)
        y2 = metric
        if y2 > y1:
            x1 = x2
            break
        x0 = x1
        x1 = x2
        y0 = y1
        y1 = y2

    i = 0
    while i < max_iter:

        i += 1
        x2 = (x0 + x1) / 2
        score = get_score(x2, feature, label)
        metric = get_metric(score, model_days, code_num, pool, ret)
        print(i, x2, metric)
        y2 = metric
        if abs(y2 / y0 - 1) < tol:
            return x0
        elif y2 > y0:
            x1 = x2
        else:
            x3 = x2 + (x1 - x2) / 100
            score = get_score(x3, feature, label)
            metric = get_metric(score, model_days, code_num, pool, ret)
            y3 = metric
            if y3 <= y2:
                x0 = x3
                y0 = y3
            else:
                x1 = x2


def interpolation_search(feature, label, model_days, code_num, pool, ret, init, point=2, tol=1e-10, max_iter=20):
    x = init
    y = [get_metric(get_score(alpha, feature, label), model_days, code_num, pool, ret) for alpha in x]

    y0 = min(y)
    x0 = x[y.index(y0)]

    x1 = [i for i in x if i < x0]
    x2 = [i for i in x if i > x0]

    x = []
    if len(x1) > 0:
        x1 = max(x1)
        x1 = [x1 + (x0 - x1) * (i + 1.) / (point + 1.) for i in range(point)]
        x += x1
    if len(x2) > 0:
        x2 = max(x2)
        x2 = [x0 + (x2 - x0) * (i + 1.) / (point + 1.) for i in range(point)]
        x += x2

    y = [get_metric(get_score(alpha, feature, label), model_days, code_num, pool, ret) for alpha in x]
    print(y)
    y1 = min(y)
    x1 = x[y.index(y1)]

    iter = 0
    while iter < max_iter:
        iter += 1
        if x0 < x1:
            x = [x0, x1]
            y = [y0, y1]
        else:
            x = [x1, x0]
            y = [y1, y0]

        x_ = [x[0] + (x[1] - x[0]) * (i + 1.) / (point + 1.) for i in range(point)]
        y_ = [get_metric(get_score(alpha, feature, label), model_days, code_num, pool, ret) for alpha in x_]

        x += x_
        y += y_

        print(x, y)

        y0 = min(y)
        x0 = x[y.index(y0)]

        y.remove(y0)
        x.remove(x0)

        y1 = min(y)
        x1 = x[y.index(y1)]

        if (abs((y0 - y1) / (y0 + y1)) < tol) | (x == init):
            return x1 if y1 <= y0 else x0
            break
        init = x.copy()


middle_address = '/data/user/015836/model/temp20200513/'
compound_address = '/data/user/015836/model/compound/'

start_date = 20140102
end_date = 20181228

factor_list = [
    'APB1m_Mean5d',
    'APB5d',
    'APB5m_Mean5d',
    'AbnAmtRet',
    'AbnormalVolRaiseMom20d',
    'AbsRet2Deal',
    'AgainstBeta',
    'Aktr',
    'AmPmDiff',
    'AmihudLast120min10d',
    'AmtDealReDiff5d',
    'AmtEhdReverse',
    'AmtPerDealRetCorr',
    'AmtPerTradeInOutflow5d',
    'AmtPerTradeReSkew20d',
    'AmtPerTradeWeightedReturn',
    'AmtPerTradeWeightedReturn5d',
    'AmtRatioEntropy',
    'AmtRet',
    'AmtRet20d',
    'AmtRet5d',
    'AmtSkew3Day',
    'AmtStdBias',
    'AmtStdMean60d',
    'AmtStd_Mean2Std_5',
    'AmtVolStdRankMean5d',
    'AtrRetCorr',
    'AvgClose2Vwap_Std_5',
    'BeforehandRetCut20',
    'BeforehandRetCut30',
    'BeforehandRetResidual30',
    'BigOrderNetInflowRate5d',
    'BigOrderReturn20d',
    'BigPlayersTurnover',
    'BigPlayersVwap',
    'BoolDW',
    'BuyAmtStd3Day',
    'C9_DIFF60',
    'CEMV_CS30_SR20',
    'CEMV_CS30_Skew40',
    'CEMV_Skew40',
    'CEMVsharpe',
    'CEMVstd',
    'CSTurnpureCorrRet',
    'CSTurnpureCorrRetSharp',
    'CancelRateStd20d',
    'CapVolume',
    'CapVolumeRR',
    'CloseCorrTurnR2',
    'CloseOpenVolumeCorr',
    'ClosePercent2Journey',
    'ClosePercentDeal5d_up',
    'ClosePercentRank10d_up',
    'ClosePercentRank5d',
    'ClosePercentSharpe5d',
    'ClosePercentSwing5d',
    'ClosePercentUp5d',
    'CloseVolatility5d',
    'CloseVwapRetKurt',
    'CorrCloseRankTurn20d',
    'CorrCloseTurn10d_max',
    'CorrCloseTurn5d_max',
    'CorrCloseVol_Std10',
    'CorrCloseVol_Std_5',
    'CorrCloseVolumeSharpe',
    'CorrDelVolumePriceSharpe5d',
    'CorrDownVolumeSharpe',
    'CorrPVTUpCloseSharpe20d',
    'CorrRetAmtPct_CS15',
    'CorrRetVol_Mean_5',
    'CorrTurnPrice10min5dSharpe',
    'CorrVolReturn5d',
    'CsResidualSkew',
    'CumretClseSlope_60',
    'CybzCorrClose',
    'DailyPrfLP_6',
    'DavisWin',
    'DealnumSharpe',
    'DebtToAsset_std_3y',
    'DeltaTurnSkew',
    'DivMulStaVol',
    'DownSpeed',
    'DownUpMeanRatio5d',
    'DownUpSumRatio5d',
    'DownVolRatioDiff30',
    'Downward_volatility_20days',
    'DuoKongMix',
    'DuoKongPV',
    'EBITDev',
    'EMVA',
    'EP_Hist2_120D',
    'EarningRevision90d_nis',
    'ExceedSwingCorAmt',
    'ExtremeTurnStd',
    'FM10_GMTTM',
    'FM10_GTGTTM',
    'FM10_PROTTM',
    'FM11_GPM',
    'FM11_PTGTTM',
    'FM11_QGM',
    'FM11_QOP',
    'FM11_QOPYOY',
    'FM11_QROE',
    'FM11_YOYOP',
    'FM11_YOYTR',
    'FM13_PTG',
    'FM15_EPS',
    'FM18_PTG',
    'FM20_PTG',
    'FM2_GMA',
    'FM2_GPM',
    'FM2_OTGR',
    'FM2_PTG',
    'FM2_YOYE',
    'FM2_YOYTR',
    'FM3_YOYOP',
    'FM5_OTE',
    'FM5_OTG',
    'FM5_PTG',
    'FM5_QG',
    'FM5_ROETTM',
    'FM5_YOYNP',
    'FM8_GPM',
    'FM8_OPYOY',
    'FM8_PTGTTM',
    'FM8_QOP',
    'FM9_GPM',
    'FM9_ROATTM',
    'FM9_YOYPRO',
    'FR10d_1001',
    'FR20d_1001',
    'FR20d_1130',
    'FR40d',
    'FR40d_1001',
    'FallTurnover',
    'ForecastBPPercent120d',
    'ForecastEPChange60d',
    'ForecastEPDelta20d',
    'ForecastEPGChange60d',
    'ForecastEPPercent120d',
    'ForecastPE',
    'ForecastPEGDelta20d',
    'ForecastPEGDelta5d',
    'ForecastPEGPercent120d',
    'ForecastPEGRoll',
    'ForecastPEGRollChange40d',
    'ForecastPERoll',
    'FreeturnRankUpDownRatio_CS30',
    'GPMarTTMStandardGrowth',
    'GTJA176',
    'GTJA179',
    'GTJA2TransRolling20',
    'GTJA2TransRolling5',
    'GTJA36',
    'GTJA54',
    'GTJA64',
    'GTJA74',
    'GTJA_007',
    'GTJA_026',
    'GTJA_032',
    'GTJA_042',
    'GTJA_062',
    'GTJA_064',
    'GTJA_083',
    'GrahamValue',
    'GrowthRefined',
    'HighCandleBottom',
    'HighCloseTurnSharpe',
    'HighCloseTurnSharpe20',
    'HighCloseTurnSharpe80',
    'HighCloseTurnSigma',
    'HighLowStdRatio_mean20d',
    'HighVolCorrMax',
    'HighVolCorrStd',
    'HighVolumeCorr10d',
    'IVR_000300_20',
    'IdeaReverser5d',
    'IlliqNeg60d',
    'IndRankinglistEffect',
    'IndustriesPBROE',
    'IndustryMidBeta',
    'IndustryNeutralizedTurnoverStd',
    'IndustryReverse',
    'IntradayAmountRatioDay',
    'InvSta',
    'KNN30',
    'LargeSmallVolumeVWAPRatio',
    'Last30MinsVwapCloseRatio5d',
    'LastTurn',
    'LiqCorr',
    'LiqRatioAS',
    'LiqRatioSA',
    'LiquidityPure20Part2',
    'LongVolGrowthSharpe60d',
    'LoserList_200',
    'LowCandleBottom',
    'LowRtnVolGrowthSharpe60d',
    'LowRtnVolSkew60d',
    'MarketHolder',
    'MarketHolderMu',
    'MarketHolderSigma',
    'MarketTaker',
    'MarketTakerMu',
    'MarketTakerSigma',
    'MeanTurn2RetDown5d',
    'MedianDownAmtRatio',
    'MedianDownVarRatio',
    'MildMoneyMaker',
    'Min10VolBurst5Wegihted5d',
    'Min10mRetUpVar',
    'Min30CEMVbias',
    'Min30HW',
    'Min30TDis',
    'Min5LastHourMFI5d',
    'Min5VwapToClose20d',
    'Min60_RVstd',
    'MinARC2VRCExcessSharpe5d',
    'MinAbnCorr',
    'MinAmtKurt20d',
    'MinAmtMidChg',
    'MinAmtMidSkew',
    'MinAmtMidStd',
    'MinAmtSkew10d',
    'MinBWS',
    'MinBWskew',
    'MinBWstd',
    'MinCloseCallAmt5maCorrSharpe',
    'MinCloseReSkew5d',
    'MinCorHighVolumeMax10d',
    'MinCorW',
    'MinCorrRank',
    'MinCorrRankMean',
    'MinCorrVolumeRetUp5d',
    'MinEMVA',
    'MinEMVANorm',
    'MinERRC',
    'MinFW',
    'MinHLS',
    'MinHVSDis',
    'MinHVSmin',
    'MinHVV',
    'MinIdx500Corr',
    'MinIndexCorr',
    'MinLSV',
    'MinMACDNumDiffMean_1_1',
    'MinMACDNumDiffRank_5_5',
    'MinPMAmpVolume5d',
    'MinPRRC',
    'MinPVCS',
    'MinPmR',
    'MinRRCDis',
    'MinRRCs',
    'MinRSTstd',
    'MinRVM',
    'MinRVS',
    'MinReSkewLast120_10d',
    'MinReSkewLast120_20d',
    'MinReSkewLast120_5d',
    'MinRetVolKurtRank_5_1',
    'MinRetVolKurtRaw_5_5',
    'MinRetVolMaxSr_1_1',
    'MinRetVolMaxSr_1_5',
    'MinRetVolMaxStd_1_1',
    'MinRetVolSkewMean_5_5',
    'MinRetVolSkewRank_5_1',
    'MinRetVolSkewRank_5_5',
    'MinRetVolStdSr_1_1',
    'MinReturnVolUp2Down5d',
    'MinSkW',
    'MinSkew40d',
    'MinSmartFoolRatioMean',
    'MinStdW',
    'MinTAW',
    'MinTTD',
    'MinTTM',
    'MinTimeHighLow_20',
    'MinTopTailCost',
    'MinTopV',
    'MinTopVolRate',
    'MinUBK',
    'MinUBM',
    'MinUBS',
    'MinUBSR',
    'MinVB10',
    'MinVBR',
    'MinVRCExcess5d',
    'MinVVCorrRank',
    'MinVVCorrRankStd',
    'MinVVRankCorrStd',
    'MinVolRe',
    'MinVwapARC2VRCExcessSharpe20d',
    'MinVwapRV',
    'MinVwapRVskew',
    'MinWAC',
    'MinWR_20_80_5d',
    'MinWeightVolReRatio',
    'MinWeightVolReSkew',
    'MinWeightVolReSwing',
    'Min_ACD',
    'Min_PredictReturn2Volume',
    'Min_PredictReturnMean',
    'Min_RelativeDownReturn',
    'Min_UpRange',
    'Minute30CloseVolumeCorr',
    'Minute30m5dVolumeHHI',
    'MinuteALTKurt',
    'MinuteAmtCV3d',
    'MinuteAmtRetCor5d',
    'MinuteAmtStdSwing',
    'MinuteCloseCallAuctionTurnoverStdChange180d',
    'MinuteCloseDiff',
    'MinuteCloseMMT',
    'MinuteCloseMomentumSharpe',
    'MinuteCloseResist',
    'MinuteCloseSmartGame',
    'MinuteCloseTurn',
    'MinuteCloseTurnCorr',
    'MinuteCloseTurnEWMA',
    'MinuteCloseTurnPlus',
    'MinuteCloseTurnR',
    'MinuteCloseTurnREWMA',
    'MinuteCloseTurnRSharpe',
    'MinuteCloseTurnRSharpe10',
    'MinuteCloseTurnRev',
    'MinuteCloseTurnSharp',
    'MinuteCloseTurnoverStd',
    'MinuteCloseUpVar',
    'MinuteCloseWREWMA',
    'MinuteCloseWRVolume',
    'MinuteCorrRank',
    'MinuteDCDTA5d',
    'MinuteDownVolatilityRatio20d',
    'MinuteEODRetDrawdownRatioSharpe',
    'MinuteEODSkewness120Min',
    'MinuteEODSortinoRatioSharpe',
    'MinuteEODVolWeightedLongShortPowerSharpe',
    'MinuteEODVolumeWeightedReturnSharpe',
    'MinuteGroupReBias5d',
    'MinuteHighLowRtnVolDiff',
    'MinuteIdioSkew5d',
    'MinuteIlliqVwapClose5d',
    'MinuteLast30mPriceVolRefineMean10d',
    'MinuteLastHourMDDMCLIMBstd20d',
    'MinuteLastHourMaxClimb20dSR',
    'MinuteLastHourSkewness40d',
    'MinuteLastTurn20std',
    'MinuteLastVolumeRank5std',
    'MinuteMADistanceMA',
    'MinutePVCorrMin',
    'MinuteRelativeUpVar',
    'MinuteRetLastHrSkew',
    'MinuteRetSkewnessSharpe',
    'MinuteRetTurnRho',
    'MinuteRetVolMultSkew',
    'MinuteRetVolMultSkewSharpe',
    'MinuteReturnAutocorr5d',
    'MinuteReturnDiffStdSharpe',
    'MinuteReturnSkew',
    'MinuteSwing',
    'MinuteTERtnVRatio',
    'MinuteTLSTRvs',
    'MinuteTLSVRatio',
    'MinuteTPVDeltaCorr',
    'MinuteTRtnVGRank',
    'MinuteTRtnVGStdRank',
    'MinuteTRtnVRatioRank',
    'MinuteTSD',
    'MinuteTTLSStdRank',
    'MinuteTWRSharpe20',
    'MinuteTWRSkew20',
    'MinuteTurnoverStdSharpe',
    'MinuteTurnoverVolSharpe',
    'MinuteUpVar',
    'MinuteVMASkew',
    'MinuteValidRet',
    'MinuteVolCVSkew10d',
    'MinuteVolVwapCorrCloseChg',
    'MinuteVolofVolumeHHI',
    'MinuteVolumeHHISharpe',
    'MinuteVolumeKurt',
    'MinuteVolumeStabilitySharpe',
    'MinuteVolumeStdSharpe',
    'MinuteWRMean',
    'MinuteliqAmtRatioSharpe20d',
    'MinuteliqSwingSharpe5d',
    'MinuteliqSwingStd5',
    'MomBigOrder3Day',
    'MomHigh2Low10d',
    'MomHighExclMorn20d',
    'MomW',
    'MoneyMaker',
    'NIGrowthZscore1y',
    'NI_SQ_IndustryRank',
    'NetProfitSurprise',
    'NetProfit_sq_TSRank8',
    'Netprofitmargin_q',
    'NetworkDegree',
    'NonstationaryPV',
    'NonstationaryPVSharp',
    'OBCVPema_10',
    'OCVPema_20',
    'ODPB_DIFF120',
    'ODPB_DIFF20',
    'ODPEG_DIFF120',
    'ODPEG_DIFF20',
    'OTC5std',
    'OpenAmt',
    'OpenPositionInHighLowWeightedByVol_Mean_5',
    'OperProfitTTMStandardGrowth',
    'OperRevTTMStandardGrowth',
    'OverBuySell_Mean_5',
    'PDPS_Hist2_120D',
    'PEAdj',
    'PROFIT_PER20',
    'PROFIT_PER60',
    'PROFIT_SUM20',
    'PROFIT_UP60',
    'PVMax',
    'PVTTurn180d',
    'PVTTurn5d',
    'PVTTurn60d',
    'PePercent240d',
    'PriceDiff',
    'ProfitNoticeIndRank',
    'Profitability_IndZscore',
    'QfaROE',
    'QfaYoyeps',
    'ROEStandardGrowth',
    'ROEWin',
    'RSI',
    'RTC',
    'RTurnGainMin',
    'RTurnGainStd',
    'RangeRetCorr20',
    'RankEBIT2TRIndustrialStability',
    'RankEBITPSChg',
    'RankP2UndistributedEPS',
    'RankPBDev',
    'RankPEChange',
    'RankRetEPSIndustrialStability',
    'RankRoAIndustrialStability',
    'RankinglistEffect',
    'Re300ReturnScore5D',
    'ReCorr20',
    'ReCorrMean5dRank',
    'ReStdUp2Down5d',
    'RelativeIndPEAS',
    'RelativeIndPEGAvg',
    'ReportScoreGrowth',
    'Ret10Max_CS60_Mean2Std10',
    'Ret2Drawdown_CS60_Mean2Std10',
    'Ret2RetLength_CS15_Bias10',
    'Ret2RetLength_CS15_Mean2Std10',
    'RetCorrTurnDelayPure',
    'RetCutCorrTurnDelay',
    'RetDiffStd_Mean2Std10',
    'RetMaxMinSum_Mean10',
    'RetMaxMinSum_SR5',
    'RetMktDevCorr',
    'RetRankStd10d',
    'RetSkewSharp',
    'RetSkew_CS120_Mean2Std10',
    'RetSkew_CS180_Mean2Std30',
    'RetSkew_CS60_Mean2Std10',
    'RetSkew_Mean2Std10',
    'RetSkew_Mean_5',
    'RetStdTurnCorr',
    'RetUpDownRatio_CS20_Mean5',
    'RetVolMultSharp_30',
    'RetVolProdSkewSharp_20',
    'RevSplit',
    'ReverseDistance',
    'ReverseMomentumDouble',
    'ReverseMomentumTriple',
    'RoeTTM_IndRank',
    'RtnVolGrowthRankDiff',
    'SPPI',
    'SectorIlliquidity',
    'SectorNotionalSharpe',
    'SectorPESharpe',
    'SellRtnSellMoneyDiffCorr',
    'SeperateBeforehandRet_30',
    'SeperateBeforehandRet_Normolized20',
    'ShoutCutILLIQ_10',
    'SimpleVolume',
    'SmallPlayersTurnover',
    'SmallPlayersTurnoverSharpe20d',
    'SmallPlayersVwap',
    'Smartmoney_amt_skew01505_rolling1_daily',
    'Smartmoney_close_trb0505_rolling3_daily',
    'Smartmoney_hlratio_ms0505_rolling1_daily',
    'Smartmoney_hlratio_rdm01505_rolling3_daily',
    'Smartmoney_hlratio_rdm0505_rolling3_daily',
    'StaVolDivRetUpdown',
    'StableRet',
    'StableVol',
    'SwingHighLowPriceCorr',
    'SwingToTurn',
    'SwingW',
    'TPVDeltaCorr',
    'TargetReturnDelta5d',
    'TickFactor_AccBuyKurt',
    'TickFactor_AccBuyStd',
    'TickFactor_ActBuyKurt',
    'TickFactor_ActBuyOrderStdRatio',
    'TickFactor_BuyOrderStd',
    'TickFactor_BuyOrderStdRatio',
    'TickFactor_MaxAccBuyStdRatio',
    'TickFactor_MaxActBuyOrderStdRatio',
    'TickFactor_MaxBuyOrderStdRatio',
    'TickFactor_MinAccBuyStdRatio',
    'TickFactor_MinActBuyOrderStdRatio',
    'TickFactor_MinBuyOrderStdRatio',
    'TickFactor_PassBuyOrderStdRatio',
    'TickFactor_RawAccBuyKurt',
    'TickFactor_RawAccBuyStdRatio',
    'TickFactor_RawActBuyOrderStdRatio',
    'TickFactor_RegActBuyOrderStdRatio',
    'TickFactor_RegBuyOrderStdRatio',
    'Tick_NewBuyOrderAmt',
    'Tick_NewBuyOrderAmt_std',
    'Tick_NewSellOrderAmt',
    'Tick_NewSellOrderAmt_std',
    'Tick_bsdiff_amt_std_top_ordercanceledvol_skew3_daily',
    'Tick_bsdiff_hl_tail_active_orderamt_cov3_daily',
    'Tick_bsdiff_hl_tail_passive_orderamt_corr3_daily',
    'Tick_bsdiff_hl_top_active_ordervol_cov1_daily',
    'Tick_bsdiff_hl_top_active_ordervol_cov3_daily',
    'Tick_bsdiff_illq_tail_active_orderamt_avg3_daily',
    'Tick_bsdiff_illq_tail_passive_orderamt_corr3_daily',
    'Tick_bsdiff_illq_tail_tradevol_corr3_daily',
    'Tick_bsdiff_illq_top_active_orderamt_cov3_daily',
    'Tick_bsdiff_illq_top_ordervol_cov3_daily',
    'Tick_bsdiff_illq_top_tradeamt_avg1_daily',
    'Tick_bsdiff_illq_top_tradevol_corr1_daily',
    'Tick_bsdiff_raw_active_ordervol_corr3_daily',
    'Tick_bsdiff_ret_skew_tail_active_orderamt_cov3_daily',
    'Tick_bsdiff_ret_skew_tail_ordercanceledamt_avg3_daily',
    'Tick_bsdiff_ret_skew_tail_ordervol_avg3_daily',
    'Tick_bsdiff_ret_skew_top_active_orderamt_skew3_daily',
    'Tick_bsdiff_ret_skew_top_passive_orderamt_corr3_daily',
    'Tick_bsdiff_ret_skew_top_tradenum_corr3_daily',
    'Tick_bsdiff_ret_std_tail_active_orderamt_corr3_daily',
    'Tick_bsdiff_ret_std_tail_passive_orderamt_corr3_daily',
    'Tick_bsdiff_ret_std_top_active_ordervol_corr3_daily',
    'Tick_bsdiff_ret_std_top_orderamt_avg3_daily',
    'Tick_bsdiff_ret_std_top_ordervol_corr3_daily',
    'Tick_bsdiff_ret_tail_orderamt_corr3_daily',
    'Tick_bsdiff_ret_tail_ordercanceledamt_cov3_daily',
    'Tick_bsdiff_ret_tail_passive_orderamt_cov3_daily',
    'Tick_bsdiff_ret_tail_passive_ordervol_corr1_daily',
    'Tick_bsdiff_ret_top_ordercanceledvol_cov1_daily',
    'Tick_bsdiff_ret_top_ordercanceledvol_cov3_daily',
    'Tick_bsdiff_ret_top_passive_orderamt_cov3_daily',
    'Tick_bsdiff_ret_top_tradenum_cov1_daily',
    'Tick_bsdiff_self_tail_active_orderamt_cov3_daily',
    'Tick_bsdiff_self_tail_ordercanceledvol_skew1_daily',
    'Tick_bsdiff_self_tail_tradeamt_std3_daily',
    'Tick_bsdiff_self_top_active_orderamt_cov3_daily',
    'Tick_bsdiff_self_top_ordercanceledamt_std3_daily',
    'TradeNumSkewDay',
    'TurnCV_10',
    'TurnCloseLowSharpe',
    'TurnCorrSharp',
    'TurnGain',
    'TurnHighClose',
    'TurnHighCloseSharpe',
    'TurnHighCloseSigma',
    'TurnNeuRetCorrSharp',
    'TurnPEAS',
    'TurnPEStd',
    'TurnRankPercent_1d_240d',
    'TurnoverSharpe',
    'TurnoverSharpe100d',
    'TwapVwapRet',
    'UpAmtKurt_Mean5',
    'UpDownVolatility',
    'UpHigh2VwapWeightedByVolume_SR20',
    'UpSpeed',
    'UpVolatilityRatio_20',
    'UpVwap2LowWeightedByVolume_SR20',
    'ValueDelay',
    'ValueGrowthChange60d',
    'ValueRefined',
    'Vol30HHI_Mean2Std10',
    'VolPctMeanRankDiffInExtremeUpDownRet_Mean5',
    'VolPriceCorr',
    'VolPriceFlyer',
    'VolPriceFlyerPlus',
    'VolPriceRunner',
    'VolRPriceRCorr20d',
    'VolRaiseMom5d',
    'VolRegIndexRsquare_20',
    'VolSurgeSharpe',
    'VolSwingRankCorr',
    'VolUpDownStdRatio_Mean_5',
    'VolaRatioOnBSlog3Day',
    'VolitilityMax',
    'VolitilityRelative',
    'VolumeRatioDown20d',
    'VolumeShortLongStdRatio',
    'VolumeStdBias',
    'VolumeStdHigh2Low20d',
    'VolumeStdHigh2Low5d',
    'VwapCloseAdj20d',
    'VwapRatio',
    'VwapRatioOnAmtPerTradeDay',
    'VwapReCorrMean10dRank',
    'VwapTurnStdRatio',
    'WQ016',
    'WQ_027',
    'WeightedDownUpSumRatio5d',
    'WinnerList_225',
    'ZaoYinTrader',
    'abnormal_coverage_nis',
    'alp10_alpuniv',
    'alp12_alpuniv',
    'alp22_alpuniv',
    'alp29_alpuniv',
    'alp3_alpuniv',
    'alphas_dongj_pct_chg_swing_combine',
    'amt_3d_120d_ratio_nis',
    'amt_size_corr_turn_nis',
    'asset_turnover_lvl_chg_nis',
    'buy_volume_exlarge_order_act_5d_inv_nis',
    'cashflow_multiple_lvl_chg_nis',
    'chgw_alpuniv',
    'chwg4',
    'chwg5',
    'close_vol_pct_prod_r20_nis',
    'core_alpuniv',
    'cs_resid_amt_std_15_nis',
    'cs_resid_turn_std_20_nis',
    'csad1',
    'csad_ftest',
    'dep_pure_nis',
    'dpEPS_F1YF2Y_lvl_chg60_nis',
    'dretvolnew_kurtmean_20_10_daily',
    'dretvolnew_skewmean_60_3_daily',
    'dretvvolnew_msmean_20_10_daily',
    'dretvvolnew_msmean_60_10_daily',
    'dretvvolnew_msmean_60_3_daily',
    'dretvvolnew_scmmean_20_10_daily',
    'dretvvolnew_scmmean_60_10_daily',
    'dretvvolnew_skewmean_20_10_daily',
    'dretvvolnew_skewmean_20_3_daily',
    'dretvvolnew_skewmean_60_10_daily',
    'duvol_derived_nis',
    'dwf_alpuniv',
    'egr_nis',
    'ep_per_nis',
    'eps_c2_lvl_chg_nis',
    'fddcom_alpuniv',
    'front_run_comb_nis',
    'gross_margin_lvl_chg_nis',
    'gross_profit_margin_lvl_chg_nis',
    'growth_alpuniv',
    'growth_by_def_nis',
    'growth_comb_nis',
    'gtja_pv105_nis',
    'gtja_pv110_nis',
    'gtja_pv130_nis',
    'gtja_pv140_nis',
    'gtja_pv16_nis',
    'gtja_pv179_nis',
    'gtja_pv1_nis',
    'gtja_pv32_nis',
    'gtja_pv62_nis',
    'gtja_pv64_nis',
    'gtja_pv83_nis',
    'ls_strength_nis',
    'mid_price_w_amt_r40_nis',
    'net_profit_c2_lvl_chg_nis',
    'net_profit_margin_lvl_chg_nis',
    'npm_qfa_lvl_chg_nis',
    'open2close_turn_ls_nis',
    'open_moneyflow_pct_volume_20d_nis',
    'optogr_qfa_nis',
    'org_num_75d_nis',
    'pe_F2YF1Y_inv_lvl_chg60_nis',
    'pe_ttm_nis',
    'pechgnew_alpuniv',
    'peg_F2YF1Y_inv_lvl_chg60_nis',
    'pegfy1chg_alpuniv',
    'price_bias_comb_nis',
    'profitchg_alpuniv',
    'pt_r2_20_r20_nis',
    'qfa_roe_alpuniv',
    'qfa_roe_lvl_chg_nis',
    'qfa_yoyop_nis',
    'qfa_yoyprofit_alpuniv',
    'qfa_yoysales_alpunivchg',
    'r2_current_20d_diff_nis',
    'rev_cvturn_max_nis',
    'rev_turn_liq_nis',
    'reversal_trade_count_20d_nis',
    'rnoa_nis',
    'roe_basic_alpunivchg',
    'roe_fa_avg_lvl_chg_nis',
    'roema_alpuniv',
    's_fa_netprofittoor_ttm_growth_nis',
    's_fa_roe_ttm_growth_nis',
    's_qfa_roe_growth_nis',
    'sdrkurt_nis',
    'sdvhhi_norm_nis',
    'sell_volume_small_order_act_1d_inv_nis',
    'sp_lvl_chg_nis',
    'su_tot_assets_1_12_nis',
    'tper_nis',
    'tptpchg_alpuniv',
    'trade_strength_last15_r20_nis',
    'turn_mvc_nis',
    'up_vol_ratio_40d_nis',
    'uretvolnew_stdstd_20_3_daily',
    'uretvvolnew_kurtmean_20_3_daily',
    'uretvvolnew_kurtskew_20_10_daily',
    'uretvvolnew_meanskew_60_10_daily',
    'uretvvolnew_msmean_20_10_daily',
    'uretvvolnew_msstd_60_10_daily',
    'uretvvolnew_msstd_60_3_daily',
    'uretvvolnew_mstb_60_10_daily',
    'uretvvolnew_skewmean_20_10_daily',
    'uretvvolnew_skewmean_20_3_daily',
    'uretvvolnew_skewmean_60_10_daily',
    'uretvvolnew_stdskew_60_10_daily',
    'valuecom_alpuniv',
    'vol_up_nis',
    'volume_hhi_nis',
    'volume_skew_nis',
    'yoynetprofit_alpunivchg',
    'zhy_factor_24',
    'zhy_factor_56',
    'zhy_factor_61',
    'zhy_factor_63',
    'zhy_factor_64',
    'zhy_factor_65',
    'zhy_factor_72',
    'zhy_factor_73',
]

price_type = 'twap'
future_days = 5

groups = 10

fee = 0.002

select_days = 120
model_days = 60

tolerate = 0.2
corr_limit = 0.7

metrics = ['active_mean_net', 'active_sp_net']
metrics_weight = [1, 1]
multi_period_weight = [0, 0, 0, 0, 1]

factor_num_limit = np.inf
factor_proportion_limit = 1.

compound_name = 'compound74'

future_days_max = 5

stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True, least_recover_days=1,
                              no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False, no_limit_down=False,
                              other_limit={'mkt_cap_ard': 0.05}, start_date=start_date, end_date=end_date)

date_list = stock_pool.index.to_list()
code_list = stock_pool.columns.to_list()
stock_pool = stock_pool.values

future = load_future(stock_pool, future_days, start_date, end_date, code_list, price_type)
future = future.transpose(1, 2, 0).dot(multi_period_weight)
future_mv = standardize(future)
future_mad = standardize(future, method='mad')
future_uniform = standardize(future, method='uniform')
future_normal = standardize(future, method='normal')

factor_pool, factor_multi_period_weight, select_rank = factor_select(
    start_date, end_date, select_days, model_days, future_days, groups, metrics, metrics_weight,
    multi_period_weight, corr_limit, factor_num_limit, factor_proportion_limit, fee, tolerate,
    middle_address, factor_list, compound_name, compound_address)

model_date_list = date_list[select_days - 1: - future_days_max - 1]


# linear model ols
def linear_ols(sub_list, model_date_list, model_days, factor_list, code_list, factor_pool, date_list, middle_address,
               select_rank, future, stock_pool, future_days_max, temp_address, line):
    for date in tqdm(sub_list, desc=str(line)):

        factor = np.full((model_days, len(factor_list), len(code_list)), fill_value=np.nan)
        for x in range(model_days):
            factor[x, factor_pool[date_list.index(date) - model_days + x + 1]] = np.load('%s%s %s.npy' % (
                middle_address, 'factor_standardize', get_pre_trade_date(date, model_days - x - 1)))
        select = select_rank[model_date_list.index(date)]
        select = select.argsort()[:len(select[np.isfinite(select)])]
        factor = factor[:, select]

        ret = future[date_list.index(date) - model_days + 1: date_list.index(date) + 1]

        pool = stock_pool[date_list.index(date) - model_days + 1: date_list.index(date) + 1]
        pool &= np.isfinite(ret) & np.all(np.isfinite(factor), axis=1)

        feature = factor.transpose(1, 0, 2).reshape(factor.shape[1], factor.shape[0] * factor.shape[2])[:,
                  pool.flatten()].T
        label = ret.flatten()[pool.flatten()]

        predict = np.full((len(factor_list), len(code_list)), fill_value=np.nan)
        predict[factor_pool[date_list.index(date) + future_days_max + 1]] = np.load('%s%s %s.npy' % (
            middle_address, 'factor_standardize', get_pre_trade_date(date, - future_days_max - 1)))
        predict = predict[select]
        predict[~np.isfinite(predict)] = 0.
        predict = predict.T

        real = future[date_list.index(date) + model_days + 1]

        reg = LinearRegression(copy_X=False)
        reg.fit(feature, label)

        model = np.full(len(factor_list), np.nan)
        model[select] = reg.coef_

        predict = reg.predict(predict)
        predict[~stock_pool[date_list.index(date) + future_days_max + 1]] = np.nan

        np.save(temp_address + 'model ' + str(get_pre_trade_date(date, - future_days_max - 1)), model)
        np.save(temp_address + 'predict ' + str(get_pre_trade_date(date, - future_days_max - 1)), predict)


temp_address = '/data/user/015836/model/ols/'
multiprocess(10, linear_ols, model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
             date_list, middle_address, select_rank, future_uniform, stock_pool, future_days_max, temp_address)

compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                              date_list[select_days + future_days_max:])]
compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
compound.to_hdf('%s%s' % (compound_address, 'compound106'), 'compound106', format='t')

model = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'model', x)) for x in
                           date_list[select_days + future_days_max:])]
model = pd.DataFrame(model, index=date_list[select_days + future_days_max:], columns=factor_list)
model.to_hdf('%s%s' % (compound_address, 'model106'), 'model106', format='t')

def tree_xgb(sub_list, model_date_list, model_days, factor_list, code_list, factor_pool, date_list, middle_address,
             select_rank, future, stock_pool, future_days_max, temp_address, line):

    for date in tqdm(sub_list, desc=str(line)):

        factor = np.full((model_days, len(factor_list), len(code_list)), fill_value=np.nan)
        for x in range(model_days):
            factor[x, factor_pool[date_list.index(date) - model_days + x + 1]] = np.load('%s%s %s.npy' % (
                middle_address, 'factor_standardize', get_pre_trade_date(date, model_days - x - 1)))
        select = select_rank[model_date_list.index(date)]
        select = select.argsort()[:len(select[np.isfinite(select)])]
        factor = factor[:, select]

        ret = future[date_list.index(date) - model_days + 1: date_list.index(date) + 1]

        pool = stock_pool[date_list.index(date) - model_days + 1: date_list.index(date) + 1]
        pool &= np.isfinite(ret) & np.all(np.isfinite(factor), axis=1)

        feature = factor.transpose(1, 0, 2).reshape(factor.shape[1], factor.shape[0] * factor.shape[2])[:,
                  pool.flatten()].T
        label = ret.flatten()[pool.flatten()]

        predict = np.full((len(factor_list), len(code_list)), fill_value=np.nan)
        predict[factor_pool[date_list.index(date) + future_days_max + 1]] = np.load('%s%s %s.npy' % (
            middle_address, 'factor_standardize', get_pre_trade_date(date, - future_days_max - 1)))
        predict = predict[select]
        predict[~np.isfinite(predict)] = 0.
        predict = predict.T

        bst = xgb.XGBRegressor(learning_rate=0.01,
                               n_estimators=450,
                               max_depth=1,
                               min_child_weight=10,
                               objective='reg:linear',
                               nthread=24,
                               scale_pos_weight=1,
                               subsample=0.7,
                               colsample_bytree=0.5,
                               gamma=2,
                               reg_lambda=0.5,
                               slice=True)

        bst.fit(feature, label, eval_metric=['rmse'])
        predict = bst.predict(predict)

        predict[~stock_pool[date_list.index(date) + future_days_max + 1]] = np.nan

        np.save(temp_address + 'predict ' + str(get_pre_trade_date(date, - future_days_max - 1)), predict)

temp_address = '/data/user/015836/model/tree/'
tree_xgb(model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
         date_list, middle_address, select_rank, future_uniform, stock_pool, future_days_max, temp_address, 0)


compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                              date_list[select_days + future_days_max:])]
compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
compound.to_hdf('%s%s' % (compound_address, 'compound114'), 'compound114', format='t')


# linear model ols
def linear_olsL2(sub_list, model_date_list, model_days, factor_list, code_list, factor_pool, date_list, middle_address,
                 select_rank, future, stock_pool, future_days_max, temp_address, line):
    for date in tqdm(sub_list, desc=str(line)):

        factor = np.full((model_days, len(factor_list), len(code_list)), fill_value=np.nan)
        for x in range(model_days):
            factor[x, factor_pool[date_list.index(date) - model_days + x + 1]] = np.load('%s%s %s.npy' % (
                middle_address, 'factor_standardize', get_pre_trade_date(date, model_days - x - 1)))
        select = select_rank[model_date_list.index(date)]
        select = select.argsort()[:len(select[np.isfinite(select)])]
        factor = factor[:, select]

        ret = future[date_list.index(date) - model_days + 1: date_list.index(date) + 1]

        pool = stock_pool[date_list.index(date) - model_days + 1: date_list.index(date) + 1]
        pool &= np.isfinite(ret) & np.all(np.isfinite(factor), axis=1)

        feature = factor.transpose(1, 0, 2).reshape(factor.shape[1], factor.shape[0] * factor.shape[2])[:,
                  pool.flatten()].T
        label = ret.flatten()[pool.flatten()]

        # code_num = len(code_list)
        # init = [1, 10, 100, 1000, 10000, 100000]
        #
        # alpha = interpolation_search(feature, label, model_days, code_num, pool, ret, init,
        #                             point=5, tol=1e-6, max_iter=20)
        # reg = Ridge(alpha=alpha).fit(feature, label)
        reg = RidgeCV((0.1, 1, 10, 100, 1000, 10000), cv=5).fit(feature, label)
        predict = np.full((len(factor_list), len(code_list)), fill_value=np.nan)
        predict[factor_pool[date_list.index(date) + future_days_max + 1]] = np.load('%s%s %s.npy' % (
            middle_address, 'factor_standardize', get_pre_trade_date(date, - future_days_max - 1)))
        predict = predict[select]
        predict[~np.isfinite(predict)] = 0.
        predict = predict.T

        model = np.full(len(factor_list), np.nan)
        model[select] = reg.coef_

        predict = reg.predict(predict)
        predict[~stock_pool[date_list.index(date) + future_days_max + 1]] = np.nan

        np.save(temp_address + 'model ' + str(get_pre_trade_date(date, - future_days_max - 1)), model)
        np.save(temp_address + 'predict ' + str(get_pre_trade_date(date, - future_days_max - 1)), predict)


temp_address = '/data/user/015836/model/ols/'
multiprocess(30, linear_olsL2, model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
             date_list, middle_address, select_rank, future, stock_pool, future_days_max, temp_address)

compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                              date_list[select_days + future_days_max:])]
compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
compound.to_hdf('%s%s' % (compound_address, 'compound103'), 'compound103', format='t')

model = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'model', x)) for x in
                           date_list[select_days + future_days_max:])]
model = pd.DataFrame(model, index=date_list[select_days + future_days_max:], columns=factor_list)
model.to_hdf('%s%s' % (compound_address, 'model103'), 'model103', format='t')

for x1 in range(400, 510, 10):
    bst = xgb.XGBRegressor(learning_rate=0.01,
                           n_estimators=450,
                           max_depth=1,
                           min_child_weight=10,
                           objective='reg:linear',
                           nthread=24,
                           scale_pos_weight=1,
                           subsample=0.7,
                           colsample_bytree=0.5,
                           gamma=2,
                           reg_lambda=0.5,
                           slice=True)

    bst.fit(feature, label, eval_metric=['rmse'])
    y_hat = bst.predict(predict)
    y = np.sqrt(np.nanmean((y_hat - real) ** 2))
    print(x1, y)

    xgb.callback.record_evaluation()

xgb.train()

def xgb_cv(bst, feature, label, fold=10, early_stop_round=30):

    params = bst.get_xgb_params()
    train = xgb.DMatrix(feature, label)
    cv_result = xgb.cv(params, train, num_boost_round=params['n_estimators'],
                       nfold=fold, metrics=['rmse'], early_stopping_rounds=early_stop_round,
                       callbacks=[xgb.callback.print_evaluation(period=1, show_stdv=True)])
    return cv_result


def xgb_fit(bst, train, test, features, cv_result):

    bst.set_params(n_estimators=cv_result.shape[0])
    bst.fit(train[features], train['label'], eval_metric=['auc'])
    train_predict_prob = bst.predict_proba(train[features])[:, 1]
    train_auc = metrics.roc_auc_score(train['label'], train_predict_prob)
    test['prob'] = bst.predict_proba(test[features])[:, 1]
    test_auc = metrics.roc_auc_score(test['label'], test['prob'])


features = [x for x in train.columns if x not in [label, IDcol]]

model1 = xgb.XGBClassifier(
    learning_rate=0.1,
    n_estimators=500,
    max_depth=4,
    min_child_weight=1,
    objective='binary:logistic',
    subsample=0.8,
    colsample_bytree=0.8,
    nthread=8,
    scale_pos_weight=1,
    seed=10)

cv_result = xgb_cv(model1, train, features)
xgb_fit(model1, train, test, features, cv_result)

param = {'max_depth': [1, 2, 3, 4, 5, 6, 7],
          'min_child_weight': [1, 2, 3, 4, 5]}



grid_search1 = GridSearchCV(estimator=bst,
                            param_grid=param,
                            scoring='neg_mean_squared_error',
                            n_jobs=1,
                            cv=10,
                            verbose=2)

grid_search1.fit(feature, label)


def tree():


if __name__ == '__main__':
    # test
    compound = pd.read_hdf('%s%s' % (compound_address, 'compound114'), 'compound114')
    stock_pool_df = pd.DataFrame(stock_pool, index=date_list, columns=code_list)
    nft = NonFactorTest(start_date=20160104, end_date=compound.index[-1],
                        stock_pool=stock_pool_df, future_days=future_days, pre_neutralize=False)
    nft.load_factor(compound, False)
    result = pd.concat([nft.calc_ic(), nft.calc_group_ret(), nft.calc_strategy_ret(buy_fee=0.000, sell_fee=0.002)],
                       axis=1)
    # print((factor_multi_period_weight != 0).sum(axis=1).mean())
    result[['IC', 'IC_IR', 'ic_group', 'top_excess_ret', 'excess_ret', 'turn', 'mdd', 'IR']].stack()

    model101 = pd.read_hdf('%s%s' % (compound_address, 'model101'), 'model101')
    model102 = pd.read_hdf('%s%s' % (compound_address, 'model102'), 'model102')
    model101.stack().dropna().corr(model102.stack().dropna())
    aaa = np.load(middle_address + 'factor_standardize 20180705.npy')

    ###
    multi_period_weight = [0, 0, 1, 0, 0]
    future = load_future(stock_pool, future_days, start_date, end_date, code_list, price_type)
    future = future.transpose(1, 2, 0).dot(multi_period_weight)
    future_mv = standardize(future)
    future_mad = standardize(future, method='mad')
    future_uniform = standardize(future, method='uniform')
    future_normal = standardize(future, method='normal')

    multiprocess(10, linear_ols, model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
                 date_list, middle_address, select_rank, future, stock_pool, future_days_max, temp_address)

    compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                                  date_list[select_days + future_days_max:])]
    compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
    compound.to_hdf('%s%s' % (compound_address, 'compound111'), 'compound111', format='t')

    model = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'model', x)) for x in
                               date_list[select_days + future_days_max:])]
    model = pd.DataFrame(model, index=date_list[select_days + future_days_max:], columns=factor_list)
    model.to_hdf('%s%s' % (compound_address, 'model111'), 'model111', format='t')

    multiprocess(10, linear_ols, model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
                 date_list, middle_address, select_rank, future_uniform, stock_pool, future_days_max, temp_address)

    compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                                  date_list[select_days + future_days_max:])]
    compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
    compound.to_hdf('%s%s' % (compound_address, 'compound112'), 'compound112', format='t')

    model = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'model', x)) for x in
                               date_list[select_days + future_days_max:])]
    model = pd.DataFrame(model, index=date_list[select_days + future_days_max:], columns=factor_list)
    model.to_hdf('%s%s' % (compound_address, 'model112'), 'model112', format='t')

    multiprocess(10, linear_ols, model_date_list, model_date_list, model_days, factor_list, code_list, factor_pool,
                 date_list, middle_address, select_rank, future_mv, stock_pool, future_days_max, temp_address)

    compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'predict', x)) for x in
                                  date_list[select_days + future_days_max:])]
    compound = pd.DataFrame(compound, index=date_list[select_days + future_days_max:], columns=code_list)
    compound.to_hdf('%s%s' % (compound_address, 'compound113'), 'compound113', format='t')

    model = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (temp_address, 'model', x)) for x in
                               date_list[select_days + future_days_max:])]
    model = pd.DataFrame(model, index=date_list[select_days + future_days_max:], columns=factor_list)
    model.to_hdf('%s%s' % (compound_address, 'model113'), 'model113', format='t')
