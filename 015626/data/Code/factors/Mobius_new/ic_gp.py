import numpy as np
from future_factor import FutureFactor

class MinuteLocalHighLowReverse(FutureFactor):
    '''
    Description: 
    Class: Local_High_Low
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def getlocallows(self, price, threshold=0.01):
        prehigh = []
        posthigh = []
        locallow = []
        preh = 0 
        posth = 0
        ll = 0
        for i in range(len(price)):
            if price[ll] <= price[preh]/(1+threshold):
                if price[ll] <= price[posth]/(1+threshold):
                    prehigh.append(preh)
                    locallow.append(ll)
                    ll = i-1
                    preh = i-1
                    posth = i-1
                    if price[i] >= price[preh]:
                        preh = i
                        ll = i
                        posth = i
                    else:
                        ll = i
                        posth = i

                else:
                    if price[i] <= price[ll]:
                        ll = i
                        posth = i
                    else:
                        posth = i
            else:
                if price[i] >= price[preh]:
                    preh = i
                    ll = i
                    posth = i
                else:
                    ll = i
                    posth = i
        return locallow

    def getlocalhighs(self,  price, threshold=0.01):

        prelow = []
        postlow = []
        localhigh = []
        prel = 0 
        postl = 0
        lh = 0
        for i in range(len(price)):
            if price[lh] >= price[prel]*(1+threshold):
                if price[lh] >= price[postl]*(1+threshold):
                    prelow.append(prel)
                    localhigh.append(lh)
                    lh = i-1
                    prel = i-1
                    postl = i-1
                    if price[i] <= price[prel]:
                        prel = i
                        lh = i
                        postl = i
                    else:
                        lh = i
                        postl = i
                else:
                    if price[i] >= price[lh]:
                        lh = i
                        postl = i
                    else:
                        postl = i
            else:
                if price[i] <= price[prel]:
                    prel = i
                    lh = i
                    postl = i
                else:
                    lh = i
                    postl = i
        return localhigh
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        
        lows = self.getlocallows(index_close, threshold=0.005)
        highs = self.getlocalhighs(index_close, threshold=0.005)
        
        if len(lows) < 5 or len(highs) < 5:
            f = 0
        else:
            a = index_close[-1] / np.sum(index_close[highs[-5:]])
            b = index_close[-1] / np.sum(index_close[lows[-5:]])
            f = b - a
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteSpreadInterestCorr(FutureFactor):
    '''
    Description:
    Class: Liquidity
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['AskP0', 'BidP0', 'interest']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        bid_p_0 = data['BidP0_cont_IC'].values[-n:]
        ask_p_0 = data['AskP0_cont_IC'].values[-n:]
        interest = data['interest_cont_IC'].values[-n:]

        spread = (ask_p_0 - bid_p_0) / (ask_p_0 + bid_p_0)

        factor_value = -np.corrcoef(interest, spread)[0, 1]

        if np.isinf(factor_value) or np.isnan(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteICIFInterestDiff(FutureFactor):
    '''
    Description: mean(interest_IF, 60) - mean(interest_IC, 60)
    Class: Multi-Variety
    Author: lixr
    '''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Variety'] = {'IC':['interest'],'IF':['interest']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 60
        interest1 = data['interest_IC'].values[-n:]
        interest2 = data['interest_IF'].values[-n:]
        
        factor_value = np.nanmean(interest2) - np.nanmean(interest1) 
        
        return factor_value
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexReDivideSwing(FutureFactor):
    '''
    Description: pct_chg(index_close, 60) / ((max(index_high, 60) - min(index_low, 60)) / delay(index_close, 60))
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 20
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        index_high = data['high_000905.SH'].values
        index_low = data['low_000905.SH'].values
        
        N = 60
        index_close_past = index_close[:self.days_past*240]
        index_high_past = index_high[:self.days_past*240]
        index_low_past = index_low[:self.days_past*240]
        index_r_past = (index_close_past[N:] - index_close_past[:-N]) / index_close_past[:-N]
        index_swing_past = (bn.move_max(index_high_past, N) - bn.move_min(index_low_past, N))[N:] / index_close_past[:-N]
        f_past = index_r_past / index_swing_past
        f_past_mean = np.nanmean(f_past)
        f_past_std = np.nanstd(f_past)
        
        index_r = (index_close[-1] - index_close[-N-1]) / index_close[-N-1]
        index_swing = (np.max(index_high[-N:]) - np.min(index_low[-N:])) / index_close[-N-1]
        f_original = index_r / index_swing
        
        f = (f_original - f_past_mean) / f_past_std
        if f > 3:
            f = 3
        elif f < -3:
            f = -3
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteSpotFutureAutoBeta(FutureFactor):
    '''
    Description: cov(delay(pct_chg(close_000905.SH, 1), 1), pct_chg(close, 1), 30) / var(delay(pct_chg(close_000905.SH, 1), 1), 30)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close']}
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        index_close = data['close_000905.SH'].values
        index_close[index_close == 0] = np.nan
        close = data['close_cont_IC'].values
        close[close == 0] = np.nan
        
        
        rtn = close[-lb:] / close[-lb - 1: -1] - 1
        index_rtn = index_close[-lb:] / index_close[-lb - 1: -1] - 1
        cov = np.cov(index_rtn[:-1], rtn[1:])
        f = cov[0, 1] / cov[0, 0]
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskBidDepthRatioStd(FutureFactor):
    '''
    Description: -ts_mean(cs_std((AskP0 - AskP4) / (BidP0 - BidP4)), 15)
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidP0', 'BidP4', 'AskP0', 'AskP4']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        bid_0 = data['BidP0'].values[-15:]
        bid_0[bid_0 == 0] = np.nan
        bid_4 = data['BidP4'].values[-15:]
        bid_4[bid_4 == 0] = np.nan
        ask_0 = data['AskP0'].values[-15:]
        ask_0[ask_0 == 0] = np.nan
        ask_4 = data['AskP4'].values[-15:]
        ask_4[ask_4 == 0] = np.nan
        ratio = (ask_0 - ask_4) / (bid_0 - bid_4)
        ratio[np.isinf(ratio)] = np.nan
        f = -np.nanmean(np.nanstd(ratio, axis=1))
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteRe5Autocorr5_120Maxmin120(FutureFactor):
    '''
    Description: max(corr(pct_chg(close, 5), delay(pct_chg(close, 5), 5), 120), 120)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        r_5 = (close[5:] - close[:-5]) / close[:-5]
        r_5_autocorr_5 = self.rolling_corr(r_5[5:], r_5[:-5], 120)
        f = np.max(r_5_autocorr_5[-120:]) - np.min(r_5_autocorr_5[-120:])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteWilliamsR(FutureFactor):
    '''
    Description: -(TodayHigh - close) / (TodayHigh - TodayLow)
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close', 'TodayHigh', 'TodayLow']}
    normalize_size = 60 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        f = -(data['TodayHigh_cont_IC'].values[-1] - data['close_cont_IC'].values[-1]) / (data['TodayHigh_cont_IC'].values[-1] - data['TodayLow_cont_IC'].values[-1])
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute25OBV(FutureFactor):
    '''
    Description: sum(where(Index_ClosePx > delay(Index_ClosePx,1), Index_Volume, 0), 25) / sum(Index_Volume, 25)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close', 'volume']}
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 25
        index_close = data['close_000905.SH'].values[-(n + 1):]
        index_volume = data['volume_000905.SH'].values[-(n + 1):]

        rtn = index_close[1:] / index_close[:-1] - 1
        rtn = np.insert(rtn, 0, np.nan)

        up_vol_sum = np.nansum(index_volume[rtn > 0])
        up_vol_ratio = up_vol_sum / np.nansum(index_volume)

        return up_vol_ratio
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteVStd5Corr60Bias120(FutureFactor):
    '''
    Description: mean(corr(pct_chg(close, 1), volume, 15), 120) / std(corr(pct_chg(close, 1), volume, 15), 120)
    Class: PV_corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'volume']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        volume = data['volume_cont_IC'].values
        r = np.diff(close) / close[:-1]
        volume_sum_5 = bn.move_sum(volume, 5)
        volatility_5 = bn.move_std(r, 5)
        volume_volatility_corr = self.rolling_corr(volume_sum_5[-200:], volatility_5[-200:], 60)
        f = (volume_volatility_corr[-1] - np.nanmean(volume_volatility_corr[-120:])) / np.nanstd(volume_volatility_corr[-120:])
        if np.isnan(f):
            f = 0
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBuySellNumStdRatio(FutureFactor):
    '''
    Description: ts_mean(cs_std(BuyTradeNum) / cs_std(SellTradeNum), 5)
    Class: Buy_Sell
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 5

        buy = data['BuyTradeNum'].values[-n:]
        sell = data['SellTradeNum'].values[-n:]

        buy_std = np.nanstd(buy, axis=1)
        sell_std = np.nanstd(sell, axis=1)

        return np.nanmean(buy_std / sell_std)
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexOmega_Refined(FutureFactor):
    '''
    Description: cs_mean(ts_omega(close, 150))
    Class: Return_Risk
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        
        N = 150
        r = (np.diff(close_adj, axis=0) / close_adj[:-1])[-N:] 
        
        omega = []
        for i in range(len(r[0])):
            r_sorted = np.sort(r[:,i])
            cdf = np.arange(0, 1, 1/len(r_sorted)) + 1/len(r_sorted)
            p = 1 / len(r_sorted)
            positive = np.sum((1-cdf[r_sorted>0])*p)
            negative = np.sum(cdf[r_sorted<0]*p)
            omega_one = positive / negative
            if omega_one == np.inf:
                omega_one = np.nan
            omega = np.append(omega, omega_one)
        f = np.nanmean(omega)
                        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteICIFConvexityDiff(FutureFactor):
    '''
    Description: mean(pct_chg(pct_chg(close_000905.SH, 1), 1) - pct_chg(pct_chg(close_000300.SH, 1), 1), 90)
    Class: Multi-Variety
    Author: jinpx, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000300.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        IC_close = data['close_000905.SH'].values
        IF_close = data['close_000300.SH'].values
        
        IC_r = np.diff(IC_close) / IC_close[:-1]
        IF_r = np.diff(IF_close) / IF_close[:-1]
        
        IC_convexity = np.diff(IC_r) / IC_r[:-1]
        IF_convexity = np.diff(IF_r) / IF_r[:-1]
        
        N = 90        
        convexity_diff = IC_convexity[-N:] - IF_convexity[-N:]
        convexity_diff[np.isinf(convexity_diff)] = np.nan
        f = np.nanmean(convexity_diff)        
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteConsecutiveUpRatio30(FutureFactor):
    '''
    Description: sum(where((delay(close_000905.SH, 2) < delay(close_000905.SH, 1)) & (close_000905.SH < delay(close_000905.SH, 1)), 1, 0), 30)
                / sum(where(delay(close_000905.SH, 1) < close_000905.SH, 1, 0), 30)
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        close_temp = close_temp[~np.isnan(close_temp)]
        
        up = (close[1:] > close[:-1]).sum()
        consecutive_up = ((close_temp[:-2] < close_temp[1: -1]) & (close_temp[2:] > close_temp[1: -1])).sum()
       
        return consecutive_up / up
##########
import numpy as np
from future_factor import FutureFactor

class MinuteWeightedConsensusUpDownRatio(FutureFactor):
    '''
    Description: (weighted_up_count - weighted_down_count) / (weighted_up_count + weighted_down_count),
weighted_up_count = sum(where(Contract0[-30:] > Contract0[-31: -1] & ... & Contract3[-30:] > Contract3[-31: -1], range(1, 31), nan)),
weighted_down_count = sum(where(Contract0[-30:] < Contract0[-31: -1] & ... & Contract3[-30:] < Contract3[-31: -1], range(1, 31), nan))
    Class: MTM
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Other_Future_Instrument'] = {'00':['close'], '01':['close'], '02':['close'], '03':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        close_00 = data['close_00'].values
        close_01 = data['close_01'].values
        close_02 = data['close_02'].values
        close_03 = data['close_03'].values
        
        N = 30
        w = np.arange(1, N+1)
        up_0 = close_00[-N:] > close_00[-N-1:-1]
        up_1 = close_01[-N:] > close_01[-N-1:-1]
        up_2 = close_02[-N:] > close_02[-N-1:-1]
        up_3 = close_03[-N:] > close_03[-N-1:-1]
        up_index = index_close[-N:] > index_close[-N-1:-1]
        w_up = w[up_0 & up_1 & up_2 & up_3 & up_index].sum()
        w_down = w[~(up_0 | up_1 | up_2 | up_3 | up_index)].sum()
        f = (w_up - w_down) / (w_up + w_down)
        if np.isnan(f) or np.isinf(f):
            f = 0
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBidAskRatioSharpe(FutureFactor):
    '''
    Description: cs_mean(Shapre((TotalBidVol - TotalAskVol) / (TotalBidVol + TotalAskVol), 15)
    Class: Bid_Ask
    Author: liuz, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        totalbidvol = data['TotalBidVol'].values
        totalaskvol = data['TotalAskVol'].values

        N = 15
        bid_ask_pressure = (totalbidvol[-N:] - totalaskvol[-N:]) / (totalbidvol[-N:] + totalaskvol[-N:])
        bid_ask_pressure_mean = np.nanmean(bid_ask_pressure, axis=0)
        bid_ask_pressure_std = np.nanstd(bid_ask_pressure, axis=0)
        f = np.nanmean(bid_ask_pressure_mean[bid_ask_pressure_std!=0] / bid_ask_pressure_std[bid_ask_pressure_std!=0])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexVOIMean(FutureFactor):
    '''
    Description: ts_mean((cs_sum(where(close > delay(close, 1), BuyTradeMoney, 0)) - cs_sum(where(close < delay(close, 1), SellTradeMoney, 0)))
                / (cs_sum(where(close > delay(close, 1), BuyTradeMoney, 0)) + cs_sum(where(close < delay(close, 1), SellTradeMoney, 0))), 60)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close', 'BuyTradeMoney', 'SellTradeMoney']
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeMoney'].values
        sell = data['SellTradeMoney'].values
        
        buy_up = np.nansum(np.where(close[-lb:] > close[-lb - 1: -1], buy[-lb:], np.nan), axis=1)
        sell_down = np.nansum(np.where(close[-lb:] < close[-lb - 1: -1], sell[-lb:], np.nan), axis=1)
        ratio = (buy_up - sell_down) / (buy_up + sell_down)
        
        return ratio.mean()
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew


class  MinuteIndexBidAskRatioMA5(FutureFactor):
    '''
    Description: ts_mean(weighted_cs_mean(Bid1AmtMean, w=index_weight) / weighted_cs_mean(Ask1AmtMean, w=index_weight), 5)
    Class:Bid_Ask
    Author:  shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['Bid1AmtMean', 'Ask1AmtMean', 'weight']

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        Ask1AmtMean = data['Ask1AmtMean'].values[-5:]
        Bid1AmtMean = data['Bid1AmtMean'].values [-5:]
        weight = data['weight'].values[-5:]
        askbidratio = np.nansum(Bid1AmtMean*weight,axis=1) / np.nansum(Ask1AmtMean*weight,axis=1)
        factor = np.nanmean(askbidratio[-5:])
        return factor


##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBuySellNumSkewRatio(FutureFactor):
    '''
    Description: ts_mean(cs_skew(BuyTradeNum) / cs_skew(SellTradeNum), 10)
    Class: Buy_Sell
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 10

        buy = data['BuyTradeNum'].values[-n:]
        sell = data['SellTradeNum'].values[-n:]

        buy_skew = stats.skew(buy, axis=1, nan_policy='omit')
        sell_skew = stats.skew(sell, axis=1, nan_policy='omit')

        return np.nanmean(buy_skew / sell_skew)
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk

class MinuteIndexHighLowBuyRatio(FutureFactor):
    '''
    Description: ts_mean(where(close_000905.SH > quantile(close_000905.SH, 2/3, 30), buyratio, nan), 30)
                / ts_mean(where(close_000905.SH < quantile(close_000905.SH, 1/3, 30), buyratio, nan), 30),
                buyratio = cs_mean(BuyTradeMoney / (BuyTradeMoney + SellTradeMoney))
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        buy = data['BuyTradeMoney']
        close = data['close_000905.SH'].reindex(index = buy.index).values.flatten()
        close[close == 0] = np.nan
        buy = buy.values
        sell = data['SellTradeMoney'].values
        
        minute_past = min(len(buy) - 237, 5)
        factor_temp_list = []
        for i in range(minute_past):
            if i == 0:
                buy_sell_ratio = np.nanmean(buy[-lb:] / (buy[-lb:] + sell[-lb:]), axis=1)
                close_temp = close[-lb:]
            else:
                buy_sell_ratio = np.nanmean(buy[-(lb + i):-i] / (buy[-(lb + i):-i] + sell[-(lb + i):-i]), axis=1)
                close_temp = close[-(lb + i):-i]
            rank = bk.rankdata(close_temp)
            f = buy_sell_ratio[rank<=10].mean() / buy_sell_ratio[rank>20].mean()
            if np.isnan(f) or np.isinf(f):
                factor_temp_list.append(1)
            else:
                factor_temp_list.append(f)
                
        return np.mean(factor_temp_list)
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioSharpe(FutureFactor):
    '''
    Description: ts_mean(weighted_cs_mean(BuyTradeQuantity / SellTradeQuantity - 1, w=index_weight), 90)
                / ts_std(weighted_cs_mean(BuyTradeQuantity / SellTradeQuantity - 1, w=index_weight), 90)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 90
        weight = data['weight'].values
        buy = data['BuyTradeQuantity'].values
        sell = data['SellTradeQuantity'].values
        
        ratio = buy[-lb:] / sell[-lb:] - 1
        ratio[np.isinf(ratio)] = np.nan
        ratio = np.nansum(ratio * weight[-lb:], axis=1)
        f = np.nanmean(ratio) / np.nanstd(ratio)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteCloseminusOpenStd_Refined(FutureFactor):
    '''
    Description: 
    Class: Price_Stat 
    Author: jinpx, modified by liuz
    '''
    def __init__(self):
        super().__init__()
        self.rolling_std = []

    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close_price = data['close_cont_IC'].values
        open_price = data['open_cont_IC'].values
        close_minus_open = close_price - open_price
        
        N1 = 30
        N2 = 5*240
        if len(self.rolling_std) == 0:
            for i in range(N2, -1, -1):
                self.rolling_std.append(np.nanstd(close_minus_open[-(i+N1):][:N1]))
        else:
            self.rolling_std.append(np.nanstd(close_minus_open[-N1:]))

        f = (self.rolling_std[-1] - np.nanmean(self.rolling_std[-(N2+1):-1])) / np.nanstd(self.rolling_std[-(N2+1):-1])

        return f
##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteResidualRtnSkew(FutureFactor):
    '''
    Description:skew(residual_return, 60),
                residual_return = close_000905.SH / predicted_price - 1,
                predicted_price = linear_regression(x=range(1, 61), y=close_000905.SH[-60:], intercept=True).predict(x=range(1, 61))
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        
        x = np.array((np.ones(lb), np.arange(1, lb + 1)))
        y = close[-lb:]
        b = np.linalg.inv(x.dot(x.T)).dot(x.dot(y))
        y_hat = b.dot(x)
        f = -skew(y / y_hat - 1)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLatestResidualAbs(FutureFactor):
    '''
    Description: abs(mean(linear_regression_residual(x=range(1, 121), y=close_000905.SH[-120:], intercept=True), 5))
    Class: Convexity
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 120
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        
        x = np.concatenate((np.ones((lb, 1)), np.arange(1, lb + 1).reshape((lb, -1))), axis=1)
        close_temp = close[-lb:]
        close_temp = close_temp[~np.isnan(close_temp)]
        y = close_temp.reshape((len(close_temp), -1))
        coef = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)
        y_hat = x.dot(coef)
        
        return abs(np.mean(y[-5:, 0]) - np.mean(y_hat[-5:, 0]))
##########
from future_factor import FutureFactor
import numpy as np


class MinuteTypicalFutureIndexCorr(FutureFactor):
    '''
    Description: corr((close + high + low) / 3, (close_000905.SH + high_000905.SH + low_000905.SH) / 3, 45)
    Class: Future_Spot_Price
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low']}
    data_dict['Index_Id'] = {'000905.SH': ['close', 'high', 'low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        typical = (data['close_cont_IC'].values[-45:] + data['high_cont_IC'].values[-45:] + data['low_cont_IC'].values[-45:]) / 3
        index_typical = (data['close_000905.SH'].values[-45:] + data['high_000905.SH'].values[-45:] + data['low_000905.SH'].values[-45:]) / 3
        f = np.corrcoef(typical, index_typical)[0, 1]
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteBidAskVolRatio(FutureFactor):
    '''
    Description: mean(bidvao_ratio + askvol_ratio, 60), where
                bidvol_ratio = bidvol / (the average bidvol at current time over past 5 trading days)
                askvol_ratio = askvol / (the average askvol at current time over past 5 trading days)
    Class: 
    Author: lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol','AskVol']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 60
        bidvol_list = data['BidVol_cont_IC'].values
        askvol_list = data['AskVol_cont_IC'].values
        
        bidvol_ratio = (bidvol_list[-240:] / np.nanmean(bidvol_list[-240*6:-240].reshape(5, 240), axis = 0))[-n:]
        askvol_ratio = (askvol_list[-240:] / np.nanmean(askvol_list[-240*6:-240].reshape(5, 240), axis = 0))[-n:]
        factor_value = np.nanmean(bidvol_ratio + askvol_ratio)
        
        return factor_value
##########
from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexTurnoverCSSkew(FutureFactor):
    '''
    Description: -ts_mean(cs_skew(amount), 15)
    Class: Liq_Cs_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['amount']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount'].values[-15:]
        amount[amount == 0] = np.nan
        f = -np.nanmean(skew(amount, axis=1, nan_policy='omit'))
        return f

##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowBuySellUniqueOrderNumSumReturnDiff(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'close', 'adjfactor']
    normalize_size = 60
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        BuySellUniqueOrderNumSum = BuyUniqueOrderNum + SellUniqueOrderNum
        N = 1 * 237
        BuySellUniqueOrderNumSum_mean = np.nanmean(BuySellUniqueOrderNumSum[-N:], axis=0)
        BuySellUniqueOrderNumSum_mean_rank = (bn.rankdata(BuySellUniqueOrderNumSum_mean)-1)/(len(BuySellUniqueOrderNumSum_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[BuySellUniqueOrderNumSum_mean_rank>0.8]) - np.nanmean(r_sum[BuySellUniqueOrderNumSum_mean_rank<0.2])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteVR1Corr15Sr120(FutureFactor):
    '''
    Description: mean(corr(pct_chg(close, 1), volume, 15), 120) / std(corr(pct_chg(close, 1), volume, 15), 120)
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'volume']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        volume = data['volume_cont_IC'].values
        r = (close[1:] - close[:-1]) / close[:-1]
        r_volume_corr_15 = self.rolling_corr(r, volume[1:], 15)
        f = np.nanmean(r_volume_corr_15[-120:]) / np.nanstd(r_volume_corr_15[-120:], ddof=1)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteICIFAskBidVolPressureDiff(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['AskVol', 'BidVol'], 'IF': ['AskVol', 'BidVol']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol_IC = data['AskVol_cont_IC'].values
        BidVol_IC = data['BidVol_cont_IC'].values
        AskVol_IF = data['AskVol_cont_IF'].values
        BidVol_IF = data['BidVol_cont_IF'].values
        
        pressure_IC = AskVol_IC - BidVol_IC
        pressure_IF = AskVol_IF - BidVol_IF
        
        N = 10
        f = np.nanmean(pressure_IC[-N:]) - np.nanmean(pressure_IF[-N:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHLCorrRetDiff(FutureFactor):
    '''
    Description: mean(return((rank(corr) > 0.5), 120min)) - mean(return((rank(corr) < 0.5), 120min))
                 corr = corr(close,close_000905.SH, 120min)
    Class: Group Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        threshold = 0.5
        n = 120
        adjfactor = data['adjfactor'].values
        stock_close = data['close'].values * adjfactor
        index_close = data['close_000905.SH'].values.flatten()
        
        stock_ret = stock_close[-n:] / stock_close[-(n + 1):-1] - 1
        index_ret = index_close[-n:] / index_close[-(n + 1):-1] - 1
        corr_list = []
        for i in range(stock_close.shape[1]):
            corr = np.corrcoef(stock_ret[:,i], index_ret)[0,1]
            corr_list.append(corr)
        corr_array = np.array(corr_list)
        corr_rank = bn.rankdata(corr_array) / len(corr_array)
        
        stock_ret_mean = np.nanmean(stock_ret,axis = 0)
        factor_value = np.nanmean(stock_ret_mean[corr_rank > threshold]) - np.nanmean(stock_ret_mean[corr_rank <= (1 - threshold)])
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class MinuteOpenInterestRtnCorr(FutureFactor):
    '''
    Description: corr(close / open - 1, OpenInterest, 250)
    Class: PV_Corr
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 2
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['OpenInterest', 'close', 'open']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_cont_IC'].values[-250:]
        open_px = data['open_cont_IC'].values[-250:]
        interest = data['OpenInterest_cont_IC'].values[-250:]
        f = np.corrcoef(interest, close / open_px - 1)[0, 1]
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexOmega(FutureFactor):
    '''
    Description: cs_mean(omega_top_bottom),
                 omega_top_bottom = omega[(omega >= cs_rank(-omega, 10)) | (omega <= cs_rank(omega, 10))],
                 omega = positive_p / negative_p,
                 positive_p = positive_num * (positive_num - 1) / 2 * (1 / 180) ** 2,
                 negative_p = negative_num * (negative_num + 1) / 2 * (1 / 180) ** 2,
                 positive_num = ts_sum(where(pct_chg(close, 1) > 0, 1, 0), 180),
                 negative_num = ts_sum(where(pct_chg(close, 1) < 0, 1, 0), 180).
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        close = data['close'].values[-181:]
        adj = data['adjfactor'].values[-181:]
        close = close * adj
        close[close == 0] = np.nan
        rtn = np.diff(close, axis=0) / close[:-1]
        positive_num = np.sum(rtn > 0, axis=0)
        negative_num = np.sum(rtn < 0, axis=0)
        omega_list = []
        for j in range(rtn.shape[1]):
            rtn_sorted = np.sort(rtn[:, j])
            cdf = np.arange(0, 1, 1 / len(rtn_sorted)) + 1 / len(rtn_sorted)
            p = 1 / len(rtn_sorted)
            positive = np.sum((1 - cdf[rtn_sorted > 0]) * p)
            negative = np.sum(cdf[rtn_sorted < 0] * p)
            omega = positive / negative
            if np.isinf(omega):
                omega = np.nan
            omega_list.append(omega)
        omega_sorted = np.sort(omega_list)
        f = np.nanmean(np.append(omega_sorted[:10], omega_sorted[-10:]))
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_Normal5dayAPO6020Delta60AskVol(FutureFactor):
    '''
    Description: APO_60_20(Delta_60(AskVol))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['AskVol']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        ask_vol = data['AskVol_cont_IC'].values

        ask_vol_delta_60 = ask_vol[60:] - ask_vol[:-60]
        apo = bn.move_mean(ask_vol_delta_60, 20) - bn.move_mean(ask_vol_delta_60, 60)

        apo_mean = np.nanmean(apo[-5 * 240 - 1:-1])
        apo_std = np.nanstd(apo[-5 * 240 - 1:-1])

        factor_value = (apo[-1] - apo_mean) / apo_std

        if np.isnan(factor_value):
            factor_value = 0

        return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class MinuteOpenInterestReturnCorrtimesReturn(FutureFactor):
    '''
    Description: -mean(pct_chg(close_000905.SH, 1), 60) * corr(pct_chg(close_000905.SH, 1), OpenInterest, 720)
    Class: PV_Corr
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 3
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['OpenInterest']}
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000905.SH'].values[-237 * self.days_past - 1:]
        interest = data['OpenInterest_cont_IC'].values[-237 * self.days_past:]
        r = np.diff(close) / close[:-1]
        f = -np.nanmean(r[-60:]) * np.corrcoef(interest, r)[0, 1]
        return f

##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIlliq5Swing30(FutureFactor):
    '''
    Description: max(abs(pct_chg(Index_ClosePx, 5)) / sum(Index_Volume, 5), 30) - min(abs(pct_chg(Index_ClosePx, 5)) / sum(Index_Volume, 5), 30)
    Class: Liquidity
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        index_close = data['close_000905.SH'].values
        index_volume = data['volume_000905.SH'].values
        
        index_r_5 = (index_close[5:] - index_close[:-5]) / index_close[:-5]
        index_volume_sum_5 = bn.move_sum(index_volume, 5)
        
        N = 30
        illiquidity = np.abs(index_r_5[-N:]) / index_volume_sum_5[-N:]
        f = np.max(illiquidity) - np.min(illiquidity)
        
        return f
##########
import numpy as np
from scipy.stats import skew
from future_factor import FutureFactor

class MinuteMACDSkew(FutureFactor):
    '''
    Description: Skew(MACD(close, 12, 26, 9), 60)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def ewma_vectorized(self, data, alpha, offset=None, dtype=None, order='C', out=None):
        """
        Calculates the exponential moving average over a vector.
        Will fail for large inputs.
        :param data: Input data
        :param alpha: scalar float in range (0,1)
            The alpha parameter for the moving average.
        :param offset: optional
            The offset for the moving average, scalar. Defaults to data[0].
        :param dtype: optional
            Data type used for calculations. Defaults to float64 unless
            data.dtype is float32, then it will use float32.
        :param order: {'C', 'F', 'A'}, optional
            Order to use when flattening the data. Defaults to 'C'.
        :param out: ndarray, or None, optional
            A location into which the result is stored. If provided, it must have
            the same shape as the input. If not provided or `None`,
            a freshly-allocated array is returned.
        """
        data = np.array(data, copy=False)

        if dtype is None:
            if data.dtype == np.float32:
                dtype = np.float32
            else:
                dtype = np.float64
        else:
            dtype = np.dtype(dtype)

        if data.ndim > 1:
            # flatten input
            data = data.reshape(-1, order)

        if out is None:
            out = np.empty_like(data, dtype=dtype)
        else:
            assert out.shape == data.shape
            assert out.dtype == dtype

        if data.size < 1:
            # empty input, return empty array
            return out

        if offset is None:
            offset = data[0]

        alpha = np.array(alpha, copy=False).astype(dtype, copy=False)

        # scaling_factors -> 0 as len(data) gets large
        # this leads to divide-by-zeros below
        scaling_factors = np.power(1. - alpha, np.arange(data.size + 1, dtype=dtype),
                                   dtype=dtype)
        # create cumulative sum array
        np.multiply(data, (alpha * scaling_factors[-2]) / scaling_factors[:-1],
                    dtype=dtype, out=out)
        np.cumsum(out, dtype=dtype, out=out)

        # cumsums / scaling
        out /= scaling_factors[-2::-1]

        if offset != 0:
            offset = np.array(offset, copy=False).astype(dtype, copy=False)
            # add offsets
            out += offset * scaling_factors[1:]

        return out

    def MACD(self, close):

        window_short = 12
        window_long = 26
        window_mid = 9

        ema_short = self.ewma_vectorized(close, 2/(window_short+1))
        ema_long = self.ewma_vectorized(close, 2/(window_long+1))
        dif = ema_short[-(len(close)-window_long):] - ema_long[-(len(close)-window_long):]
        dea = self.ewma_vectorized(dif, 2/(window_mid+1))

        macd = dif[-(len(dif)-window_mid):] - dea[-(len(dif)-window_mid):]

        return macd
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].values
        
        N = 60
        macd = self.MACD(close)
        f = skew(macd[-N:])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteICIFUpNum(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 237
        close_300 = data['close_000300.SH'].values
        close_500 = data['close_000905.SH'].values
        f = ((close_300[1:] > close_300[:-1])[-lb:] & (close_500[1:] > close_500[:-1])[-lb:]).sum()
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownRtnMean(FutureFactor):
    '''
    Description: weighted_cs_mean(((close[-1] / ts_max(close, 240) - 1) / (240 - ts_arg_max(close, 240)) 
                + (close[-1] / ts_min(close, 240) - 1) / (240 - ts_argmin(close, 240))) / 2, w=index_weight)
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'adjfactor', 'close']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        close_price = close[-lb:]
        mask = np.all(np.isnan(close_price), axis=0)
        close_price = close_price[:, ~mask]
        argmax = lb - np.nanargmax(close_price, axis=0)
        rtn_0 = (close_price[-1] / np.nanmax(close_price, axis=0) - 1) / argmax
        argmin = lb - np.nanargmin(close_price, axis=0)
        rtn_1 = (close_price[-1] / np.nanmin(close_price, axis=0) - 1) / argmin
        rtn = (rtn_1 + rtn_0) / 2
        f = np.nansum(rtn * weight[-1][~mask])
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60Ret2AutoCorr(FutureFactor):
    '''
    Description: corr(pct_chg(Index_ClosePx,1), delay(pct_chg(Index_ClosePx,1),2), 60)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 30 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 2
        n2 = 60
        index_close = data['close_000905.SH'].values[-n2 - 1:]
        rtn = index_close[1:] / index_close[:-1] - 1

        rtn_shift_2 = rtn[n1:]

        return np.corrcoef(rtn[:-n1], rtn_shift_2)[0, 1]
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAmountStd(FutureFactor):
    '''
    Description: std(close_000905.SH * volume_000905.SH, 20) / mean(close_000905.SH * volume_000905.SH, 90)
    Class: Liquidity
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['close', 'volume']}
    normalize_size = 40 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000905.SH'].values[-90:]
        volume = data['volume_000905.SH'].values[-90:]
        close_volume = close * volume
        f = np.nanstd(close_volume[-20:]) / np.nanmean(close_volume)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteDownsideReSR30(FutureFactor):
    '''
    Description: mean(where(pct_chg(index_close, 1) > 0, 0, pct_chg(index_close, 1)), 30) / std(where(pct_chg(index_close, 1) > 0, 0, pct_chg(index_close, 1)), 30)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''  
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].values
        index_r = np.diff(index_close) / index_close[:-1]
        index_r[index_r>=0] = 0
        f = np.nanmean(index_r[-30:]) / np.nanstd(index_r[-30:])
        if np.isnan(f):
            f = 0
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteOBVolClose30Corr(FutureFactor):
    '''
    Description: -corr(ClosePx, AskVol + BidVol, 30)
    Class: PV_Corr
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['AskVol', 'BidVol','close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IC'].values 
        BidVol = data['BidVol_cont_IC'].values 
        close = data['close_cont_IC'].values 

        ob_vol = AskVol+BidVol
        factor = -np.corrcoef(ob_vol[-30:], close[-30:])[0,1]
        return  factor
    

##########
import numpy as np
from future_factor import FutureFactor

class MinuteCloseTurnoverRatioCorrAbs(FutureFactor):
    '''
    Description: abs(corr(close_000905.SH, amount_ratio, 60)),
                 amount_ratio =  / (the average amount_000905.SH at current time over past 5 trading days)
    Class: PV_Corr
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        turn = data['amount_000905.SH'].values
        past_turn = turn[:237 * 6].reshape(6, -1)
        past_turn_ratio = past_turn[-1] / np.nanmean(past_turn[:-1], axis=0)
        turn_mean = np.nanmean(past_turn[1:], axis=0)
        
        lb = 60
        today_turn = turn[-237:]
        turn_ratio = np.concatenate((past_turn_ratio, today_turn / turn_mean[:len(today_turn)]))
        close_temp = close[-lb:]
        turn_ratio_temp = turn_ratio[-lb:]
        mask = np.isnan(close_temp) | np.isnan(turn_ratio_temp)
        f = np.abs(np.corrcoef(close_temp[~mask], turn_ratio_temp[~mask])[0,1])
            
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteBounceUpStdRatio(FutureFactor):
    '''
    Description: max((close_000905.SH - cum_min(low_000905.SH)) / cum_min(low_000905.SH), 40) /
                 std(where(close_000905.SH > delay(close_000905.SH, 1), pct_chg(close_000905.SH, 1), 40))
    Class: Return_Risk
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','low']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 40
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        low = data['low_000905.SH'].values
        low[low == 0] = np.nan
        low_temp = low[-lb:] 
        mask = np.isnan(close_temp) | np.isnan(low_temp)
        close_temp = close_temp[~mask]
        low_temp = low_temp[~mask]
        
        cum_min = np.minimum.accumulate(low_temp)
        mbb = ((close_temp - cum_min) / cum_min).max()
        r = close_temp[1:] / close_temp[:-1] - 1
        up_std = r[r > 0].std()
        
        if up_std == 0 or np.isnan(up_std):
            up_ratio = 0
        else:
            up_ratio = mbb / up_std
            
        return up_ratio
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexBuyMoneyRatioMean(FutureFactor):
    data_type = 'IndexStock'
    days_past = 7
    data_dict = {}
    data_dict['Stock'] = ['BuyTradeMoney']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        buy_money = data['BuyTradeMoney'].values[-6 * 237:]
        buy_money[buy_money == 0] = np.nan
        nan_num = np.isnan(buy_money).sum(axis=0)
        buy_money = buy_money[:, nan_num == 0]
        buy_money = buy_money.reshape(6, 237, -1)
        buy_ratio = buy_money[-1] / np.nanmean(buy_money[:-1], axis=0)
        f = np.nanmean(buy_ratio[-lb:])
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteContract1PVCorr(FutureFactor):
    '''
    Description: -corr(close_01, volume_01, 90)
    Class: All_Contract
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Other_Future_Instrument'] = {'01': ['close', 'volume']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_01'].values[-90:]
        volume = data['volume_01'].values[-90:]
        f = -np.corrcoef(close, volume)[0, 1]
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteHighLowCorr(FutureFactor):
    '''
    Description: corr(high, low, 90)
    Class: Price_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['high', 'low']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high_cont_IC'].values[-90:]
        low = data['low_cont_IC'].values[-90:]
        f = np.corrcoef(high, low)[0, 1]
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexUniqueBuyRatioMA10(FutureFactor):
    '''
    Description: -cs_mean(ts_mean(BuyUniqueOrderNum, 10)) / cs_mean(ts_mean(BuyTradeNum, 10))
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 10

        buy_unique_num = data['BuyUniqueOrderNum'].values[-n:]
        buy_trade_num = data['BuyTradeNum'].values[-n:]

        buy_unique_num_mean = np.nanmean(np.nanmean(buy_unique_num))
        buy_trade_num_mean = np.nanmean(np.nanmean(buy_trade_num))

        factor_value = -buy_unique_num_mean / buy_trade_num_mean

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowWeightReturnDiff(FutureFactor):
    '''
    Description: ts_mean(cs_mean(rtn_high), 30) - ts_mean(cs_mean(rtn_low), 30),
                 rtn_high = pct_chg(close * adjfactor, 1)[:, weight[-1] > quantile(weight[-1], 0.8)],
                 rtn_low = pct_chg(close * adjfactor, 1)[:, weight[-1] < quantile(weight[-1], 0.2)].
    Class: Group_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        weight = data['weight'].values[-1]
        close = data['close'].values[-31:]
        close[close == 0] = np.nan
        adj = data['adjfactor'].values[-31:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        rtn_high = np.nanmean(rtn[:, weight > np.nanquantile(weight, 0.8)], axis=1)
        rtn_low = np.nanmean(rtn[:, weight < np.nanquantile(weight, 0.2)], axis=1)
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_CMO60MidPoint30Rank60BidVol(FutureFactor):
    '''
    Description: CMO_60(MidPoint_30(Rank_60(BidVol)))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        rank_60 = data['BidVol_cont_IC'].rolling(60).apply(lambda x: x.searchsorted(x[-1], sorter=np.argsort(x)),
                                                   raw=True).fillna(0).values
        rank_60[np.isnan(rank_60)] = 0

        mid_point_30 = (bn.move_max(rank_60, 30) + bn.move_min(rank_60, 30)) / 2
        mid_point_30[np.isnan(mid_point_30)] = 0

        mid_point_rtn = mid_point_30[-60:] / mid_point_30[-61:-1] - 1
        mid_point_rtn[np.isinf(mid_point_rtn)] = np.nan

        pos_rtn = np.copy(mid_point_rtn)
        pos_rtn[pos_rtn < 0] = 0

        neg_rtn = np.copy(mid_point_rtn)
        neg_rtn[neg_rtn > 0] = 0

        pos_rtn_sum = np.nansum(pos_rtn[-60:])
        neg_rtn_sum = np.nansum(-neg_rtn[-60:])

        factor_value = (pos_rtn_sum - neg_rtn_sum) / (pos_rtn_sum + neg_rtn_sum)

        return factor_value

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighVolumeCorr(FutureFactor):
    '''
    Description: abs(cs_mean(ts_corr(high, volume, 60)))
    Class: PV_Corr
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high', 'volume', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        N = 60
        high = data['high'].values[-N:]
        volume = data['volume'].values[-N:]
        adjfactor = data['adjfactor'].values[-N:]
        high_adj = high * adjfactor
        volume_adj = volume / adjfactor
        
        c = np.array([])
        for i in range(len(high_adj[-1])):
            c = np.append(c, np.corrcoef(high_adj[:,i], volume_adj[:,i])[0,1])
        
        f = np.abs(np.nanmean(c))
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinutePosInterestRet(FutureFactor):
    '''
    Description:
    Class: PV_Corr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['interest', 'close']}
    normalize_size = 15 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        interest = data['interest_cont_IC'].values[-n:]
        close = data['close_cont_IC'].values[-n - 1:]

        rtn = close[1:] / close[:-1] - 1

        factor_value = np.nanmean(rtn[interest > 0])

        if np.isinf(factor_value) or np.isnan(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowBuySellTradeNumSumReturnDiff(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'close', 'adjfactor']
    normalize_size = 120
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        BuyTradeNum = data['BuyTradeNum'].values
        SellTradeNum = data['SellTradeNum'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        BuySellTradeNumSum = BuyTradeNum + SellTradeNum
        N = 3 * 237
        BuySellTradeNumSum_mean = np.nanmean(BuySellTradeNumSum[-N:], axis=0)
        BuySellTradeNumSum_mean_rank = (bn.rankdata(BuySellTradeNumSum_mean)-1)/(len(BuySellTradeNumSum_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[BuySellTradeNumSum_mean_rank>0.8]) - np.nanmean(r_sum[BuySellTradeNumSum_mean_rank<0.2])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew

class  MinuteFutureBasis120Skew(FutureFactor):
    '''
    Description: -skew(ClosePx - Index_ClosePx, 120)
    Class:Future_Spot_Price
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()

    data_dict['Continuous_Data'] = {'IC': ['close']}
    data_dict['Index_Id'] = {'000905.SH':['close']}

    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close_list = data['close_000905.SH'].values
        close_list = data['close_cont_IC'].values
        future_basis_list = close_list-index_close_list
        
        factor = -skew(future_basis_list[-120:])
        return factor
    
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexKappaRatio(FutureFactor):
    '''
    Description: cs_mean(kappa_top_bottom),
                 kappa_top_bottom = kappa[(kappa >= cs_rank(-kappa, 10)) | (kappa <= cs_rank(kappa, 10))],
                 kappa = ts_mean(diff(close * adjfactor, 1), 150) / ts_max(-diff(close * adjfactor, 1), 150).
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        close = data['close'].values[-151:]
        adj = data['adjfactor'].values[-151:]
        close = close * adj
        close[close == 0] = np.nan
        diff = np.diff(close, axis=0)
        kappa = np.nanmean(diff, axis=0) / np.max(-diff, axis=0)
        kappa[np.isinf(kappa)] = np.nan
        kappa_sorted = np.sort(kappa)
        f = np.nanmean(np.append(kappa_sorted[:10], kappa_sorted[-10:]))
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowBetaRtnDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 120
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 237
        adj = data['adjfactor'].values
        close = (data['close'].values * adj / adj[-1])[-lb - 1:]
        rtn = close[1:] / close[:-1] - 1
        zero_num = (np.abs(rtn) < 1 / 10000).sum(axis=0)
        rtn = rtn[:, zero_num < (lb / 2)]
        
        index_close = data['close_000905.SH'].values[-lb - 1:]
        index_close = index_close.reshape(len(index_close), -1)
        index_rtn = index_close[1:] / index_close[:-1] - 1
        
        beta = np.mean((rtn - np.mean(rtn, axis=0)) * (index_rtn - np.mean(index_rtn)), axis=0) / np.var(index_rtn)
        median = np.nanmedian(beta)
        
        rtn_high = rtn[:, (beta > median)]
        rtn_low = rtn[:, (beta <= median)]
        
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighTreynorRatioReturn(FutureFactor):
    '''
    Description: cs_mean(ts_mean(rtn_high, from 09:30 T-5)),
                 rtn_high = rtn[:, TreynorRatio > percentile(TreynorRatio, 90)],
                 TreynorRatio = alpha / beta,
                 alpha = ts_mean(rtn, from 09:30 T-5) - ts_mean(rtn_000905.SH, ffrom 09:30 T-5),
                 beta = cov(rtn, rtn_000905.SH) / var(rtn_000905.SH),
                 rtn = pct_chg(close * adjfactor, 1),
                 rtn_000905.SH = pct_chg(close_000905.SH, 1).
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 5
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        idx = data['close'].index
        close = data['close'].values
        close[close == 0] = np.nan
        adj = data['adjfactor'].values
        adj[adj == 0] = np.nan
        index_close = data['close_000905.SH'].reindex(index=idx).values
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        index_rtn = np.diff(index_close, axis=0) / index_close[:-1]
        beta = ((rtn - np.mean(rtn, axis=0)) * (index_rtn - np.mean(index_rtn))).mean(axis=0) / np.var(index_rtn)
        beta[beta < 0] = np.nan
        rtn_mean = np.nanmean(rtn, axis=0)
        index_rtn_mean = np.nanmean(index_rtn)
        tr = (rtn_mean - index_rtn_mean) / beta
        f = np.nanmean(rtn_mean[tr > np.percentile(tr[~np.isnan(tr)], 90)])
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnWeightRatioRetDiff(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'weight']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 10
        n2 = 60

        close = data['close'].values[-(n1 + 1):]
        rtn = close[-1] / close[-(n1 + 1)] - 1

        weight = data['weight'].values[-n2:]
        turnover = data['amount'].values[-n2:]

        turnover_weight_ratio = turnover / weight
        turnover_weight_ratio = np.where(np.isinf(turnover_weight_ratio), np.nan, turnover_weight_ratio)

        turnover_weight_ratio_rank = self.rank(np.nanmean(turnover_weight_ratio, axis=0), ascending=True, pct=True)

        factor_value = np.nansum(rtn[turnover_weight_ratio_rank > 0.9]) - np.nansum(
            rtn[turnover_weight_ratio_rank < 0.1])

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHLCloseRtnDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 15

        close = data['close'].values

        rtn = close[1:] / close[:-1] - 1

        mid_close = np.nanpercentile(close[-1], 50)
        rtn_mean = np.nanmean(rtn[-n:], axis=0)

        high_rtn = rtn_mean[close[-1] > mid_close]
        low_rtn = rtn_mean[close[-1] < mid_close]

        factor_value = np.nanmean(high_rtn) - np.nanmean(low_rtn)

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownOrderImbalanceRatio(FutureFactor):
    '''
    Description: ts_mean(ts_mean(where(cs_mean(pct_chg(ClosePx, 1)) > 0, cs_mean((sum(BidVi, i=0,1,…4) - sum(AskVi, i=0,1,…,4)) / ((sum(BidVi, i=0,1,…,4) + sum(AskVi, i=0,1,…,4))), nan), 20)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        bid_0_volume = data['BidV0'].values
        bid_1_volume = data['BidV1'].values
        bid_2_volume = data['BidV2'].values
        bid_3_volume = data['BidV3'].values
        bid_4_volume = data['BidV4'].values
        ask_0_volume = data['AskV0'].values
        ask_1_volume = data['AskV1'].values
        ask_2_volume = data['AskV2'].values
        ask_3_volume = data['AskV3'].values
        ask_4_volume = data['AskV4'].values
        
        close_adj = close * adjfactor        
        r = np.diff(close_adj, axis=0) / close_adj[:-1] 

        N1 = 20
        N2 = 10
        N = N1 + N2
        bid_volume = bid_0_volume[-N:] + bid_1_volume[-N:] + bid_2_volume[-N:] + bid_3_volume[-N:] + bid_4_volume[-N:]
        ask_volume = ask_0_volume[-N:] + ask_1_volume[-N:] + ask_2_volume[-N:] + ask_3_volume[-N:] + ask_4_volume[-N:]
        order_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)

        order_imbalance_up_down_ratio_list = []
        for i in range(1, N2+1):
            r_mean = np.nanmean(r[-(N1+i):-i], axis=1)
            order_imbalance_mean = np.nanmean(order_imbalance[-(N1+i):-i], axis=1)
            order_imbalance_up_down_ratio = np.nanmean(order_imbalance_mean[r_mean>0]) / np.nanmean(order_imbalance_mean[r_mean<0])
            order_imbalance_up_down_ratio_list.append(order_imbalance_up_down_ratio) 

        f = np.nanmean(order_imbalance_up_down_ratio_list)
        if np.isnan(f):
            f = 1
            
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteRe5Std30(FutureFactor):
    '''
    Description: std(pct_chg(close, 5), 30)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].values
        
        r_5 = (close[5:] - close[:-5]) / close[:-5]
        f = np.nanstd(r_5[-30:], ddof=1)
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexEMV(FutureFactor):
    '''
    Description: cs_mean(ts_mean(diff((high_adj + low_adj) / 2, 1) * (high_adj - low_adj) * volume_adj, 20)),
                 high_adj = high * adjfactor, low_adj = low * adjfactor, volume_adj = volume / adjfactor.
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['high', 'low', 'volume', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high'].values[-21:]
        high[high == 0] = np.nan
        low = data['low'].values[-21:]
        low[low == 0] = np.nan
        volume = data['volume'].values[-20:]
        volume[volume == 0] = np.nan
        adj = data['adjfactor'].values[-21:]
        adj[adj == 0] = np.nan
        high = high * adj
        low = low * adj
        volume = volume / adj[-20:]
        mid = (high + low) / 2
        mid_g = np.diff(mid, axis=0)
        hml = high[-20:] - low[-20:]
        emv = mid_g * hml * volume
        f = np.nanmean(np.nanmean(emv, axis=0))
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor
import bottleneck as bottleneck


class MinuteIndexHLWeightDivergence(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30
        threshold = 0.2

        close = data['close'].values[-(n + 1):]
        rtn = close[-1] / close[-(n + 1)] - 1

        weight = data['weight'].values[-1]
        weight_rank = self.rank(weight, ascending=True, pct=True)

        std_1 = np.nanstd(rtn[weight_rank < threshold])
        std_2 = np.nanstd(rtn[weight_rank > (1 - threshold)])

        factor_value = std_1 / std_2

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteConvexity(FutureFactor):
    '''
    Description: mean(convexity(close_000905.SH, i), i=3,5,…119)
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 120
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close = close[-lb:]
        close = close[~np.isnan(close)]
        
        convex = []
        for i in range(3, len(close), 2):
            convex.append(abs((close[-1] + close[-i] - 2 * close[-int((i + 1) / 2)]) / close[-int((i + 1) / 2) - 1]))
       
        return np.nanmean(convex)
##########
import numpy as np
from scipy.stats import skew
from future_factor import FutureFactor

class MinuteIndexBuySellRatioSkew(FutureFactor):
    '''
    Description: -ts_skew(cs_mean(BuyTradeQuantity / SellTradeQuantity - 1), 60)
    Class: Buy_Sell
    Author: hefj, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        buytradequantity = data['BuyTradeQuantity'].values
        selltradequantity = data['SellTradeQuantity'].values

        N = 60
        buy_sell_trade_quantity_ratio = buytradequantity[-N:] / selltradequantity[-N:]
        buy_sell_trade_quantity_ratio[np.isinf(buy_sell_trade_quantity_ratio)] = np.nan
        buy_sell_trade_quantity_ratio_mean = np.nanmean(buy_sell_trade_quantity_ratio, axis=1)
        f = - skew(buy_sell_trade_quantity_ratio_mean, nan_policy='omit')
        if np.isnan(f) or np.isinf(f):
            f = 0
            
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteVolumeShrinkReturn(FutureFactor):
    '''
    Description: 
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Other_Future_Instrument'] = {'00':['volume'], '01':['volume'], '02':['volume'], '03':['volume']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        volume_00 = data['volume_00'].values
        volume_01 = data['volume_01'].values
        volume_02 = data['volume_02'].values
        volume_03 = data['volume_03'].values
        
        volume = (volume_00 + volume_01 + volume_02 + volume_03)
        r = (close[5:] - close[:-5]) / close[:-5]
        volume_ratio = volume[-240:] / np.nansum(volume[-1440:-240].reshape(5, 240), axis=0)
        volume_ratio_change = volume_ratio[5:] - volume_ratio[:-5]
        f = np.nanmean(r[-60:][volume_ratio_change[-60:]<0])
        if np.isnan(f):
            f = 0
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteRapidChange(FutureFactor):
    '''
    Description: 
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
                    
        N = 45
        baseline = np.array([i/(N-1)*(index_close[-1]-index_close[-N])+index_close[-N] for i in range(N)])
        distance = (index_close[-N:] - baseline) / index_close[-N] * (index_close[-N] - index_close[-1]) / index_close[-N]

        f = np.max(distance) - np.min(distance)

        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLongTermDistance2Rtn(FutureFactor):
    '''
    Description: Sum(r, 240) / Sum(Abs(r), 240)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low']}
    normalize_size = 30
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        index_high = data['high_000905.SH'].values
        index_low = data['low_000905.SH'].values
        index_typical = index_close + index_high + index_low
        index_typical_r = np.diff(index_typical) / index_typical[:-1]
        
        N = 240
        f = np.sum(index_typical_r[-N:]) / np.sum(np.abs(index_typical_r[-N:]))

        return f
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHLWeightIlliqDiff(FutureFactor):
    '''
    Description: cs_mean(where(weight_rank > 0.9, illiq, nan)) - cs_mean(where(weight_rank <= 0.1, illiq, nan)), 
                where weight_rank = cs_rank(weight), illiq(abs(ret) / amount_ratio),
                ret = pct_chg(close, 30), amount_ratio = (amount,30) / ts_mean(amount, last 5 days)
    Class: Group_Stat
    Author: lixr, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['weight','close', 'amount']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        threshold = 0.9
        n = 30
        weight = data['weight'].values[-1]
        weight_rank = bn.rankdata(weight) / len(weight)
        close_price = data['close'].values
        close_price[close_price == 0] = np.nan
        amount = data['amount'].values
        amount[amount == 0] = np.nan
        
        ret = (close_price[-n:] - close_price[-(n + 1):-1]) / close_price[-(n + 1):-1]
        amount_ratio = amount[-n:] / np.nanmean(amount[-(n + 237*5):-n], axis = 0)
        illiq = np.nanmean(abs(ret) / amount_ratio, axis = 0)
        factor_value = np.nanmean(illiq[weight_rank > threshold]) - np.nanmean(illiq[weight_rank <= (1 - threshold)])
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value
##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteIndexTSSkewSharpe(FutureFactor):
    '''
    Description: cs_mean(ts_skew(pct_chg(close, 1), 65)) / cs_std(ts_skew(pct_chg(close, 1), 65))
    Class: Price_TS_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close']
    normalize_size = 30 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 65
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        rtn = close[1:] / close[:-1] - 1
        rtn_temp = rtn[-lb:]
        skew_temp = skew(rtn_temp, axis=0, nan_policy='omit')
        
        return np.nanmean(skew_temp) / np.nanstd(skew_temp)

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownDepthRatio_Refined(FutureFactor):
    '''
    Description: ts_mean(cs_mean(depth(r>0)) / cs_mean(depth(r<0)))
                 depth = (AskP0 - AskP4) / (BidP0 - BidP4)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'BidP0', 'BidP4', 'AskP0', 'AskP4']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        bid_0_price = data['BidP0'].values
        bid_4_price = data['BidP4'].values
        ask_0_price = data['AskP0'].values
        ask_4_price = data['AskP4'].values
        
        close_adj = close * adjfactor        
        r = np.diff(close_adj, axis=0) / close_adj[:-1] 

        N1 = 20
        N2 = 5
        N = N1 + N2

        ask_depth = ask_0_price[-N:] - ask_4_price[-N:]
        bid_depth = bid_0_price[-N:] - bid_4_price[-N:]
        depth = ask_depth / bid_depth
        depth[np.isinf(depth)] = np.nan

        depth_up_down_ratio_list = []
        for i in range(1, N2):
            r_mean = np.nanmean(r[-(N1+i):-i], axis=1)
            depth_mean = np.nanmean(depth[-(N1+i):-i], axis=1)
            depth_up_down_ratio = np.nanmean(depth_mean[r_mean>0]) / np.nanmean(depth_mean[r_mean<0])
            depth_up_down_ratio_list.append(depth_up_down_ratio) 
        f = np.nanmean(depth_up_down_ratio_list)
        if np.isnan(f):
            f = 1
            
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteBidAskVolAutoCorr(FutureFactor):
    '''
    Description: corr(sum(AskVol,BidVol),delay(sum(AskVol,BidVol),1),60)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol', 'AskVol']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 60
        n2 = 1
        bid_vol = data['BidVol_cont_IC'].values[-n1:]
        ask_vol = data['AskVol_cont_IC'].values[-n1:]
        bid_ask_vol_sum = bid_vol + ask_vol

        return np.corrcoef(bid_ask_vol_sum[n2:], bid_ask_vol_sum[:-n2])[0, 1]
##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteIndexNetNewBidAskDiffSkew(FutureFactor):
    '''
    Description: sum(skew(new_bid - new_ask, 240), w = index_weight), 
                where new_bid = (diff(bid) + sell) / adjfactor, new_ask = (diff(ask) + buy) / adjfactor
    Class: Bid_Ask
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'adjfactor', 'BuyTradeQuantity', 'SellTradeQuantity', 'TotalBidVol', 'TotalAskVol']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        buy = data['BuyTradeQuantity'].values
        sell = data['SellTradeQuantity'].values
        bid = data['TotalBidVol'].values
        ask = data['TotalAskVol'].values
        new_bid = (np.diff(bid[:237], axis=0) + sell[1:237]) / adjfactor[1:237]
        new_ask = (np.diff(ask[:237], axis=0) + buy[1:237]) / adjfactor[1:237]
        
        minute_past = len(buy) - 237
        if minute_past == 1:
            new_bid = np.concatenate((new_bid, [(bid[-1] + sell[-1]) / adjfactor[-1]]))
            new_ask = np.concatenate((new_ask, [(ask[-1] + buy[-1]) / adjfactor[-1]]))
        else:
            new_bid = np.concatenate((new_bid, [(bid[-minute_past] + sell[-minute_past]) / adjfactor[-minute_past]]))
            new_bid = np.concatenate((new_bid, (np.diff(bid[-minute_past:], axis=0) + sell[(-minute_past+1):]) / adjfactor[(-minute_past+1):]))
            new_ask = np.concatenate((new_ask, [(ask[-minute_past] + buy[-minute_past]) / adjfactor[-minute_past]]))
            new_ask = np.concatenate((new_ask, (np.diff(ask[-minute_past:], axis=0) + buy[(-minute_past+1):]) / adjfactor[(-minute_past+1):]))
            
        ratio = (new_bid[-lb:] - new_ask[-lb:])
        ratio_skew = skew(ratio, axis=0, nan_policy = 'omit')
        f = np.nansum(ratio_skew * weight[-1])
 
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexCorrWeightedReturn(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[-1]
        
        f = np.nanmean(np.nansum(r[-1185:], axis=0) * stk_index_corr_zz500[-1])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpRatio(FutureFactor):
    '''
    Description: ts_mean(cs_sum(pct_chg(close, 1) > 0), 20)
    Class: MTM
    Author: liuz, modified by jinpx
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor

        N = 20
        r = np.diff(close_adj[-N:], axis=0) / close_adj[-N:][:-1]
        up_num = np.sum(r>0, axis=1)
        f = np.nanmean(up_num)
            
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownRtnMean(FutureFactor):
    '''
    Description: (Index_ClosePx / min(Index_ClosePx, 60) - 1) / (60 - argmin(Index_ClosePx, 60)) 
                + (Index_ClosePx / max(Index_ClosePx, 60) - 1) / (60 - argmax(Index_ClosePx, 60))
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        
        argmin = np.nanargmin(close_temp)
        argmax = np.nanargmax(close_temp)
        f = (close_temp[-1] / np.nanmin(close_temp) - 1) / (lb - argmin) + (close_temp[-1] / np.nanmax(close_temp) - 1) / (lb - argmax)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowCorrReturnDiff(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'adjfactor']
    normalize_size = 60
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5 * 237
        stk_index_corr_zz500_mean = np.nanmean(stk_index_corr_zz500[-N:], axis=0)
        stk_index_corr_zz500_mean_rank = bn.rankdata(stk_index_corr_zz500_mean) / len(stk_index_corr_zz500_mean)
        
        r_sum = np.nansum(r[-N:], axis=0)
        
        f = np.nanmean(r_sum[stk_index_corr_zz500_mean_rank>0.8]) - np.nanmean(r_sum[stk_index_corr_zz500_mean_rank<0.2])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew




class  MinuteUpDownNumDiff(FutureFactor):
    '''
    Description: sum(where(ClosePx > OpenPx, 1, 0), 30) - sum(where(ClosePx < OpenPx, 1, 0), 30)
    Class: MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close_cont_IC'].values 
        open_ = data['open_cont_IC'].values 

        rtn = close/open_-1
        
        up_rtn_list = []
        down_rtn_list = []
        
        for r in rtn:
            if r > 0:
                down_rtn_list.append(0)
                up_rtn_list.append(r)
            else:
                down_rtn_list.append(r)
                up_rtn_list.append(0)
                
        factor = np.nansum(np.array(up_rtn_list[-30:]) > 0) - np.nansum(np.array(down_rtn_list[-30:]) < 0)
        
        return  factor
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowTurnoverRateReturnDiff(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'adjfactor']
    normalize_size = 60
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        turnover_rate = data['turnover_rate'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5 * 237
        turnover_rate_mean = np.nanmean(turnover_rate[-N:], axis=0)
        turnover_rate_mean_rank = bn.rankdata(turnover_rate_mean) / len(turnover_rate_mean)
        
        r_sum = np.nansum(r[-N:], axis=0)
        
        f = np.nanmean(r_sum[turnover_rate_mean_rank>0.8]) - np.nanmean(r_sum[turnover_rate_mean_rank<0.2])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexRtnAutoCorr(FutureFactor):
    '''
    Description: Sum(AutoCorr(r, 30) * weight)
    Class: Price_TS_Stat
    Author: hefj, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        weight = data['weight'].values
        
        close_adj = close * adjfactor   
        r = np.diff(close_adj, axis=0) / close_adj[:-1] 
        
        N = 30
        r = r[-N:]
        auto_corr = np.nanmean((r[1:] - np.nanmean(r[1:], axis=0)) * (r[:-1] - np.nanmean(r[:-1], axis=0)), axis=0) / np.nanstd(r[1:], axis=0) / np.nanstd(r[:-1], axis=0)
        f = np.nansum(auto_corr * weight[-1])
        if np.isnan(f) or np.isinf(f):
            f = 0
            
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowSpreadReturnDiff(FutureFactor):
    '''
    Description: ts_mean(cs_mean(rtn_high), 45) - ts_mean(cs_mean(rtn_low), 45),
                 rtn_high = pct_chg(close * adjfactor, 1)[:, spread > quantile(spread, 0.8)],
                 rtn_low = pct_chg(close * adjfactor, 1)[:, spread < quantile(spread, 0.2)],
                 spread = ts_mean((BidP0 - AskP0) / ((BidP0 + AskP0) / 2), from 09:30 T-1).
    Class: Group_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'AskP0', 'BidP0', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-46:]
        close[close == 0] = np.nan
        adj = data['adjfactor'].values[-46:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        ask = data['AskP0'].values
        ask[ask == 0] = np.nan
        bid = data['BidP0'].values
        bid[bid == 0] = np.nan
        spread = np.nanmean((bid - ask) / ((bid + ask) / 2), axis=0)
        high_level = np.quantile(spread[~np.isnan(spread)], 0.8)
        low_level = np.quantile(spread[~np.isnan(spread)], 0.2)
        rtn_high = np.nanmean(rtn[:, spread > high_level], axis=1)
        rtn_low = np.nanmean(rtn[:, spread < low_level], axis=1)
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIFIHReturnDiff(FutureFactor):
    '''
    Description: mean(pct_chg(close_000300.SH, 1) - pct_chg(close_000016.SH, 1), 30)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000016.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_hs = data['close_000300.SH'].values[-31:]
        close_sz = data['close_000016.SH'].values[-31:]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        r_sz = (close_sz[1:] - close_sz[:-1]) / close_sz[:-1]
        f = np.nanmean(r_hs - r_sz)
        return f

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew





class  MinuteOBVolInterest120Corr(FutureFactor):
    '''
    Description: corr(Interest, AskVol + BidVol, 120)
    Class: Bid_Ask
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC':['AskVol', 'BidVol','interest']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IC'].values 
        BidVol = data['BidVol_cont_IC'].values 
        Interest = data['interest_cont_IC'].values 

        ob_vol = AskVol+BidVol
        factor = np.corrcoef(ob_vol[-120:], Interest[-120:])[0,1]
        return  factor
    

##########
import numpy as np
from future_factor import FutureFactor

class MinuteTodayHMLoverOpen(FutureFactor):
    '''
    Description: mean((TodayHigh - TodayLow) / TodayOpen, 25)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['TodayHigh', 'TodayLow', 'TodayOpen']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        N = 25
        todayhigh = data['TodayHigh_cont_IC'].values[-N:]
        todaylow = data['TodayLow_cont_IC'].values[-N:]
        todayopen = data['TodayOpen_cont_IC'].values[-N:]
        
        f = np.nanmean((todayhigh-todaylow)/todayopen)
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteTtimesTFutureReturnCorr(FutureFactor):
    '''
    Description: mean(rtn_t, 60) * corr(rtn, rtn_t, 480),
                 rtn = pct_chg(close, 1),
                 rtn_t = pct_chg(close_T, 1).
    Class: Treasure_Future
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 3
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Other_Variety'] = {'T': ['close']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        t = data['close_T'].values[-481:]
        close = data['close_cont_IC'].values[-481:]
        rtn_t = np.diff(t) / t[:-1]
        rtn = np.diff(close) / close[:-1]
        f = np.mean(rtn_t[-60:]) * np.corrcoef(rtn_t, rtn)[0, 1]
        return f

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor



class MinuteAllIndexTurnoverShrinkReturn(FutureFactor):
    '''
    Description: "mean(where((index_turnover_ratio_IC < shift(index_turnover_ratio_IC, 1)) & (index_turnover_ratio_IF < shift(index_turnover_ratio_IF, 1)
                    & (index_turnover_ratio_IH < shift(index_turnover_ratio_IH, 1), pct_chg(Index_ClosePx, 1), nan), 45),
                    index_turnover_ratio = Index_Turnover / (the average Index_Turnover at current time over past 5 trading days)"
    Class: PV_Corr
    Author: jinpx  modeified by liuz
    '''    
    data_type='Future'
    instrument_type='recent'
    days_past=7
    data_dict=dict()
    data_dict['Index_Id'] = {'000905.SH':['close','amount'],'000300.SH':['amount'],'000016.SH':['amount']}

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        IC_close = data['close_000905.SH'].values 
        IC_amt = data['amount_000905.SH'].values 
        IF_amt = data['amount_000300.SH'].values 
        IH_amt = data['amount_000016.SH'].values       

        r_IC = np.diff(IC_close) / IC_close[:-1]
        IC_turnover_ratio = IC_amt[-240:] / np.nanmean(IC_amt[-1440:-240].reshape(5, 240), axis=0)
        IF_turnover_ratio = IF_amt[-240:] / np.nanmean(IF_amt[-1440:-240].reshape(5, 240), axis=0)
        IH_turnover_ratio = IH_amt[-240:] / np.nanmean(IH_amt[-1440:-240].reshape(5, 240), axis=0)

        N = 45
        f = np.nanmean(r_IC[-N:][np.logical_and.reduce([np.diff(IC_turnover_ratio)[-N:]<0, np.diff(IF_turnover_ratio)[-N:]<0, np.diff(IH_turnover_ratio)[-N:]<0])])
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60BidAskVolRatio(FutureFactor):
    '''
    Description: mean(BidVol, 60) / mean(AskVol, 60)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol', 'AskVol']}
    normalize_size = 60 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 60
        bid_vol = data['BidVol_cont_IC'].values[-n:]
        ask_vol = data['AskVol_cont_IC'].values[-n:]

        bid_ask_vol_ratio = np.nanmean(ask_vol[-n:]) / np.nanmean(bid_vol[-n:])

        return bid_ask_vol_ratio
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexSellMoneyPerUniqueOrderGrowth(FutureFactor):
    '''
    Description: -1 * sum(mean(sell_growth, 240) / std(sell_growth, 240), w = index_weight) when num(sell_growth == 0) < 3 for index stock,
                where sell_growth = pct_chg(sell_money_30 / sell_order_30), sell_money_30 = pct_chg(cumsum(SellTradeMoney,240),30), sell_order_30 = pct_chg(cumsum(SellUniqueOrderNum,240),30)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','SellTradeMoney', 'SellUniqueOrderNum']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        weight = data['weight'].values
        sell_money = data['SellTradeMoney'].values
        sell_order = data['SellUniqueOrderNum'].values
        
        sell_money_temp = np.nancumsum(sell_money[-lb:], axis=0)
        sell_money_30 = sell_money_temp[::-30][::-1]
        sell_money_30 = sell_money_30[1:] - sell_money_30[:-1]

        sell_order_temp = np.nancumsum(sell_order[-lb:], axis=0)
        sell_order_30 = sell_order_temp[::-30][::-1]
        sell_order_30 = sell_order_30[1:] - sell_order_30[:-1]

        sell_per_order = sell_money_30 / sell_order_30
        sell_growth = sell_per_order[1:] / sell_per_order[:-1] - 1

        sell_growth[sell_growth == 0] = np.nan
        nan_num = np.isnan(sell_growth).sum(axis=0)
        sell_growth = sell_growth[:, nan_num < 3]
        mean = np.nanmean(sell_growth, axis=0)
        std = np.nanstd(sell_growth, axis=0)
        std[std == 0] = np.nan

        f = -np.nansum(mean / std * weight[-1][nan_num < 3])
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteRe5Autocorr5_60Std120(FutureFactor):
    '''
    Description: std(corr(pct_chg(index_close, 5), delay(pct_chg(index_close, 5), 5), 60), 60)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        index_r_5 = (index_close[5:] - index_close[:-5]) / index_close[:-5]
        index_r_5_autocorr_5 = self.rolling_corr(index_r_5[5:], index_r_5[:-5], 60)
        f = np.nanstd(index_r_5_autocorr_5[-60:], ddof=1)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLocalHighLowPredictDistance(FutureFactor):
    '''
    Description: 
    Class: Local_High_Low
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def getlocallows(self, price, threshold=0.01):
        prehigh = []
        posthigh = []
        locallow = []
        preh = 0 
        posth = 0
        ll = 0
        for i in range(len(price)):
            if price[ll] <= price[preh]/(1+threshold):
                if price[ll] <= price[posth]/(1+threshold):
                    prehigh.append(preh)
                    locallow.append(ll)
                    ll = i-1
                    preh = i-1
                    posth = i-1
                    if price[i] >= price[preh]:
                        preh = i
                        ll = i
                        posth = i
                    else:
                        ll = i
                        posth = i

                else:
                    if price[i] <= price[ll]:
                        ll = i
                        posth = i
                    else:
                        posth = i
            else:
                if price[i] >= price[preh]:
                    preh = i
                    ll = i
                    posth = i
                else:
                    ll = i
                    posth = i
        return locallow

    def getlocalhighs(self,  price, threshold=0.01):

        prelow = []
        postlow = []
        localhigh = []
        prel = 0 
        postl = 0
        lh = 0
        for i in range(len(price)):
            if price[lh] >= price[prel]*(1+threshold):
                if price[lh] >= price[postl]*(1+threshold):
                    prelow.append(prel)
                    localhigh.append(lh)
                    lh = i-1
                    prel = i-1
                    postl = i-1
                    if price[i] <= price[prel]:
                        prel = i
                        lh = i
                        postl = i
                    else:
                        lh = i
                        postl = i
                else:
                    if price[i] >= price[lh]:
                        lh = i
                        postl = i
                    else:
                        postl = i
            else:
                if price[i] <= price[prel]:
                    prel = i
                    lh = i
                    postl = i
                else:
                    lh = i
                    postl = i
        return localhigh
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        
        lows = self.getlocallows(index_close, threshold=0.005)
        highs = self.getlocalhighs(index_close, threshold=0.005)
        
        if len(lows) > len(highs):
            lows = lows[1:]
        elif len(lows) < len(highs):
            highs = highs[1:]

        if len(lows) == 0 or len(highs) == 0:
            f = 0
        elif lows[0] < highs[0]:
            swing = np.nanmean(index_close[highs] / index_close[lows] - 1)
            re = index_close[-1] / index_close[highs[-1]] - 1
            f = np.abs(re - swing)
        else:
            swing = np.nanmean(index_close[lows] / index_close[highs] - 1)
            re = index_close[-1] / index_close[lows[-1]] - 1
            f = np.abs(swing - re)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import kurtosis

class MinuteResidualRtnKurt(FutureFactor):
    '''
    Description: kurt(residual_return, 60),
                residual_return = typical_price / predicted_price - 1,
                typical_price = (close_000905.SH + open_000905.SH + high_000905.SH + low_000905.SH) / 4,
                predicted_price = linear_regression(x=range(1, 61), y=typical_price[-60:], intercept=True).predict(x=range(1, 61))
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','open','high','low']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        op = data['open_000905.SH'].values
        op[op == 0] = np.nan
        high = data['high_000905.SH'].values
        high[high == 0] = np.nan
        low = data['low_000905.SH'].values
        low[low == 0] = np.nan
        
        x = np.array((np.ones(lb), np.arange(1, lb + 1)))
        y = (close[-lb:] + op[-lb:] + high[-lb:] + low[-lb:]) / 4
        b = np.linalg.inv(x.dot(x.T)).dot(x.dot(y))
        y_hat = b.dot(x)
        f = -kurtosis(y - y_hat)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverDivergence(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 30
        n2 = 120
        threshold = 0.2

        close = data['close'].values[-(n1 + 1):]
        rtn = close[-1] / close[-(n1 + 1)] - 1

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        std_1 = np.nanstd(rtn[turnover_rank < threshold])
        std_2 = np.nanstd(rtn[turnover_rank > (1 - threshold)])

        factor_value = std_1 / std_2

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteICIHDivergenceCount(FutureFactor):
    '''
    Description: sum(where((close_000905.SH > shift(close_000905.SH, 1)) & (close_000016.SH < shift(close_000016.SH, 1)), weight, 0), 20)
                - sum(where((close_000905.SH < shift(close_000905.SH, 1)) & (close_000016.SH > shift(close_000016.SH, 1)), weight, 0), 20),
                weight = range(1, 21)
    Class: Multi-Variety
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000016.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 20
        w = np.arange(1, lb + 1)
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close_1 = data['close_000016.SH'].values
        close_1[close_1 == 0] = np.nan
        
        up_down = (close[-lb:] > close[-lb - 1: -1]) & (close_1[-lb:] < close_1[-lb - 1: -1])
        down_up = (close[-lb:] < close[-lb - 1: -1]) & (close_1[-lb:] > close_1[-lb - 1: -1])
        f = w[up_down].sum() - w[down_up].sum()
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverUniqueSellRatioDiff(FutureFactor):
    '''
    Description: cs_mean(where(turnoverrank > 0.5, selluniqueratio, nan)) - cs_mean(where(turnoverrank < 0.5, selluniqueratio, nan)),
                 turnoverrank = cs_rank(ts_mean(Turnover, 60)),selluniqueratio = ts_mean(SellUniqueOrderNum / SellTradeNum, 10)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum', 'amount']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 10
        n2 = 60

        sell_unique_num = data['SellUniqueOrderNum'].values[-n1:]
        sell_trade_num = data['SellTradeNum'].values[-n1:]

        sell_unique_ratio = sell_unique_num / sell_trade_num
        sell_unique_ratio[np.isinf(sell_unique_ratio)] = np.nan

        ratio_mean = np.nanmean(sell_unique_ratio, axis=0)

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        factor_value = np.nanmean(ratio_mean[turnover_rank > 0.5]) - np.nanmean(ratio_mean[turnover_rank < 0.5])

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor

    
class  MinuteFSTurnRatioCloseCorr(FutureFactor):
    '''
    Description: "-corr(ClosePx, index_turnover_ratio_all, 60),
                index_turnover_ratio_all = (Contract0_Turnover + Contract1_Turnover + Contract2_Turnover + Contract3_Turnover) / Index_Turnover"
    Class:PV_Corr
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()

    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Index_Id'] = {'000905.SH':['amount',]}
    data_dict['Other_Future_Instrument'] = {'00':['amount'],'01':['amount'],'02':['amount'],'03':['amount']}
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_turnover = data['amount_000905.SH'].values
        future_turnover = [data['amount_00'].values[i] + data['amount_01'].values[i] + data['amount_02'].values[i] + data['amount_03'].values[i] for i in range(len(data['amount_02'].values))] 
        index_close =  data['close_cont_IC'].values
        turnover_ratio = []
        for i in range(len(index_turnover)):
            if index_turnover[i] == 0:
                turnover_ratio.append(1)
            else:
                turnover_ratio.append(future_turnover[i] / index_turnover[i])
        factor = -np.corrcoef(turnover_ratio[-60:],index_close[-60:])[0,1]

        return factor
    
##########
import numpy as np
from future_factor import FutureFactor

class MinuteApb1_60(FutureFactor):
    '''
    Description: mean(amount / volume, 60) / (sum(amount, 60) / sum(volume, 60))
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['volume', 'amount']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        volume = data['volume_cont_IC'].values
        amount = data['amount_cont_IC'].values
        vwap = amount / volume
        f = np.nanmean(vwap[-60:]) / (np.nansum(amount[-60:]) / np.nansum(volume[-60:]))
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor

    

class  MinuteContraVarietyDiffConflictMean(FutureFactor):
    '''
    Description: "mean(where(((Index_ClosePx / Index_OpenPx - 1 > 0) & (Index_Other2_ClosePx / Index_Other2_OpenPx - 1 < 0)) |
            ((Index_ClosePx / Index_OpenPx - 1 < 0) & (Index_Other2_ClosePx / Index_Other2_OpenPx - 1> 0)), Index_ClosePx / Index_OpenPx - Index_Other2_ClosePx / Index_Other2_OpenPx, nan), 20)"
    Class:Multi-Variety
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close','open'],'000016.SH':['close','open']}
    
    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close =  data['close_000905.SH'].values 
        index_other_close =  data['close_000016.SH'].values 
        index_open =  data['open_000905.SH'].values 
        index_other_open =  data['open_000016.SH'].values 

        index_rtn_list =index_close/index_open-1
        other_rtn_list = index_other_close/index_other_open-1

        conflict_rtn_list = []

        for i in range(20):
            idx = i-20
            if (index_rtn_list[idx] > 0 and other_rtn_list[idx] < 0) or (index_rtn_list[idx] < 0 and other_rtn_list[idx] > 0):
                conflict_rtn_list.append(index_rtn_list[idx] - other_rtn_list[idx])

        if len(conflict_rtn_list) == 0:
            factor = 0
        else:
            factor =np.nanmean(conflict_rtn_list)

        return factor
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioCloseCorrSharpe(FutureFactor):
    '''
    Description: weighted_cs_mean(ts_corr(close, ((BuyTradeQuantitiy - SellTradeQuantity) / (BuyTradeQuantity + SellTradeQuantity)), 50), w=index_weight)
                / weighted_cs_std(ts_corr(close, ((BuyTradeQuantity - SellTradeQuantity) / (BuyTradeQuantity + SellTradeQuantity)), 50), w=index_weight)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','SellTradeQuantity', 'BuyTradeQuantity', 'close', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        def corr_coef(x, y):
            mask = np.isnan(x) | np.isnan(y) | np.isinf(x) | np.isinf(y)
            x = np.where(mask, np.nan, x)
            y = np.where(mask, np.nan, y)
            return np.nanmean((x - np.nanmean(x, axis=0)) * (y - np.nanmean(y, axis=0)), axis=0) / (np.nanstd(x, axis=0) * np.nanstd(y, axis=0))

        lb = 50
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeQuantity'].values
        sell = data['SellTradeQuantity'].values
        
        ratio = (buy[-lb:] - sell[-lb:]) / (buy[-lb:] + sell[-lb:])
        close = close[-lb:]
        corr = corr_coef(close, ratio)
        corr[np.isinf(corr)] = np.nan
        mean = np.nansum(corr * weight[-1])
        std = np.nansum(((corr - mean) ** 2) * weight[-1]) ** 0.5
        
        return -mean / std
##########
from future_factor import FutureFactor
import numpy as np


class MinuteLocalExtremaVolumeRatio(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['close', 'volume']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def get_local_extrema(self, price):
        threshold = 2 * np.nanstd(price[1:] / price[:-1] - 1)
        localhighs = []
        locallows = []
        prel = 0
        preh = 0
        lh = 0
        ll = 0
        for i in range(len(price)):
            if price[lh] >= price[prel] * (1 + threshold) and price[lh] >= price[i] * (1 + threshold):
                localhighs.append(lh)
                lh = i
                prel = i
            else:
                if price[i] < price[lh] / (1 + threshold) or price[i] > price[lh]:
                    lh = i
                if price[i] <= price[prel]:
                    prel = i
            if price[ll] <= price[preh] / (1 + threshold) and price[ll] <= price[i] / (1 + threshold):
                locallows.append(ll)
                ll = i
                preh = i
            else:
                if price[i] > price[ll] * (1 + threshold) or price[i] < price[ll]:
                    ll = i
                if price[i] >= price[preh]:
                    preh = i
        if price[lh] >= price[prel] * (1 + threshold):
            localhighs.append(lh)
        if price[ll] <= price[preh] / (1 + threshold):
            locallows.append(ll)
        return localhighs, locallows
        
    def calculate(self, data):
        lb = 60
        close = data['close_cont_IC'].values[-lb:]
        volume = data['volume_cont_IC'].values[-lb:]
        lh, ll = self.get_local_extrema(close)
        if (len(ll) >= 1) & (len(lh) >= 1):
            vol_ll = np.nanmean(volume[ll])
            vol_lh = np.nanmean(volume[lh])
            f = (vol_ll - vol_lh) / (vol_ll + vol_lh)
        else:
            f = 0
        if np.isnan(f) or np.isinf(f):
            f = 0
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownTotalValueTradeRatio(FutureFactor):
    '''
    Description: ts_mean(cs_mean(totalvaluetrade(r>0)) / cs_mean(totalvaluetrade(r<0)))
    Class: PV_Corr
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'TotalValueTrade']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        totalvaluetrade = data['TotalValueTrade'].values
        
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5
        totalvaluetrade_ratio = np.array([])
        for i in range(N):
            totalvaluetrade_ratio = np.append(totalvaluetrade_ratio, np.nanmean(totalvaluetrade[-i][r[-i]>0])/np.nanmean(totalvaluetrade[-i][r[-i]<0]))

        f = np.nanmean(totalvaluetrade_ratio)
            
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexTSCSStdRatio(FutureFactor):
    '''
    Description: ts_std(weighted_cs_mean(pct_chg(close, 1), w=index_weight), 60)
                / weighted_cs_std(ts_mean(pct_chg(close, 1), 60))
    Class: Price_TS_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','adjfactor', 'close']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        rtn_temp = close[-lb:] / close[-lb - 1: -1] - 1
        idx_rtn = np.nansum(rtn_temp * weight[-lb:], axis=1)
        ts_std = np.nanstd(idx_rtn)
        stk_rtn = np.nanmean(rtn_temp, axis=0)
        cs_mean = np.nansum(stk_rtn * weight[-1])
        cs_std = np.nansum(((stk_rtn - cs_mean) ** 2) * weight[-1]) ** 0.5
        
        return ts_std / cs_std
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteFutureBasisTurnoverRatio(FutureFactor):
    '''
    Description: mean(Index_Turnover, from last_trading day) / mean(Turnover, from last trading day)
    Class: Future_Spot_Amount
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['amount']}
    data_dict['Index_Id'] = {'000905.SH': ['amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        index_amount = data['amount_000905.SH'].values
        amount = data['amount_cont_IC'].values

        index_amount[index_amount == 0] = np.nan
        amount[amount == 0] = np.nan

        mean_ratio = np.nanmean(index_amount) / np.nanmean(amount)

        factor_value = 0 if (np.isnan(mean_ratio) or np.isinf(mean_ratio)) else mean_ratio

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexCSSkewSharpe(FutureFactor):
    '''
    Description: weighted_ts_mean(weighted_cs_skew(pct_chg(close, 1), w=index_weight), 30, w=range(1, 31))
                / weighted_ts_std(weighted_cs_skew(pct_chg(close, 1), w=index_weight), 30, w=range(1, 31))
    Class: Price_CS_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        w = np.arange(1, lb + 1)
        w = w / w.sum()
        
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        rtn_temp = close[-lb:] / close[-lb - 1: -1] - 1
        mean = np.nansum(rtn_temp * weight[-lb:], axis=1).reshape((len(rtn_temp), -1))
        std = np.nansum(((rtn_temp - mean) ** 2) * weight[-lb:], axis=1) ** 0.5
        skew = np.nansum(((rtn_temp - mean) ** 3) * weight[-lb:], axis=1) / (std ** 3)
        mean = np.sum(skew * w)
        std = np.sum(((skew - mean) ** 2) * w) ** 0.5
        
        return mean / std
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexAskBidVolRatioStd(FutureFactor):
    '''
    Description: ts_mean(cs_std(TotalBidVol / TotalAskVol), 10)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        totalbidvol = data['TotalBidVol'].values
        totalaskvol = data['TotalAskVol'].values

        N = 10
        total_bid_ask_vol_ratio = totalbidvol[-N:] / totalaskvol[-N:]
        total_bid_ask_vol_ratio[np.isinf(total_bid_ask_vol_ratio)] = np.nan
        f = np.nanmean(np.nanstd(total_bid_ask_vol_ratio, axis=1))
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskVolDiff(FutureFactor):
    '''
    Description: cs_mean(ts_mean(pct_chg(TotalAskVol / adjfactor, 1), 20))
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalAskVol', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['TotalAskVol'].values[-21:]
        ask[ask == 0] = np.nan
        adj = data['adjfactor'].values[-21:]
        adj[adj == 0] = np.nan
        ask = ask / adj
        ask_g = np.nanmean(np.diff(ask, n=1, axis=0) / ask[:-1], axis=0)
        f = -np.nanmean(ask_g)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioAutoCorrSharpe(FutureFactor):
    '''
    Description: mean(autocorr(bs_ratio)) / std(autocorr(bs_ratio)),
                 where bs_ratio = ((BuyTradeMoney - SellTradeMoney) / (BuyTradeMoney + SellTradeMoney),30)     
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyTradeMoney', 'SellTradeMoney']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        weight = data['weight'].values
        buy_money = data['BuyTradeMoney'].values
        sell_money = data['SellTradeMoney'].values
        
        bs_ratio = (buy_money[-lb:] - sell_money[-lb:]) / (buy_money[-lb:] + sell_money[-lb:])
        auto_corr = np.nanmean((bs_ratio[:-1] - np.nanmean(bs_ratio, axis=0)) * (bs_ratio[1:] - np.nanmean(bs_ratio, axis=0)), axis=0) / np.nanvar(bs_ratio, axis=0)
        mean = np.nansum(auto_corr * weight[-1])
        std = np.nansum(((auto_corr - mean) ** 2) * weight[-1]) ** 0.5
        f = mean / std
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLocalLowHighNumDiff(FutureFactor):
    '''
    Description: count(local_low) - count(local_high)
    Class: Local_High_Low
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].values
        
        N = 237   
        w = np.arange(1, N - 1)
        w = w / np.nansum(w)
        
        index_r = np.diff(index_close[-N:]) / index_close[-N:][:-1]
        index_r_std = np.nanstd(index_r)
        local_low = np.nansum(w[(index_r[:-1] < -index_r_std) & (index_r[1:] > index_r_std)])
        local_high = np.nansum(w[(index_r[:-1] > index_r_std) & (index_r[1:] < -index_r_std)])
        
        f = local_low - local_high       
        if np.isnan(f) or np.isinf(f):
            f = 0
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew


class  MinuteIndexUDRtnMeanDiff(FutureFactor):
    '''
    Description: 
    Class: Price_CS_Stat
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['close', 'open']

    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close'].values
        open_ = data['open'].values

        rtn = close/open_-1
        rtn[np.isinf(rtn)] = np.nan
        up_rtn = np.nanmean(np.where(rtn>0,rtn, np.nan),axis=1)

        down_rtn = np.nanmean(np.where(rtn<0,rtn, np.nan),axis=1)
        factor= np.nanmean(up_rtn[-20:])+ np.nanmean(down_rtn[-20:])
            
        return factor





##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew


class  MinuteIndexAskBidCorr(FutureFactor):
    '''
    Description: cs_mean(corr(AskP4 * Adjfactor, BidP4 * Adjfactor, 30))
    Class: Bid_Ask
    Author:shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['BidP4', 'AskP4', 'adjfactor']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskP4 = data['AskP4'].values 
        BidP4 = data['BidP4'].values 
        adjfactor = data['adjfactor'].values 

        askadj = adjfactor*AskP4
        bidadj = adjfactor*BidP4
        
        factor = np.nanmean(self.array_coef(askadj[-30:], bidadj[-30:]))

        return  factor
    
    def array_coef(self, x, y):

        
        x[np.isinf(x)] = np.nan
        y[np.isinf(y)] = np.nan
        nan_index = np.isnan(x) | np.isnan(y)
        x[nan_index] = np.nan
        y[nan_index] = np.nan
        delta_x = x - np.nanmean(x, axis=0)
        delta_y = y - np.nanmean(y, axis=0)
        multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
        multi[np.isinf(multi)] = np.nan
        return multi

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexTradeMoneyRatioDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'AskP0', 'AskV0', 'BidP0', 'BidV0']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        buy_trade_money = data['BuyTradeMoney'].values
        sell_trade_money = data['SellTradeMoney'].values
        ask_amt = data['AskP0'].values * data['AskV0'].values
        bid_amt = data['BidP0'].values * data['BidV0'].values

        total_buy_money = np.nansum(buy_trade_money, axis=1)
        total_sell_money = np.nansum(sell_trade_money, axis=1)
        total_bid_amt = np.nansum(bid_amt, axis=1)
        total_ask_amt = np.nansum(ask_amt, axis=1)

        buy_sell_ratio = total_buy_money / total_ask_amt - total_sell_money / total_bid_amt
        buy_sell_ratio[np.isinf(buy_sell_ratio)] = np.nan

        factor_value = np.nanmean(buy_sell_ratio[-n:])

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexObLv1AmtPerOrderRatioSharpe(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Bid1AmtMean','Ask1AmtMean','Buy1NumOrdersMean','Sell1NumOrdersMean']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        bid_amt = data['Bid1AmtMean'].values
        ask_amt = data['Ask1AmtMean'].values

        bid_order_num = data['Buy1NumOrdersMean'].values
        ask_order_num = data['Sell1NumOrdersMean'].values

        bid_amt_per_order = bid_amt / bid_order_num
        ask_amt_per_order = ask_amt / ask_order_num

        order_amt_ratio = (bid_amt_per_order - ask_amt_per_order) / (bid_amt_per_order + ask_amt_per_order)

        factor_value = np.nanmean(np.nanmean(order_amt_ratio[-n:],axis=1)) / np.nanstd(np.nanmean(order_amt_ratio[-n:],axis=1))

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteSpotFutureCloseCorr(FutureFactor):
    '''
    Description: corr(close, close_000905.SH, 30)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_cont_IC'].values
        close[close == 0] = np.nan
        index_close = data['close_000905.SH'].values
        index_close[index_close == 0] = np.nan   
        mask = np.isnan(index_close[-lb:]) | np.isnan(close[-lb:])
        
        return np.corrcoef(index_close[-lb:][~mask], close[-lb:][~mask])[0,1]
##########
from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexTurnoverStd(FutureFactor):
    '''
    Description: std(amount_000905.SH, 20)
    Class: Liquidity
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['amount']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount_000905.SH'].values[-20:]
        f = np.std(amount)
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBidAskTotVolMA20DiffRatio(FutureFactor):
    '''
    Description: ts_mean((cs_sum(TotalBidVol) - cs_sum(TotalAskVol)) / (cs_sum(TotalBidVol) + cs_sum(TotalAskVol)), 20)
    Class: Bid_Ask
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 20

        total_bid = np.nansum(data['TotalBidVol'].values[-n:] / data['adjfactor'].values[-n:], axis=1)
        total_ask = np.nansum(data['TotalAskVol'].values[-n:] / data['adjfactor'].values[-n:], axis=1)

        bid_mean = np.nanmean(total_bid)
        ask_mean = np.nanmean(total_ask)

        if (bid_mean + ask_mean) == 0:
            factor_value = 0
        else:
            factor_value = (bid_mean - ask_mean) / (bid_mean + ask_mean)

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteICIFConvexityDiff_Refined(FutureFactor):
    '''
    Description: mean(pct_chg(pct_chg(close_000905.SH, 1), 1) - pct_chg(pct_chg(close_000300.SH, 1), 1), 90)
    Class: Multi-Variety
    Author: jinpx, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000300.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        IC_close = data['close_000905.SH'].values
        IF_close = data['close_000300.SH'].values

        N = 30
        IC_r = IC_close[N:] / IC_close[:-N] - 1
        IF_r = IF_close[N:] / IF_close[:-N] - 1
        
        IC_convexity = np.diff(IC_r)
        IF_convexity = np.diff(IF_r)
        
        N = 120
        convexity_diff = IC_convexity[-N:] - IF_convexity[-N:]
        f = np.nanmean(convexity_diff)        
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteContract23PriceDiffVolatility(FutureFactor):
    '''
    Description: -std(close_02 / close_03 - 1, 30)
    Class: All_Contract
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Other_Future_Instrument'] = {'02': ['close'], '03': ['close']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_02 = data['close_02'].values[-30:]
        close_03 = data['close_03'].values[-30:]
        f = -np.nanstd((close_02 - close_03) / close_03)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteRe5Autocorr5_120Mean120(FutureFactor):
    '''
    Description: mean(corr(pct_chg(ClosePx, 5), delay(pct_chg(ClosePx, 5), 5), 120), 120)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        r_5 = (close[5:] - close[:-5]) / close[:-5]
        r_5_autocorr_5 = self.rolling_corr(r_5[5:], r_5[:-5], 120)
        f = np.nanmean(r_5_autocorr_5[-120:])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew

class  MinuteNetAmtRatio(FutureFactor):
    '''
    Description: "(sum(where(pct_chg(ClosePx, 1) > rtn_mean + 2 * rtn_std, Turnover, 0), 120) - sum(where(pct_chg(ClosePx, 1) < rnt_mean - 2 * rtn_std, Turnover, 0), 120)) /
(sum(where(pct_chg(ClosePx, 1) > rtn_mean + 2 * rtn_std, Turnover, 0), 120) + sum(where(pct_chg(ClosePx, 1) < rnt_mean - 2 * rtn_std, Turnover, 0), 120)),
rtn_mean = mean(pct_chg(ClosePx, 1), 5days), rtn_std = std(pct_chg(ClosePx, 1), 5days) / (10 ** 0.5)"
    Class:MTM
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=5
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['close' ,'amount']}
    
    normalize_size=5*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close_lastdays = data['close_cont_IC'].values[:240*5]
        amount_lastdays = data['amount_cont_IC'].values[:240*5]
        
        rtn_list_lastdays = close_lastdays[1:]/close_lastdays[:-1]-1
        rtn_mean = np.nanmean(rtn_list_lastdays)
        rtn_std = np.nanstd(rtn_list_lastdays)/np.sqrt(10)
        
        close = data['close_cont_IC'].values
        amount = data['amount_cont_IC'].values
        rtn_list= close[1:]/close[:-1]-1
        
        turnover_up_array = amount[-120:][rtn_list[-120:] > rtn_mean+2*rtn_std]
        turnover_down_array =amount[-120:][rtn_list[-120:] < rtn_mean-2*rtn_std]
       
        if len(turnover_up_array) <= 0:
            turnover_up_sum = 0
        else:
            turnover_up_sum = np.nansum(turnover_up_array)

        if len(turnover_down_array) <= 0:
            turnover_down_sum = 0
        else:
            turnover_down_sum = np.nansum(turnover_down_array)

        if turnover_down_sum == 0 and turnover_up_sum == 0:
            factor = 0
        else:
            factor = (turnover_up_sum - turnover_down_sum) / (turnover_up_sum + turnover_down_sum)

        return  factor
    
    
##########
import numpy as np
from future_factor import FutureFactor

class MinuteMtmSustainability(FutureFactor):
    '''
    Description: auto_corr(pct_chg(close, 1), 30) * (sum(where(close > delay(close, 1), 1, 0), 30) - 15)
    Class: MTM
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        index_r = np.diff(index_close) / index_close[:-1]
        index_r_autocorr = np.corrcoef(index_r[-30:], index_r[-31:-1])[0, 1]
        counter = np.sum(index_r[-30:]>0) - 15
        f = index_r_autocorr * counter
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownVolRate(FutureFactor):
    '''
    Description: sum(where(index_close >= delay(index_close, 1), index_volume, 0), 60) / sum(index_volume, 60)
    Class: MTM
    Author: liuz, modified by jinpx
    '''   
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close = data['close_000905.SH'].values[-60:]
        index_volume = data['volume_000905.SH'].values[-60:]
        
        index_r = np.append(np.nan, np.diff(index_close) / index_close[:-1])
        f = np.nansum(index_volume[index_r>=0]) / np.nansum(index_volume)        
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteCalmarRatio120min(FutureFactor):
    '''
    Description: calmar(index_close, 120)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        
        N = 120
        index_r = np.diff(index_close[-N:]) / index_close[-N:][:-1]
        index_r_cumsum = np.cumsum(index_r) + 1
        
        max_r = 0
        max_drawdown = 0.0000001
        
        for i in range(N-1):
            if index_r_cumsum[i] > max_r:
                max_r = index_r_cumsum[i]
            if index_r_cumsum[i] / max_r - 1 < max_drawdown:
                max_drawdown = index_r_cumsum[i] / max_r - 1 
        f = - index_r.mean() / max_drawdown
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_Sum60Skew30MA60IndexTurnover(FutureFactor):
    '''
    Description: Sum_60(Skew_30(MA_60(Index_Turnover)))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['amount']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        turnover_ma_60 = bn.move_mean(data['amount_000905.SH'].values, 60)
        turnover_ma_60[np.isnan(turnover_ma_60)] = 0

        rolling_mean = bn.move_mean(turnover_ma_60, 30)
        # Skew_Bias = True, which equals scipy.stats.skew(a) or standard skew formula
        skew_30 = (pd.Series(turnover_ma_60).rolling(30).skew() * (30 - 2) / np.sqrt((30 - 1) * 30)).fillna(0).values

        factor_value = np.nansum(skew_30[-60:])

        if np.isnan(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class MinuteIndexHLTurnoverRateUniqueSellRatioDiff(FutureFactor):
    '''
    Description: mean(ratio(rank > 0.8)) - mean(ratio(rank < 0.2)),
                 ratio = -1 * mean(SellTradeNum / SellUniqueOrderNum, 30)
                 rank = rank(mean(turnover_rate, 237))
    Class: Group_Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum','SellTradeNum','turnover_rate']
    normalize_size = 180
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n1 = 30
        n2 = 237
        threshold = 0.8
        
        sell_unique = data['SellUniqueOrderNum'].values
        sell_unique[sell_unique == 0] = np.nan
        sell = data['SellTradeNum'].values
        sell[sell == 0] = np.nan
        turnover = data['turnover_rate'].values
        
        ratio = -1 * np.nanmean(sell[-n1:] / sell_unique[-n1:], axis = 0)
        mask = np.isnan(ratio)
        ratio = ratio[~mask]
        turnover_mean = np.nanmean(turnover[-n2:], axis = 0)[~mask]
        rank = bk.rankdata(turnover_mean) / len(turnover_mean)
        factor_value = np.nanmean(ratio[rank > threshold]) - np.nanmean(ratio[rank <= (1 - threshold)])
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteVWAPTWAPRatioSharpe(FutureFactor):
    '''
    Description: mean(((amount / volume / 200) - twap) / ((amount / volume / 200) + twap), 120)
    Class: Return_Risk
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['amount', 'volume', 'twap']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        amount = data['amount_cont_IC'].values
        volume = data['volume_cont_IC'].values
        twap = data['twap_cont_IC'].values
        
        vwap = amount / volume
        vwap_twap_ratio = (vwap - twap) / (vwap + twap)

        N = 120
        f = np.nanmean(vwap_twap_ratio[-N:]) / np.nanstd(vwap_twap_ratio[-N:])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor


class MinuteBidAskVolPressure30Ema(FutureFactor):
    '''
    Description: -ema(SUM(BidVol, 30) / SUM(AskVol, 30), 5)
    Class:Bid_Ask
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['AskVol', 'BidVol']}
    
    normalize_size=5*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        ask_vol = data['AskVol_cont_IC'].values 
        bid_vol = data['BidVol_cont_IC'].values 

        pressure_ema_list = []
        for i in range(59, -1, -1):
            ask_vol_sum = np.nansum(ask_vol[-30-i:][:30])
            bid_vol_sum = np.nansum(bid_vol[-30-i:][:30])
            if ask_vol_sum == 0:
                pressure = 0
            else:
                pressure = bid_vol_sum / ask_vol_sum
            pressure_ema = self.calc_ema(pressure_ema_list,pressure,5)
            pressure_ema_list.append(pressure_ema)

        factor = -pressure_ema_list[-1]

        return factor
    
    def calc_ema(self, cur_ema_list,x_n,span=None):
        cur_ema_length = len(cur_ema_list)

        if span == None:
            span = cur_ema_length + 1
        else:
            span = min(cur_ema_length+1,span)
            assert span > 0, "Invalid input of arg span!"

        alpha = 2 / (span+1)

        if cur_ema_length == 0:
            return x_n
        else:
            return (alpha * x_n + (1-alpha) * cur_ema_list[-1])

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor


    
class MinuteCloseminusOpenStd(FutureFactor):
    '''
    Description: (std(ClosePx - OpenPx, 30) - mean(std(ClosePx - OpenPx, 30), 240)) / std(std(ClosePx - OpenPx, 30), 240)
    Class: Price_Stat
    Author:  jinpx modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=5
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']}
    
    normalize_size=10*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close_cont_IC'].values 
        open_ = data['open_cont_IC'].values 

        N1 = 30
        N2 = 720
        rolling_std = []
        for i in range(720,-1, -1):

            rolling_std.append(np.nanstd((close-open_)[-N1-i:][:N1]))
        factor = (rolling_std[-1] - np.mean(rolling_std[-(N2+1):-1])) / np.std(rolling_std[-(N2+1):-1])

    
        return factor
    
    
##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownAutoCorrDiff(FutureFactor):
    '''
    Description: corr(where(delay(close_000905.SH, 1) > delay(close_000905.SH, 2), delay(pct_chg(close_000905.SH, 1), 1), nan),
                where(delay(close_000905.SH, 1) > delay(close_000905.SH, 2), pct_chg(close, 1), nan), 35)
                - corr(where(delay(close_000905.SH, 1) < delay(close_000905.SH, 2), delay(pct_chg(close_000905.SH, 1), 1), nan),
                where(delay(close_000905.SH, 1) < delay(close_000905.SH, 2), pct_chg(close, 1), nan), 35)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 35
        close = data['close_cont_IC'].values
        close[close == 0] = np.nan
        idx_close = data['close_000905.SH'].values
        idx_close[idx_close == 0] = np.nan   

        rtn = close[-lb - 1:] / close[-lb - 2: -1] - 1
        rtn[np.isnan(rtn)] = 0
        idx_rtn = idx_close[-lb - 1:] / idx_close[-lb - 2: -1] - 1
        idx_rtn[np.isnan(idx_rtn)] = 0
        up = idx_rtn[:-1] > 0
        down = idx_rtn[:-1] < 0
        corr_up = np.corrcoef(idx_rtn[:-1][up], rtn[1:][up])[0,1]
        corr_down = np.corrcoef(idx_rtn[:-1][down], rtn[1:][down])[0,1]
        f = corr_up - corr_down
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor

class MinuteADL(FutureFactor):
    '''
    Description: mean((ClosePx - OpenPx) / (HighPx - LowPx), 120)
    Class: MTM
    Author:jinpx,  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'low', 'open', 'high']}

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb=120
        factor =(data['close_cont_IC'].values[-lb:]-data['open_cont_IC'].values[-lb:])/(data['high_cont_IC'].values[-lb:]-data['low_cont_IC'].values[-lb:])
            
        return np.nanmean(factor)

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute90RetAutoCorr(FutureFactor):
    '''
    Description: corr(pct_chg(Index_ClosePx,1), delay(pct_chg(Index_ClosePx,1),1),90)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 40 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 1
        n2 = 90
        index_close = data['close_000905.SH'].values[-(n2 + 1):]

        rtn = index_close[1:] / index_close[:-1] - 1

        return np.corrcoef(rtn[n1:], rtn[:-n1])[0, 1]
##########
import numpy as np
from future_factor import FutureFactor

class MinutePVCorr15Bias120(FutureFactor):
    '''
    Description: -z_score(corr(volume, close, 15), 120)
    Class: PV_corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'volume']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        volume = data['volume_cont_IC'].values
        
        pv_corr = self.rolling_corr(close, volume, 15)
        
        f = - (pv_corr[-1] - np.nanmean(pv_corr[-120:])) / np.nanstd(pv_corr[-120:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexNetBuyRtnDiff(FutureFactor):
    '''
    Description: (mean(ret[net_buy < 0]) - mean(ret[net_buy > 0])) / std(ret),
                 where ret = close[-1] / close[-30] - 1, net_buy = sum(BuyTradeMoney[-30:]) - sum(SellTradeMoney[-30:])          
    Class: Group_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close', 'BuyTradeMoney', 'SellTradeMoney']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeMoney'].values
        sell = data['SellTradeMoney'].values
        
        close_temp = close[-lb:]
        rtn_temp = close_temp[-1] / close_temp[0] - 1
        net_buy_temp = np.nansum(buy[-lb:], axis=0) - np.nansum(sell[-lb:], axis=0)
        f = (np.nanmean(rtn_temp[net_buy_temp < 0]) - np.nanmean(rtn_temp[net_buy_temp > 0])) / np.nanstd(rtn_temp)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from future_factor import FutureFactor
import numpy as np
from scipy.stats import pearsonr


class MinuteIndexHighLowRtnStdRatio(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        adj = data['adjfactor'].values[-lb:]
        close = data['close'].values[-lb:] * adj / adj[-1]
        rtn = close[-1] / close[0] - 1
        median = np.nanmedian(rtn)
        up_std = rtn[rtn > median].std()
        down_std = rtn[rtn < median].std()
        f = (up_std - down_std) / (up_std + down_std)
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute20HighVolCorr(FutureFactor):
    '''
    Description: -corr(volume, high, 20)
    Class: PV_Corr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high', 'volume']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        high = data['high_cont_IC'].values[-20:]
        volume = data['volume_cont_IC'].values[-20:]

        return -np.corrcoef(high, volume)[0, 1]
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownLimitNumDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['TotalAskVol'].values[-1]
        bid = data['TotalBidVol'].values[-1]
        up_limit_num = ((bid > 0) & (ask == 0)).sum()
        down_limit_num = ((bid == 0) & (ask > 0)).sum()
        f = up_limit_num - down_limit_num
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteVolumeSpreadRatio(FutureFactor):
    '''
    Description: mean(volume_ratio / ((AskP0 - BidP0) / (AskP0 + BidP0)), 30)
                 volume_ratio = volume / (the average volume at current time over past 5 trading days)
    Class: Liquidity
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['volume', 'AskP0', 'BidP0']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        volume = data['volume_cont_IC'].values
        ask_0 = data['AskP0_cont_IC'].values
        bid_0 = data['BidP0_cont_IC'].values
        
        spread = (ask_0 - bid_0) / (ask_0 + bid_0)
        volume_ratio = volume[-240:] / np.nanmean(volume[-1440:-240].reshape(5, 240), axis=0)
            
        N = 30
        liquidity = volume_ratio[-N:] / spread[-N:] 
        liquidity[np.isinf(liquidity)] = np.nan

        f = np.nanmean(liquidity)
        
        return f
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowAbsPxPathReturnDiff(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'AbsPxPath']
    normalize_size = 90
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        AbsPxPath = data['AbsPxPath'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5 * 237
        AbsPxPath_mean = np.nanmean(AbsPxPath[-N:], axis=0)
        AbsPxPath_mean_rank = bn.rankdata(AbsPxPath_mean) / len(AbsPxPath_mean)

        r_sum = np.nansum(r[-N:], axis=0)
        
        f = np.nanmean(r_sum[AbsPxPath_mean_rank>0.8]) - np.nanmean(r_sum[AbsPxPath_mean_rank<0.2])
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndex20WeightedReturnSkew(FutureFactor):
    '''
    Description: weighted_cs_skew(pct_chg(ClosePx,1),w=index_weight)
    Class: Price_CS_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        weight = data['weight'].values

        close_adj = close * adjfactor
        close_adj[close_adj == 0] = np.nan

        rtn = close_adj[-1] / close_adj[-21] - 1
        weighted_mean = np.nansum(rtn * weight[-1])
        weighted_std = np.nansum(weight[-1] * (rtn - weighted_mean) ** 2) ** 0.5

        return np.nansum(weight[-1] * (rtn - weighted_mean) ** 3) / (weighted_std ** 3)
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexHighBetaRtn(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=2
    data_dict=dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values

        close_adj = close*adjfactor
        rtn = close_adj[1:]/close_adj[:-1]-1

        index_rtn = index_close[1:] / index_close[:-1] - 1

        rtn[np.isinf(rtn)] = np.nan
        index_rtn[np.isinf(index_rtn)] = np.nan

        adj_rtn_237 = rtn[-237:]
        index_rtn_237 = index_rtn[-237:]
        adj_rtn_30 = rtn[-30:] 
        cov_matrix = np.cov(adj_rtn_237.T,index_rtn_237.reshape(237,-1).T)
        cov_rtn = cov_matrix[-1][:-1]
        index_rtn_std = np.nanstd(index_rtn_237)

        beta = cov_rtn / np.power(index_rtn_std,2)
        factor = np.nanmean(np.nanmean(adj_rtn_30[:,beta > 3],axis=0))

        if np.isnan(factor):
            factor = 0
            
            
        return factor


##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteVolSpreadInterestCorr(FutureFactor):
    '''
    Description: 
    Class:Liquidity
    Author: lixr modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC':['AskVol', 'BidVol','interest']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IC'].values 
        BidVol = data['BidVol_cont_IC'].values 
        Interest = data['interest_cont_IC'].values 

        vol_spread = BidVol-AskVol
        factor = -np.corrcoef(vol_spread[-120:], Interest[-120:])[0,1]
        return  factor
    
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew





class  MinuteSignedRangeMean(FutureFactor):
    '''
    Description: mean(where(ClosePx > OpenPx, HighPx / LowPx, -HighPx / LowPx), 120)
    Class:MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC':['high', 'low','open', 'close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        open_ = data['open_cont_IC'].values 
        close = data['close_cont_IC'].values 
        high = data['high_cont_IC'].values 
        low = data['low_cont_IC'].values 
        
        range_ =high/low
        sign = np.sign(close-open_)
        
        signed_range = (sign*range_)
        factor = np.nanmean(signed_range[-120:])
        return  factor
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighLowTurnoverRatioAbs(FutureFactor):
    '''
    Description: abs(cs_mean((ts_mean(where(close > ts_quantile(close, 0.9), amount, nan), 60) 
                - ts_mean(where(close < ts_quantile(close, 0.1), amount, nan),60)) 
                / (ts_mean(where(close > ts_quantile(close, 0.9), amount, nan), 60) 
                + ts_mean(where(close < ts_quantile(close, 0.1), amount, nan), 60))))
    Class: PV_Corr
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','close', 'amount', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        amount = data['amount'].values
        close = close[-lb:]
        amount = amount[-lb:]
        
        high_threshold = np.nanpercentile(close, 90, axis=0)
        low_threshold = np.nanpercentile(close, 10, axis=0)
        amount_0 = np.nanmean(np.where(close > high_threshold, amount, np.nan), axis=0)
        amount_1 = np.nanmean(np.where(close < low_threshold, amount, np.nan), axis=0)
        f = np.abs(np.nanmean((amount_0 - amount_1) / (amount_0 + amount_1) * weight[-1]))
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverUniqueBuyRatioDiff(FutureFactor):
    '''
    Description: cs_mean(where(turnoverrank > 0.5, buyuniqueratio, nan)) - cs_mean(where(turnoverrank < 0.5, buyuniqueratio, nan)),
                 turnoverrank = cs_rank(ts_mean(Turnover, 120)),buyuniqueratio = -ts_mean(BuyUniqueOrderNum / BuyTradeNum, 10)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'amount']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 10
        n2 = 120

        buy_unique_num = data['BuyUniqueOrderNum'].values[-n1:]
        buy_trade_num = data['BuyTradeNum'].values[-n1:]

        buy_unique_ratio = -buy_unique_num / buy_trade_num
        buy_unique_ratio[np.isinf(buy_unique_ratio)] = np.nan

        ratio_mean = np.nanmean(buy_unique_ratio, axis=0)

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        factor_value = np.nanmean(ratio_mean[turnover_rank > 0.5]) - np.nanmean(ratio_mean[turnover_rank < 0.5])

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute25HighOverOpen(FutureFactor):
    '''
    Description: -mean(Index_HighPx, 25) / mean(Index_OpenPx, 25)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['high', 'open']}
    normalize_size = 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 25
        index_high = data['high_000905.SH'].values[-n:]
        index_open = data['open_000905.SH'].values[-n:]

        return np.nanmean(index_high) / np.nanmean(index_open)
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuyQuantityPerUniqueOrderRatioSharpe(FutureFactor):
    '''
    Description: (ts_mean(buy_quantity_per_unique_order_ratio, 5) / ts_std(buy_quantity_unique_order_ratio, 5),
                buy_quantity_per_unique_order_ratio = cs_mean((BuyTradeQuantity / BuyUniqueOrderNum) 
                / ((BuyTradeQuantity + SellTradeQuantity) / (BuyUniqueOrderNum + SellUniqueOrderNum)), w=index_weight) - 1
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyUniqueOrderNum', 'SellUniqueOrderNum', 'BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 5
        weight = data['weight'].values
        buy_unique = data['BuyUniqueOrderNum'].values
        buy_q = data['BuyTradeQuantity'].values
        sell_unique = data['SellUniqueOrderNum'].values
        sell_q = data['SellTradeQuantity'].values
        
        buy_q_per_order = buy_q / buy_unique
        q_per_order = (buy_q + sell_q) / (buy_unique + sell_unique)
        f_temp = np.nansum(buy_q_per_order / q_per_order * weight, axis = 1) - 1
        
        return np.nanmean(f_temp[-lb:]) / np.nanstd(f_temp[-lb:])
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexBidAskGrowthDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalAskVol', 'TotalBidVol', 'adjfactor', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        weight = data['weight'].values[-lb:]
        adj = data['adjfactor'].values[-lb:]
        ask = data['TotalAskVol'].values[-lb:] / adj * adj[-1]
        ask[ask == 0] = np.nan
        bid = data['TotalBidVol'].values[-lb:] / adj * adj[-1]
        bid[bid == 0] = np.nan
        nan_num = np.isnan(ask).sum(axis=0) + np.isnan(bid).sum(axis=0)
        ask = ask[:, nan_num == 0]
        bid = bid[:, nan_num == 0]
        ask_diff = ask[1:] - ask[:-1]
        bid_diff = bid[1:] - bid[:-1]
        diff_ratio = (bid_diff - ask_diff) / (np.abs(bid_diff) + np.abs(ask_diff))
        f = np.nanmean(np.nansum(diff_ratio * weight[1:, nan_num == 0], axis=1))
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuyOrderNumQuotationRatio(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx 
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'BuyNumOrdersSumMean']
    normalize_size = 90
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values
        
        buy_ratio = BuyNumOrdersSumMean / Buy1NumOrdersMean
        
        N = 5
        f = - np.nanmean(buy_ratio[-N:])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor


class  MinuteContraVarietyCloseCorr(FutureFactor):
    '''
    Description: corr(Index_ClosePx, Index_Other1_ClosePx, 30)
    Class:Multi-Variety
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close'],'000300.SH':['close']}
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close =  data['close_000905.SH'].values 
        index_other_close =  data['close_000300.SH'].values 

        factor= np.corrcoef(index_close[-30:],index_other_close[-30:])[0,1]
                    
        return factor
    
    
##########
from future_factor import FutureFactor
import numpy as np


class MinuteLocalHighsOLSBeta(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 5
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 30
    normalize_type = 'ts_rank'
    
    def get_local_extrema(self, price):
        threshold = 2 * np.nanstd(price[1:] / price[:-1] - 1)
        localhighs = []
        locallows = []
        prel = 0
        preh = 0
        lh = 0
        ll = 0
        for i in range(len(price)):
            if price[lh] >= price[prel] * (1 + threshold) and price[lh] >= price[i] * (1 + threshold):
                localhighs.append(lh)
                lh = i
                prel = i
            else:
                if price[i] < price[lh] / (1 + threshold) or price[i] > price[lh]:
                    lh = i
                if price[i] <= price[prel]:
                    prel = i
            if price[ll] <= price[preh] / (1 + threshold) and price[ll] <= price[i] / (1 + threshold):
                locallows.append(ll)
                ll = i
                preh = i
            else:
                if price[i] > price[ll] * (1 + threshold) or price[i] < price[ll]:
                    ll = i
                if price[i] >= price[preh]:
                    preh = i
        if price[lh] >= price[prel] * (1 + threshold):
            localhighs.append(lh)
        if price[ll] <= price[preh] / (1 + threshold):
            locallows.append(ll)
        return localhighs, locallows
        
    def calculate(self, data):
        lb = 5 * 237
        close = data['close_000905.SH'].values[-lb:]
        lh, ll = self.get_local_extrema(close)
        if (len(ll) >= 3) & (len(lh) >= 3):
            beta_h = np.nanmean((close[lh] - np.nanmean(close[lh])) * (lh - np.nanmean(lh))) / np.nanvar(lh)
            f = beta_h
        else:
            f = 0
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexTotalAskBidVolSum(FutureFactor):
    '''
    Description: TotalAskVol / (Mean of TotalAskVol during past 5 days at the same minute) + TotalBidVol / (Mean of TotalBidVol during past 5 days at the same minute)
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['TotalAskVol', 'TotalBidVol']
    normalize_size = 30 
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        TotalAskVol = data['TotalAskVol'].values
        TotalBidVol = data['TotalBidVol'].values
        
        TotalAskVol_ratio = TotalAskVol[-237:] / np.nanmean(TotalAskVol[-1422:-237].reshape(5, 237, len(TotalAskVol[0])), axis=0)
        TotalBidVol_ratio = TotalBidVol[-237:] / np.nanmean(TotalBidVol[-1422:-237].reshape(5, 237, len(TotalBidVol[0])), axis=0)
        
        f = np.nansum(TotalAskVol_ratio[-1]) + np.nansum(TotalBidVol_ratio[-1])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowCorrMeanSharpeDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 120
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 236
        adj = data['adjfactor'].values
        close = data['close'].values * adj / adj[-1]
        rtn = close[1:] / close[:-1] - 1
        rtn = np.concatenate((rtn[:236], rtn[237:]), axis=0)
        rtn = rtn[-lb:]
        nan_num = np.isnan(rtn).sum(axis=0)
        zero_num = (rtn == 0).sum(axis=0)
        rtn = rtn[:, (nan_num == 0) & (zero_num < (lb / 2))]
        corr = np.corrcoef(rtn.T)
        corr_mean = corr.mean(axis=0)
        corr_mean_median = np.median(corr_mean)
        rtn_mean = rtn.mean(axis=0)
        rtn_mean_high = rtn_mean[corr_mean > corr_mean_median]
        rtn_mean_low = rtn_mean[corr_mean < corr_mean_median]
        f = rtn_mean_high.mean() / rtn_mean_high.std() - rtn_mean_low.mean() / rtn_mean_low.std()
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighLowLiquidityReturnDiff(FutureFactor):
    '''
    Description: high_low_diff((AskP0-BidP0)/volume_ratio, 20), cs_mean(r)
    Class: Group_Stat
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'volume', 'AskP0', 'BidP0']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        volume = data['volume'].values
        ask_0_price = data['AskP0'].values
        bid_0_price = data['BidP0'].values
        
        close_adj = close * adjfactor
        r = np.diff(close_adj[-238:], n=1, axis=0) / close_adj[-238:][:-1]
        spread = (ask_0_price[-238:] - bid_0_price[-238:]) / (ask_0_price[-238:] + bid_0_price[-238:])
        volume_ratio = volume[-237:] / np.nanmean(volume[-1422:-237].reshape(5, 237, len(close[0])), axis=0)
        
        N = 120
        liquidity = volume_ratio[-N:] / spread[-N:]
        liquidity[np.isinf(liquidity)] = np.nan
        liquidity_mean = np.nanmean(liquidity, axis=0)
        liquidity_high_limit = np.percentile(liquidity_mean[~np.isnan(liquidity_mean)], 80)
        liquidity_low_limit = np.percentile(liquidity_mean[~np.isnan(liquidity_mean)], 20)
        N = 30
        r_mean = np.nanmean(r[-N:], axis=0)
        f = np.nanmean(r_mean[liquidity_mean>liquidity_high_limit]) - np.nanmean(r_mean[liquidity_mean<liquidity_low_limit])
            
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60CloseStdMeanRatio(FutureFactor):
    '''
    Description: std(Index_ClosePx,60) / mean(Index_ClosePx,60)
    Class: Volatility
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 30 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 60
        close = data['close_000905.SH'].values[-n:]

        return np.nanstd(close) / np.nanmean(close)
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor


    


class  MinuteConsecutiveUpRatio(FutureFactor):
    '''
    Description: "sum(where((delay(Index_ClosePx, 2) < delay(Index_ClosePx, 1)) & (Index_ClosePx < delay(Index_ClosePx, 1)), 1, 0), 120)
                    / sum(where(delay(Index_ClosePx, 1) < Index_ClosePx, 1, 0), 120)"
    Class: MTM
    Author: hefj  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close']}
    
    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000905.SH'].values
        close_temp =  close[-120:]
        up = (close[1:] > close[:-1]).sum()
        consecutive_up = ((close_temp[:-2] < close_temp[1: -1]) & (close_temp[2:] > close_temp[1: -1])).sum()
        return consecutive_up/up
    
    


    
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownRangeRatio_Refined(FutureFactor):
    '''
    Description: cs_mean(ts_mean(where(rtn > 0, hml, nan), 30) / ts_mean(where(rtn < 0, hml, nan), 30)),
                 rtn = pct_chg(close * adjfactor, 1),
                 hml = high * adjfactor - low * adjfactor.
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'high', 'low', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-31:]
        close[close == 0] = np.nan
        high = data['high'].values[-30:]
        high[high == 0] = np.nan
        low = data['low'].values[-30:]
        low[low == 0] = np.nan
        adj = data['adjfactor'].values[-31:]
        close = close * adj
        high = high * adj[-30:]
        low = low * adj[-30:]
        rtn = np.diff(close, axis=0) / close[:-1]
        hml = high - low
        ratio = np.nanmean(np.where(rtn > 0, hml, np.nan), axis=0) / np.nanmean(np.where(rtn < 0, hml, np.nan), axis=0)
        ratio[np.isinf(ratio)] = np.nan
        f = np.nanmean(ratio)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteVolumeAutoCorr(FutureFactor):
    '''
    Description: corr(volume_ratio, shift(volume_ratio, 1), 60),
                 volume_ratio = volume[-240:] / mean(volume[-1440:-240].reshape(5, 240), axis=0)
    Class: Volume_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['volume']}
    normalize_size = 40 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        volume = data['volume_cont_IC'].values[-1440:]
        volume_ratio = volume[-240:] / np.nanmean(volume[:-240].reshape(5, 240), axis=0)
        f = np.corrcoef(volume_ratio[-60:], volume_ratio[-61:-1])[0, 1]
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowTrendRtnDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'high', 'low', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        adj = data['adjfactor'].values[-lb:]
        high = data['high'].values[-lb:] * adj / adj[-1]
        low = data['low'].values[-lb:] * adj / adj[-1]
        close = data['close'].values[-lb:] * adj / adj[-1]
        nan_num = np.isnan(high).sum(axis=0) + np.isnan(low).sum(axis=0) + np.isnan(close).sum(axis=0)
        high = high[:, nan_num == 0]
        low = low[:, nan_num == 0]
        close = close[:, nan_num == 0]
        mdd = -np.min(close / np.maximum.accumulate(high, axis=0) - 1, axis=0)
        mbb = np.max(close / np.minimum.accumulate(low, axis=0) - 1, axis=0)
        trend = np.minimum(mdd, mbb)
        trend = np.where(trend == 0, np.nan, trend)
        median = np.nanmedian(trend)
        rtn = close[-1] / close[0] - 1
        f = (rtn[trend > median].mean() - rtn[trend < median].mean()) / np.nanstd(rtn)
        return f

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor

class Minute30CloseLowDiff(FutureFactor):
    '''
    Description: mean(ClosePx, 30) / mean(LowPx, 30)
    Class: MTM
    Author: hefj, modeified by liuz
    '''

    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'low']}

    normalize_size=20*240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb=30
        factor = np.nanmean(data['close_cont_IC'].values[-lb:])- np.nanmean(data['low_cont_IC'].values[-lb:])
            
        return factor

##########
import numpy as np
from future_factor import FutureFactor

class MinuteInterestTreasure120Corr(FutureFactor):
    '''
    Description: corr(Interest, Treasure_LastPx, 120)
    Class: Treasure_Future
    Author: shentq, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['interest']}
    data_dict['Other_Variety'] = {'T':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        interest = data['interest_cont_IC'].values
        close_T = data['close_T'].values
        
        f = np.corrcoef(interest[-120:], close_T[-120:])[0, 1]
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinutePressureRtn(FutureFactor):
    '''
    Description: 
    Class: Bid_Ask
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'AskVol', 'BidVol']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].values
        askvol = data['AskVol_cont_IC'].values
        bidvol = data['BidVol_cont_IC'].values
        
        N = 60
        r = (np.diff(close) / close[:-1])[-N:]
        bid_ask_vol_diff = (bidvol - askvol)[-(N+1):-1]

        f = np.nansum((r<0) & (bid_ask_vol_diff<0))/np.nansum(r<0) - np.nansum((r>0)&(bid_ask_vol_diff>0))/np.nansum(r>0)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteBidAskVolDiffAutoCorr(FutureFactor):
    '''
    Description: autocorr(BidVol - AskVol, 50)
    Class: Bid_Ask
    Author: lixr, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol','AskVol']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 50        
        askvol_list = data['AskVol_cont_IC'].values[-n:]
        bidvol_list = data['BidVol_cont_IC'].values[-n:]    
        mask = np.isnan(askvol_list) | np.isnan(bidvol_list)
        askvol_list = askvol_list[~mask]
        bidvol_list = bidvol_list[~mask]
        
        bidaskvol_diff = bidvol_list - askvol_list   
        factor_value = np.corrcoef(bidaskvol_diff[:-1], bidaskvol_diff[1:])[0,1]
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value
##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor
import bottleneck as bn


class Minute60_10Speed(FutureFactor):
    '''
    Description: pct_chg(ema(ClosePx, 60), 10)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def __init__(self):
        super().__init__()
        self.ema_list = []

    def calculate(self, data):
        close = data['close_cont_IC'].values
        self.ema_list.append(self.calc_ema(self.ema_list, close[-1], 60))
        if len(self.ema_list) >= 70:
            close_ema_1 = self.ema_list[-1]
            close_ema_2 = self.ema_list[-11]
            factor_value = close_ema_1 / close_ema_2 - 1
        else:
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value

    def calc_ema(self, cur_ema_list, x_n, span=None):
        cur_ema_length = len(cur_ema_list)

        if span == None:
            span = cur_ema_length + 1
        else:
            span = min(cur_ema_length + 1, span)
            assert span > 0, "Invalid input of arg span!"

        alpha = 2 / (span + 1)

        if cur_ema_length == 0:
            return x_n
        else:
            return (alpha * x_n + (1 - alpha) * cur_ema_list[-1])
##########
from future_factor import FutureFactor
import numpy as np


class MinuteICIFReturnDiff(FutureFactor):
    '''
    Description: mean(pct_chg(close_000905.SH, 1) - pct_chg(close_000300.SH, 1), 15)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['close'], '000300.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_zz = data['close_000905.SH'].values[-16:]
        close_hs = data['close_000300.SH'].values[-16:]
        r_zz = (close_zz[1:] - close_zz[:-1]) / close_zz[:-1]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        f = np.nanmean(r_zz - r_hs)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteAskBidDiffStd(FutureFactor):
    '''
    Description: std(AskVol, 40) / mean(AskVol + BidVol, 240)
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['AskVol', 'BidVol']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        ask = data['AskVol_cont_IC'].values[-240:]
        bid = data['BidVol_cont_IC'].values[-240:]
        f = np.nanstd(ask[-40:] - bid[-40]) / np.nanmean(ask + bid)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteDistanceAmountOLSBeta(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['open', 'close', 'high', 'low', 'amount']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        open_px = data['open_000905.SH'].values
        close = data['close_000905.SH'].values
        high = data['high_000905.SH'].values
        low = data['low_000905.SH'].values
        amount = data['amount_000905.SH'].values
        x = amount
        y = 2 * (high - low) - (np.maximum(open_px, close) - np.minimum(open_px, close))
        is_ava = ~((x == 0) | (y == 0) | np.isnan(x) | np.isnan(y))
        x = x[is_ava][-lb:]
        y = y[is_ava][-lb:]
        f = -1 / (x.dot(x)) * (x.dot(y))
        return f

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexObVolWeightedRatio(FutureFactor):
    '''
    Description: "(weighted_cs_mean(BidVolMean[-1], w=index_weight) - weighted_cs_mean(AskVolMean[-1], w=index_weight))
                    / (weighted_cs_mean(BidVolMean[-1], w=index_weight) + weighted_cs_mean(AskVolMean[-1], w=index_weight))"
    Class:Bid_Ask
    Author: shentq modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=0
    data_dict=dict()
    data_dict['Stock'] = ['BidVolMean', 'AskVolMean', 'weight']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        BidVolMean = data['BidVolMean'].values[-1]
        AskVolMean = data['AskVolMean'].values [-1]
        weight = data['weight'].values[-1]
        bid_vol_sum = np.nansum(BidVolMean*weight)
        ask_vol_sum = np.nansum(AskVolMean*weight)
        
        if (bid_vol_sum + ask_vol_sum) == 0:
            factor = 0
        else:
            factor = (bid_vol_sum - ask_vol_sum) / (bid_vol_sum + ask_vol_sum)
        return factor



##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowBuySellMoneyPerUniqueSumReturnDiff(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'BuyTradeMoney', 'SellTradeMoney', 'close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values
        BuyTradeMoney = data['BuyTradeMoney'].values
        SellTradeMoney = data['SellTradeMoney'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        BuyMoneyPerUnique = BuyTradeMoney / BuyUniqueOrderNum
        SellMoneyPerUnique = SellTradeMoney / SellUniqueOrderNum
        BuySellMoneyPerUniqueSum = BuyMoneyPerUnique + SellMoneyPerUnique

        N = 40
        BuySellMoneyPerUniqueSum_mean = np.nanmean(BuySellMoneyPerUniqueSum[-N:], axis=0)
        BuySellMoneyPerUniqueSum_mean[np.isnan(BuySellMoneyPerUniqueSum_mean)] = np.nanmean(BuySellMoneyPerUniqueSum_mean)
        BuySellMoneyPerUniqueSum_mean_rank = (bn.rankdata(BuySellMoneyPerUniqueSum_mean)-1)/(len(BuySellMoneyPerUniqueSum_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[BuySellMoneyPerUniqueSum_mean_rank>0.5]) - np.nanmean(r_sum[BuySellMoneyPerUniqueSum_mean_rank<0.5])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteSpreadStdMeanRatio(FutureFactor):
    '''
    Description: BidAskVol / BidAskMean
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidAskVol', 'BidAskMean']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BidAskVol = data['BidAskVol_cont_IC'].values
        BidAskMean = data['BidAskMean_cont_IC'].values
                
        SpreadStdMeanRatio = BidAskVol / BidAskMean
        
        N = 20
        f = np.nanmean(SpreadStdMeanRatio[-N:])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteAskVolRatioMean(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['AskVol']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        ask = (data['AskVol_cont_IC']).values[-6 * 240:].reshape(-1, 240)
        ask_ratio = (ask[-1] / np.nanmean(ask[:-1], axis=0))[-lb:]
        f = np.nanmean(ask_ratio)
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexUniqueSellRatioMA10(FutureFactor):
    '''
    Description: cs_mean(ts_mean(SellUniqueOrderNum, 10)) / cs_mean(ts_mean(SellTradeNum, 10))
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 10

        sell_unique_num = data['SellUniqueOrderNum'].values[-n:]
        sell_trade_num = data['SellTradeNum'].values[-n:]

        sell_unique_num_mean = np.nanmean(np.nanmean(sell_unique_num))
        sell_trade_num_mean = np.nanmean(np.nanmean(sell_trade_num))

        factor_value = sell_unique_num_mean / sell_trade_num_mean

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexUniqueBuyRatioSkew(FutureFactor):
    '''
    Description: ts_mean(cs_skew(BuyUniqueOrderNum / BuyTradeNum), 5)
    Class:Buy_Sell
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']

    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        BuyTradeNum = data['BuyTradeNum'].values
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        df_buy_unique_ratio = BuyUniqueOrderNum / BuyTradeNum
        s = skew(df_buy_unique_ratio[-5:],axis=1,nan_policy='omit',bias=False)

        factor = np.nanmean(np.array(s))

        return factor



##########
from future_factor import FutureFactor


class MinuteStyleRtnDiff(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['close'], '000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        close_50 = data['close_000016.SH'].values
        close_300 = data['close_000300.SH'].values
        close_500 = data['close_000905.SH'].values
        rtn_50 = close_50[-1] / close_50[-lb - 1] - 1
        rtn_300 = close_300[-1] / close_300[-lb - 1] - 1
        rtn_500 = close_500[-1] / close_500[-lb - 1] - 1
        rtn_min, rtn_max = min(rtn_50, rtn_300, rtn_500), max(rtn_50, rtn_300, rtn_500)
        f = (rtn_500 - rtn_min) / (rtn_max - rtn_min)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexOrderImbalanceStd(FutureFactor):
    '''
    Description: -ts_mean(cs_std((bid - ask) / (bid + ask)), 20),
                 bid = BidV0 + BidV1 + BidV2 + BidV3 + BidV4,
                 ask = AskV0 + AskV1 + AskV2 + AskV3 + AskV4.
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        bid0 = data['BidV0'].values[-20:]
        bid0[bid0 == 0] = np.nan
        bid1 = data['BidV1'].values[-20:]
        bid1[bid1 == 0] = np.nan
        bid2 = data['BidV2'].values[-20:]
        bid2[bid2 == 0] = np.nan
        bid3 = data['BidV3'].values[-20:]
        bid3[bid3 == 0] = np.nan
        bid4 = data['BidV4'].values[-20:]
        bid4[bid4 == 0] = np.nan
        ask0 = data['AskV0'].values[-20:]
        ask0[ask0 == 0] = np.nan
        ask1 = data['AskV1'].values[-20:]
        ask1[ask1 == 0] = np.nan
        ask2 = data['AskV2'].values[-20:]
        ask2[ask2 == 0] = np.nan
        ask3 = data['AskV3'].values[-20:]
        ask3[ask3 == 0] = np.nan
        ask4 = data['AskV4'].values[-20:]
        ask4[ask4 == 0] = np.nan
        bid = bid0 + bid1 + bid2 + bid3 + bid4
        ask = ask0 + ask1 + ask2 + ask3 + ask4
        order_imbalance = (bid - ask) / (bid + ask)
        f = -np.nanmean(np.nanstd(order_imbalance, axis=1))
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexUniqueBuyQuantityRatio(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeQuantity']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 240
        n2 = 10

        buy_unique_num = data['BuyUniqueOrderNum'].values[-n1:]
        buy_trade_quantity = data['BuyTradeQuantity'].values[-n1:]

        buy_order_size = buy_trade_quantity / buy_unique_num
        buy_order_size = np.where(np.isinf(buy_order_size), np.nan, buy_order_size)

        factor_value = np.nanmean(np.nanmean(buy_order_size[-n2:] / np.nanmean(buy_order_size, axis=0)))

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexTurnoverWeightCorr(FutureFactor):
    '''
    Description: ts_mean(cs_corr(amount, weight), 10)
    Class: Liq_Cs_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['amount', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount'].values[-10:]
        amount[amount == 0] = np.nan
        weight = data['weight'].values[-1]
        corr = []
        for j in range(1, 11):
            valid = np.logical_and(~np.isnan(amount[-j]), ~np.isnan(weight))
            c = np.corrcoef(amount[-j][valid], weight[valid])[0, 1]
            if np.isnan(c):
                c = 0
            corr = np.append(corr, c)
        f = np.nanmean(corr)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowAutoCorrSharpeDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 90
        adj = data['adjfactor'].values
        close = (data['close'].values * adj / adj[-1])
        rtn = close[1:] / close[:-1] - 1
        rtn = rtn[-lb:]
        nan_num = np.isnan(rtn).sum(axis=0)
        zero_num = (rtn == 0).sum(axis=0)
        rtn = rtn[:, (nan_num == 0) & (zero_num < lb / 2)]
        auto_corr = ((rtn[1:] - rtn.mean(axis=0)) * (rtn[:-1] - rtn.mean(axis=0))).mean(axis=0) / rtn.var(axis=0)
        auto_corr_median = np.median(auto_corr)
        rtn_high = rtn[:, auto_corr > auto_corr_median]
        rtn_low = rtn[:, auto_corr < auto_corr_median]
        f = rtn_high.mean() / rtn_high.std() - rtn_low.mean() / rtn_low.std()
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteAskVolStd(FutureFactor):
    '''
    Description: std(AskVol, 20) / mean(AskVol, 240)
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['AskVol']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['AskVol_cont_IC'].values[-240:]
        f = np.nanstd(ask[-20:]) / np.nanmean(ask)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteTotalValueTrade3Ratio(FutureFactor):
    '''
    Description: mean(TotalValueTrade_03 / (TotalValueTrade_00 + TotalValueTrade_01 + TotalValueTrade_02 + TotalValueTrade_03), 10)
    Class: All_Contract
    Author: jinpx, modified by jinpx
    '''   
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Future_Instrument'] = {'00':['TotalValueTrade'], '01':['TotalValueTrade'], '02':['TotalValueTrade'], '03':['TotalValueTrade']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        totalvaluetrade_00 = data['TotalValueTrade_00'].values
        totalvaluetrade_01 = data['TotalValueTrade_01'].values
        totalvaluetrade_02 = data['TotalValueTrade_02'].values
        totalvaluetrade_03 = data['TotalValueTrade_03'].values
        
        N = 10
        totalvaluetrade_ratio = totalvaluetrade_03[-N:]/(totalvaluetrade_00[-N:]+totalvaluetrade_01[-N:]+totalvaluetrade_02[-N:]+totalvaluetrade_03[-N:])
        f = np.nanmean(totalvaluetrade_ratio)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteBounceZScore240(FutureFactor):
    '''
    Description: z_score(close - cum_min(low) / cum_min(low), 240)
    Class: Return_Risk
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close','low']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        close = data['close_cont_IC'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        low = data['low_cont_IC'].values
        low[low == 0] = np.nan
        low_temp = low[-lb:]
        mask = np.isnan(close_temp) | np.isnan(low_temp)
        close_temp = close_temp[~mask]
        low_temp = low_temp[~mask]
        
        price_min = np.minimum.accumulate(low_temp)
        bounce = (close_temp - price_min) / price_min
            
        return (bounce[-1] - np.mean(bounce)) / np.std(bounce)
##########
import numpy as np
from future_factor import FutureFactor

class MinuteCloseRtnCorr(FutureFactor):
    '''
    Description: corr(pct_chg(close_000905.SH, 1), delay(close_000905.SH, 1), 60) 
                 - corr(pct_chg(close_000905.SH, 1), close_000905.SH, 60)
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values[-lb:]
        close[close == 0] = np.nan
        
        p = close[~np.isnan(close)]
        r = p[1:] / p[:-1] - 1
        
        return np.corrcoef(r, p[:-1])[0,1] - np.corrcoef(r, p[1:])[0,1]
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew

class  MinuteIndexBSUniqueDiff30Ma(FutureFactor):
    '''
    Description: ts_mean(cs_sum(SellUniqueOrderNum) / cs_sum(SellTradeNum) - cs_sum(BuyUniqueOrderNum) / cs_sum(BuyTradeNum), 30)
    Class:Buy_Sell
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'BuyTradeNum', 'SellTradeNum']

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-30:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-30:]
        BuyTradeNum = data['BuyTradeNum'].values[-30:]
        SellTradeNum = data['SellTradeNum'].values[-30:]
        
        buy_unique_num_list =np.nansum(BuyUniqueOrderNum,axis=1).tolist()
        sell_unique_num_list = np.nansum(SellUniqueOrderNum,axis=1).tolist()
        buy_num_list = np.nansum(BuyTradeNum,axis=1).tolist()
        sell_num_list = np.nansum(SellTradeNum,axis=1).tolist()

        buy_unique_ratio_list = []
        sell_unique_ratio_list = []

        buy_sell_unique_diff_list = []
        
        for i in range(len(buy_unique_num_list)):
            if buy_num_list[i] == 0:
                buy_unique_ratio_list.append(0)
            else:
                buy_unique_ratio_list.append(buy_unique_num_list[i] / buy_num_list[i])

            if sell_num_list[i] == 0:
                sell_unique_ratio_list.append(0)
            else:
                sell_unique_ratio_list.append(sell_unique_num_list[i] / sell_num_list[i])

            buy_sell_unique_diff_list.append(sell_unique_ratio_list[-1] - buy_unique_ratio_list[-1])
        
        factor = np.nanmean(buy_sell_unique_diff_list[-30:])
        return factor

##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteSwing5Mean60(FutureFactor):
    '''
    Description: mean((max(close, 5) - min(close, 5)) / delay(close, 5), 60)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        close = data['close_cont_IC'].values
        
        swing_5 = (bn.move_max(close, 5) - bn.move_min(close, 5))[5:] / close[:-5]

        N = 60
        f = np.nanmean(swing_5[-N:])
        
        return f
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor

    
    
class  MinuteCVICorr(FutureFactor):
    '''
    Description: -corr(Index_ClosePx, Interest + Volume, 30)
    Class:PV_Corr
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC': ['volume', 'interest']}
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close_list =  data['close_000905.SH'].values 
        volume_list =  data['volume_cont_IC'].values 
        interest_list =  data['interest_cont_IC'].values 
        
        new_volume_list = [volume_list[i]+interest_list[i] for i in range(len(volume_list))]
        factor = -np.corrcoef(index_close_list[-30:],new_volume_list[-30:])[0,1]
        
        return factor
    
    

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowStdRtnDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 237
        adj = data['adjfactor'].values
        close = (data['close'].values * adj / adj[-1])[-lb - 1:]
        rtn = close[1:] / close[:-1] - 1
        zero_num = (np.abs(rtn) < 1 / 10000).sum(axis=0)
        rtn = rtn[:, zero_num < (lb / 2)]
        std = np.std(rtn, axis=0)
        median = np.nanmedian(std)
        rtn_high_std = rtn[:, std > median]
        rtn_low_std = rtn[:, std < median]
        f = np.nanmean(rtn_high_std) - np.nanmean(rtn_low_std)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteTwapCloseRatio(FutureFactor):
    '''
    Description: -mean(twap, 30) / mean(close, 30)
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close', 'twap']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_cont_IC'].values[-30:]
        twap = data['twap_cont_IC'].values[-30:]
        f = -np.mean(twap) / np.mean(close)
        return f

##########
import numpy as np
from future_factor import FutureFactor


class MinuteAccUpDownAmountRatio(FutureFactor):

    def __init__(self):
        super().__init__()
        self.acc_up_amount = 0
        self.acc_down_amount = 0
        self.acc_up_amount_list = []
        self.acc_down_amount_list = []

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close', 'amount']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close = data['close_000905.SH'].values
        amount = data['amount_000905.SH'].values

        if len(self.acc_up_amount_list) == 0:
            for i in range(15):
                idx = -(15-i)
                if close[idx] < close[idx-1]:
                    self.acc_up_amount = amount[idx]
                    self.acc_down_amount += amount[idx]
                else:
                    self.acc_up_amount += amount[idx]
                    self.acc_down_amount = amount[idx]

                self.acc_up_amount_list.append(self.acc_up_amount)
                self.acc_down_amount_list.append(self.acc_down_amount)
        else:

            if close[-1] < close[-2]:
                self.acc_up_amount = amount[-1]
                self.acc_down_amount += amount[-1]
            else:
                self.acc_up_amount += amount[-1]
                self.acc_down_amount = amount[-1]

            self.acc_up_amount_list.append(self.acc_up_amount)
            self.acc_down_amount_list.append(self.acc_down_amount)

        ratio_array = np.array(self.acc_up_amount_list[-15:]) / np.array(self.acc_down_amount_list[-15:])
        ratio_array[np.isinf(ratio_array)] = 1
        factor_value = np.nanmean(ratio_array)

        return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIlliquidityStd(FutureFactor):
    '''
    Description: - Std(AbsDistance/amount, 15)
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['AbsDistance', 'amount']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        AbsDistance = data['AbsDistance_cont_IC'].values
        amount = data['amount_cont_IC'].values
        
        AbsDistance_ratio = AbsDistance[-240:] / np.nanmean(AbsDistance[-1440:-240].reshape(5, 240), axis=0)
        amount_ratio = amount[-240:] / np.nanmean(amount[-1440:-240].reshape(5, 240), axis=0)
        
        illiquidity = AbsDistance_ratio / amount_ratio
        
        N = 15
        f = - np.nanstd(illiquidity[-N:])
        
        return f
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHLUniqueBuyRetDiff(FutureFactor):
    '''
    Description: high_low_diff(BuyTradeNum/BuyUniqueOrderNum, 20), cs_mean(r(20))
    Class: Group_Stat
    Author: lixr, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'BuyUniqueOrderNum', 'BuyTradeNum', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        buy_unique_num = data['BuyUniqueOrderNum'].values
        buy_trade_num = data['BuyTradeNum'].values
        close_adj = close * adjfactor
        
        n = 20
        buy_order_size = buy_trade_num[-1,:] / buy_unique_num[-1,:]
        buy_order_size[np.isinf(buy_order_size)] = np.nan
        buy_order_size_rank = (bn.rankdata(buy_order_size)-1)/(len(buy_order_size)-1)
        ret = (close_adj[-1,:] - close_adj[-n,:]) / close_adj[-n,:]
        f = np.nanmean(ret[buy_order_size_rank > 0.75]) - np.nanmean(ret[buy_order_size_rank < 0.25])

        if np.isnan(f):
            f = 0
            
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexWeightedBidAskTotalVolRatio(FutureFactor):
    '''
    Description: weighted_cs_mean(TotalBidVol[-1], w=index_weight) / weighted_cs_mean(TotalAskVol[-1], w=index_weight)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        weight_ratio = data['weight'].values[-1] / np.nansum(data['weight'].values[-1])

        buy = np.nansum(data['TotalBidVol'].values[-1] * weight_ratio)
        sell = np.nansum(data['TotalAskVol'].values[-1] * weight_ratio)

        if sell == 0:
            factor_value = 0
        else:
            factor_value = buy / sell

        return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIFIHSharpeDiff(FutureFactor):
    '''
    Description: sharpe(pct_chg(close_000300.SH, 1), 15) - sharpe(pct_chg(close_000016.SH, 1), 15)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000016.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_hs = data['close_000300.SH'].values[-16:]
        close_sz = data['close_000016.SH'].values[-16:]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        r_sz = (close_sz[1:] - close_sz[:-1]) / close_sz[:-1]
        f = np.nanmean(r_hs) / np.nanstd(r_hs) - np.nanmean(r_sz) / np.nanstd(r_sz)
        return f

##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexObLevelsDiff(FutureFactor):
    '''
    Description: 
    Class: Bid_Ask
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'BidVolMean', 'AskVolMean']

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        TotalBidVol = data['TotalBidVol'].values
        TotalAskVol = data['TotalAskVol'].values
        BidVolMean = data['BidVolMean'].values
        AskVolMean = data['AskVolMean'].values

        bid_levels = TotalBidVol / BidVolMean
        ask_levels = TotalAskVol / AskVolMean
        
    
        bid_levels[np.isnan(bid_levels) | np.isinf(bid_levels)] = np.nan
        ask_levels[np.isnan(ask_levels) | np.isinf(ask_levels)] = np.nan

        factor = np.nanmean(np.nanmean((bid_levels-ask_levels)[-10:],axis=0))
        
        return factor




##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew





class  MinuteIndexUpDownCountDiff(FutureFactor):
    '''
    Description: "(cs_sum(where(ClosePx * Adjfactor / shift(ClosePx * Adjfactor, 60) > Index_ClosePx / shift(Index_ClosePx, 60), 1, 0))
        - cs_sum(where(ClosePx * Adjfactor / shift(ClosePx * Adjfactor, 60) < Index_ClosePx / shift(Index_ClosePx, 60), 1, 0)))[-1]"
    Class: Group_Stat
    Author:  shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        rtn_back = 60

        index_close = data['close_000905.SH'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values

        close_adj = close*adjfactor
        rtn = close_adj[rtn_back:]/close_adj[:-rtn_back]-1
        rtn_index = index_close[rtn_back:]/index_close[:-rtn_back]-1
        
        upcount = np.nansum(np.where(rtn[-1]> rtn_index[-1], 1,0))
        downcount =  np.nansum(np.where(rtn[-1] < rtn_index[-1], 1,0))
        
        factor = downcount-upcount
        
        return  factor
##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownRangeSumRatio(FutureFactor):
    '''
    Description: (sum(where(close_000905.SH > open_000905.SH, high_000905.SH - low_000905.SH, 0), 30) 
                 - sum(where(close_000905.SH < open_000905.SH, high_000905.SH - low_000905.SH, 0), 30))
                / (sum(where(close_000905.SH > open_000905.SH, high_000905.SH - low_000905.SH, 0), 30) 
                 + sum(where(close_000905.SH < open_000905.SH, high_000905.SH - low_000905.SH, 0), 30))
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','open','high','low']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        op = data['open_000905.SH'].values
        op[op == 0] = np.nan
        high = data['high_000905.SH'].values
        high[high == 0] = np.nan
        low = data['low_000905.SH'].values
        low[low == 0] = np.nan
        
        range_temp = high[-lb:] - low[-lb:]
        up_temp = range_temp[close[-lb:] > op[-lb:]].sum()
        down_temp = range_temp[close[-lb:] < op[-lb:]].sum()
        
        return (up_temp - down_temp) / (up_temp + down_temp)
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverBuySellNumRatioDiff(FutureFactor):
    '''
    Description: cs_mean(where(turnoverrank > 0.5, buysellratio, nan)) - cs_mean(where(turnoverrank < 0.2, buysellratio, nan)),
                 turnoverrank = cs_rank(ts_mean(Turnover, 140)),buysellratio = ts_mean(BuyTradeNum / SellTradeNum, 6)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'amount']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 6
        n2 = 140

        buy = data['BuyTradeNum'].values[-n1:]
        sell = data['SellTradeNum'].values[-n1:]
        ratio = buy / sell
        ratio[np.isinf(ratio)] = np.nan
        ratio_mean = np.nanmean(ratio, axis=0)

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        return np.nanmean(ratio_mean[turnover_rank > 0.5]) - np.nanmean(ratio_mean[turnover_rank < 0.5])

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteWeightedRSI(FutureFactor):
    '''
    Description: "sum(where(Index_ClosePx > Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx > Index_OpenPx, -0.01, 0)[-120:])), 120)
/ (sum(where(Index_ClosePx > Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx > Index_OpenPx, -0.01, 0)[-120:])), 120)
+ sum(where(Index_ClosePx < Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx < Index_OpenPx, -0.01, 0)[-120:])), 120))"
    Class: MTM
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] = {'000905.SH':['close','open']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close_000905.SH'].values 
        open_ = data['open_000905.SH'].values 
        rtn_list = close/open_-1


        rtn_up_sum = 0
        rtn_down_sum = 0
        up_weight = 2
        down_weight = 2

        for i in range(120):
            if rtn_list[i-120] > 0:
                rtn_up_sum += abs(rtn_list[i-120]) * up_weight
                up_weight += -0.01
            elif rtn_list[i-120] < 0:
                rtn_down_sum += abs(rtn_list[i-120]) * down_weight
                down_weight += -0.01

        factor = rtn_up_sum / (rtn_up_sum+rtn_down_sum)

        return  factor
    

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownSpreadRatio(FutureFactor):
    '''
    Description: ts_mean(ts_mean(where(rtn_cs_mean > 0, spread_cs_mean, nan), 40) / ts_mean(where(rtn_cs_mean < 0, spread_cs_mean, nan), 40), 10),
                 rtn_cs_mean = cs_mean(pct_chg(close * adjfactor, 1)),
                 spread_cs_mean = cs_mean(AskP0 - BidP0).
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'BidP0', 'AskP0', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-51:]
        close[close == 0] = np.nan
        bid = data['BidP0'].values[-50:]
        bid[bid == 0] = np.nan
        ask = data['AskP0'].values[-50:]
        ask[ask == 0] = np.nan
        adj = data['adjfactor'].values[-51:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        spread = ask - bid
        ratio = []
        for j in range(1, 11):
            r = np.nanmean(rtn[-(40 + j): -j], axis=1)
            s = np.nanmean(spread[-(40 + j): -j], axis=1)
            ratio.append(np.nanmean(s[r > 0]) / np.nanmean(s[r < 0]))
        f = np.nanmean(ratio)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteOpenCloseCorr(FutureFactor):
    '''
    Description: corr(open, close, 60)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['open', 'close']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        open_price = data['open_cont_IC'].values
        close_price = data['close_cont_IC'].values
        
        N = 60
        f = np.corrcoef(open_price[-N:], close_price[-N:])[0, 1]
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexNewHighNewLowRatio(FutureFactor):
    '''
    Description:(cs_sum(ts_max(close, 240) == close[-1]) - cs_sum(ts_min(close, 240) == close[-1]))
                / (cs_sum(ts_max(close, 240) == close[-1]) + cs_sum(ts_min(close, 240) == close[-1]))    
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        new_high = np.where(np.nanmax(close[-lb:], axis=0) == close[-1], 1, 0).sum()
        new_low = np.where(np.nanmin(close[-lb:], axis=0) == close[-1], 1, 0).sum()
        
        if (new_high + new_low) == 0:
            return 0
        else:
            return (new_high - new_low) / (new_high + new_low)
##########
import numpy as np
from future_factor import FutureFactor

class MinuteTreasureRtn120Ma(FutureFactor):
    '''
    Description: -mean(pct_chg(Treasure_LastPx, 1), 120)
    Class: Treasure_Future
    Author: shentq, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Variety'] = {'T':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        close_T = data['close_T'].values
        r_T = np.diff(close_T) / close_T[:-1]
        
        f = - np.nanmean(r_T[-120:])
        
        return f
##########
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class MinuteIndexBidAskVolSkewRatio(FutureFactor):
    '''
    Description: -cs_skew(TotalBidVol[-1]) / skew(TotalAskVol[-1])
    Class: Bid_Ask
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        total_bid_vol = data['TotalBidVol'].values[-1]
        total_ask_vol = data['TotalAskVol'].values[-1]

        skew_bid = stats.skew(total_bid_vol, nan_policy='omit')
        skew_ask = stats.skew(total_ask_vol, nan_policy='omit')

        return -skew_bid / skew_ask
##########
