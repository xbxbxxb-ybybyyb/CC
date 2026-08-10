import numpy as np
import pandas as pd
from future_factor import FutureFactor

class MinuteIndexSmallBigOrderDiff_IF(FutureFactor):

    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money', 'buy_bigorder_money' ,'sell_smallorder_money', 'sell_bigorder_money']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        buy_smallorder_money =  data['buy_smallorder_money'].values 
        buy_bigorder_money =  data['buy_bigorder_money'].values 
        sell_smallorder_money =  data['sell_smallorder_money'].values 
        sell_bigorder_money =  data['sell_bigorder_money'].values 

        buy = np.nansum(buy_smallorder_money[-lb:],axis=0)/np.nansum(buy_bigorder_money[-lb:],axis=0)
        buy[np.isinf(buy)] = np.nan
        sell = np.nansum(sell_smallorder_money[-lb:],axis=0)/np.nansum(sell_bigorder_money[-lb:],axis=0)
        sell[np.isinf(sell)] = np.nan
        factor = np.nanmean(buy)-np.nanmean(sell)
        return -factor
##########
from future_factor import FutureFactor
import numpy as np


class  MinuteContraVarietyCloseCorr_IF(FutureFactor):
    '''
    Description: corr(Index_ClosePx, Index_Other1_ClosePx, 30)
    Class: Multi-Variety
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
        index_close = data['close_000905.SH'].values 
        index_other_close = data['close_000300.SH'].values 

        factor= np.corrcoef(index_close[-30:],index_other_close[-30:])[0,1]
                    
        return factor
    

##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownRtnMean_IF(FutureFactor):
    '''
    Description: (close_000300.SH / min(close_000300.SH, 60) - 1) / (60 - argmin(close_000300.SH, 60)) 
                + (close_000300.SH / max(close_000300.SH, 60) - 1) / (60 - argmax(close_000300.SH, 60))
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000300.SH'].values
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
from future_factor import FutureFactor
import numpy as np


class  MinuteIndexUpDownCountDiff_IF(FutureFactor):
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
    data_dict['Index_Id'] = {'000300.SH':['close']}
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        rtn_back = 120

        index_close = data['close_000300.SH'].values
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

class MinuteIndexBidAskRatioSharpe_IF(FutureFactor):
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
import pandas as pd
from future_factor import FutureFactor


class  MinuteMaxGrowthMaxDrawdownTimeDiff_IF(FutureFactor):

    data_type='Future'
    instrument_type='recent'
    days_past= 5
    data_dict=dict()

    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size= 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        lb = 237
        close_index = data['close_000300.SH'].values
        rtn = close_index[1:]/close_index[:-1]-1

        rtn = rtn[-lb:]

        i = np.argmax(np.maximum.accumulate(rtn) - rtn)  # 结束位置
        if i == 0:
            return 0
        j = np.argmax(rtn[:i])  # 开始位置

        mdd = i-j
        i = np.argmin(np.minimum.accumulate(rtn) - rtn)  # 结束位置
        if i == 0:
            return 0
        j = np.argmin(rtn[:i])  # 开始位置
        mcl = i-j

        return mcl-mdd



##########
from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexAmountRatioTSSkew_IF(FutureFactor):
    '''
    Description: -cs_mean(ts_skew(amount_ratio, 30)),
                 amount_ratio[i, :] = amount[i, :] / ts_mean(amount[i - n * 237, :], n=1, 2, ..., 5).
    Class: Liq_Ts_Stat
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 7
    data_dict = {}
    data_dict['Stock'] = ['amount']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        amount = data['amount'].values[-6 * 237:].reshape(6, 237, -1)
        amount_ratio = amount[-1] / np.nanmean(amount[:-1], axis=0)
        amount_ratio = amount_ratio[-30:]
        
        nan_inf_num = np.isnan(amount_ratio).sum(axis=0) + np.isinf(amount_ratio).sum(axis=0)
        amount_ratio = amount_ratio[:, nan_inf_num == 0]
        
        f = -np.mean(skew(amount_ratio, axis=0))
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexSharpeMean30_IF(FutureFactor):
    '''
    Description: cs_weighted_mean(ts_mean(rtn, 30) / ts_std(rtn, 30), w=weight),
                 rtn = pct_chg(close * adjfactor, 1).
    Class: MTM
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        weight = data['weight'].values[-1]
        close = data['close'].values[-lb - 1:]
        close[close == 0] = np.nan
        adj = data['adjfactor'].values[-lb - 1:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = close[1:] / close[:-1] - 1
        inf_nan_num = np.isnan(rtn).sum(axis=0) + np.isinf(rtn).sum(axis=0)
        rtn = rtn[:, inf_nan_num == 0]
        sharpe = np.nanmean(rtn, axis=0) / np.nanstd(rtn, axis=0)
        f = np.nansum(sharpe * weight[inf_nan_num == 0])
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteLongTermRtn_IF(FutureFactor):
    '''
    Description: mean(rtn, from 09:30 T-5),
                 rtn = pct_chg(close_000300.SH, 1)
    Class: MTM
    Author: hefj
    '''
    data_type = 'Future'
    days_past = 5
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000300.SH'].values
        rtn = close[1:] / close[:-1] - 1
        f = np.nanmean(rtn)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexBidAskRatioDiff_IF(FutureFactor):
    '''
    Description: cs_weighted_mean(ts_mean(bid_ask_ratio_g, 20), w=weight),
                 bid_ask_ratio_g = diff(bid_ask_ratio, 1),
                 bid_ask_ratio = (TotalBidVol - TotalAskVol) / (TotalBidVol + TotalAskVol).
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'weight']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        bid = data['TotalBidVol'].values[-21:]
        bid[bid == 0] = np.nan
        ask = data['TotalAskVol'].values[-21:]
        ask[ask == 0] = np.nan
        weight = data['weight'].values[-1]
        ratio = (bid - ask) / (bid + ask)
        g = ratio[1:] - ratio[:-1]
        nan_num = np.isnan(g).sum(axis=0)
        g = g[:, nan_num == 0]
        f = np.nansum(np.nanmean(g, axis=0) * weight[nan_num == 0])
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteCalmarRatio120min_IF(FutureFactor):
    '''
    Description: calmar(index_close, 120)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000300.SH'].values
        
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
from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexAmountRatioCSSkew_IF(FutureFactor):
    '''
    Description: -ts_mean(cs_skew(amount_ratio), 30),
                 amount_ratio[i, :] = amount[i, :] / ts_mean(amount[i - n * 237, :], n=1, 2, ..., 5).
    Class: Liq_Cs_Stat
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 7
    data_dict = {}
    data_dict['Stock'] = ['amount']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        amount = data['amount'].values[-self.days_past * 237:].reshape(self.days_past, 237, -1)
        amount_ratio = amount[-1] / np.nanmean(amount[:-1], axis=0)
        amount_ratio = amount_ratio[-30:]
        
        nan_inf_num = np.isnan(amount_ratio).sum(axis=0) + np.isinf(amount_ratio).sum(axis=0)
        amount_ratio = amount_ratio[:, nan_inf_num == 0]
        
        f = -np.mean(skew(amount_ratio, axis=1))
        return f


##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskBidDepthRatioStd_IF(FutureFactor):
    '''
    Description: -ts_mean(cs_std((AskP4 - AskP0) / (BidP0 - BidP4)), 30)
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
        bid_0 = data['BidP0'].values[-30:]
        bid_0[bid_0 == 0] = np.nan
        bid_4 = data['BidP4'].values[-30:]
        bid_4[bid_4 == 0] = np.nan
        ask_0 = data['AskP0'].values[-30:]
        ask_0[ask_0 == 0] = np.nan
        ask_4 = data['AskP4'].values[-30:]
        ask_4[ask_4 == 0] = np.nan
        ratio = (ask_4 - ask_0) / (bid_0 - bid_4)
        ratio[np.isinf(ratio)] = np.nan
        f = -np.nanmean(np.nanstd(ratio, axis=1))
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexObLv1AmtPerOrderRatioSharpe_IF(FutureFactor):
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

class MinuteIlliquidityStd_IF(FutureFactor):
    '''
    Description: - Std(AbsDistance/amount, 15)
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF': ['AbsDistance', 'amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        AbsDistance = data['AbsDistance_cont_IF'].values
        amount = data['amount_cont_IF'].values
        
        AbsDistance_ratio = AbsDistance[-240:] / np.nanmean(AbsDistance[-1440:-240].reshape(5, 240), axis=0)
        amount_ratio = amount[-240:] / np.nanmean(amount[-1440:-240].reshape(5, 240), axis=0)
        
        illiquidity = AbsDistance_ratio / amount_ratio
        
        N = 15
        f = - np.nanstd(illiquidity[-N:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteInterestRatioStd_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['interest']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        interest = data['interest_cont_IF'].values
        
        N = 20
        interest_ratio = interest[-N:] / np.nansum(interest[-N:]) 

        f = - np.nanstd(interest_ratio[-N:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBidAskSpreadMeanRatioSum_IF(FutureFactor):
    '''
    Description: BidAskSpreadMean / (Mean of BidAskSpreadMean during past 5 days at the same minute)
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['BidAskSpreadMean']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        BidAskSpreadMean = data['BidAskSpreadMean'].values
        
        BidAskSpreadMean_ratio = BidAskSpreadMean[-237:] / np.nanmean(BidAskSpreadMean[-1422:-237].reshape(5, 237, len(BidAskSpreadMean[0])), axis=0)
        
        N = 3
        f = - np.nansum(BidAskSpreadMean_ratio[-N:])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskBidDepthRatio_IF(FutureFactor):
    '''
    Description: ts_mean(cs_mean((BidP0 / BidP4 - 1) / (AskP4 / AskP0 - 1)), 10)
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidP0', 'BidP4', 'AskP0', 'AskP4']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        bid_0 = data['BidP0'].values[-10:]
        bid_0[bid_0 == 0] = np.nan
        bid_4 = data['BidP4'].values[-10:]
        bid_4[bid_4 == 0] = np.nan
        ask_0 = data['AskP0'].values[-10:]
        ask_0[ask_0 == 0] = np.nan
        ask_4 = data['AskP4'].values[-10:]
        ask_4[ask_4 == 0] = np.nan
        ratio = (bid_0 / bid_4 - 1) / (ask_4 / ask_0 - 1)
        ratio[np.isinf(ratio)] = np.nan
        f = np.nanmean(ratio)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class  MinuteOBVolInterest120Corr_IF(FutureFactor):
    '''
    Description: corr(Interest, AskVol + BidVol, 120)
    Class: Bid_Ask
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IF':['AskVol', 'BidVol','interest']}

    normalize_size=5*240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IF'].values 
        BidVol = data['BidVol_cont_IF'].values 
        Interest = data['interest_cont_IF'].values 

        ob_vol = AskVol+BidVol
        factor = np.corrcoef(ob_vol[-237:], Interest[-237:])[0,1]
        return  factor

##########
import numpy as np
from future_factor import FutureFactor

class MinuteUpDownAmountDiff_IF(FutureFactor):
    '''
    Description: sum(where(index_close >= delay(index_close, 1), index_amount, 0), 90) / sum(index_amount, 90)
    Class: MTM
    Author: liuz, modified by jinpx
    '''   
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'amount']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        N = 90
        index_amount = data['amount_000300.SH'].values[-N:]
        index_close = data['close_000300.SH'].values[-N:]
        
        index_r = np.append(np.nan, np.diff(index_close) / index_close[:-1])
        f = np.nansum(index_amount[index_r>=0]) / np.nansum(index_amount)        
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class  MinuteLongtermUpdownAmtRatio_IF(FutureFactor):
    '''
    Description: "-corr(ClosePx, index_turnover_ratio_all, 60),
                index_turnover_ratio_all = (Contract0_Turnover + Contract1_Turnover + Contract2_Turnover + Contract3_Turnover) / Index_Turnover"
    Class:PV_Corr
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past= 5
    data_dict=dict()


    data_dict['Index_Id'] = {'000300.SH':['close','amount']}
    normalize_size= 60
    normalize_type = 'ts_rank'

    def calculate(self, data):
        lb = 237*5

        close_index = data['close_000300.SH'].values[-lb:]
        amount_index = data['amount_000300.SH'].values[-lb:][1:]
        re = close_index[1:]/close_index[:-1]-1

        factor = np.nansum(amount_index[re>0])/np.nansum(amount_index[re<=0])
        return factor


##########
import numpy as np
from future_factor import FutureFactor

class MinuteOpenCloseCorr_IF(FutureFactor):
    '''
    Description: corr(open, close, 60)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['open', 'close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_open = data['open_000300.SH'].values
        index_close = data['close_000300.SH'].values
        
        N = 45
        f = np.corrcoef(index_open[-N:], index_close[-N:])[0, 1]
        
        return f
##########
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class MinuteIndexHLTurnoverBSOrderQtyRatioDiff_IF(FutureFactor):
    '''
    Description: mean(ratio(rank > 0.8)) - mean(ratio(rank < 0.2)),
                 ratio = -1 * mean(BuyOrderQtySumMean / SellOrderQtySumMean, 10)
                 rank = rank(mean(turnover_rate, 120))
    Class: Group_Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyOrderQtySumMean','SellOrderQtySumMean','turnover_rate']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n1 = 10
        n2 = 120
        threshold = 0.8
        
        buy = data['BuyOrderQtySumMean'].values
        buy[buy == 0] = np.nan
        sell = data['SellOrderQtySumMean'].values
        sell[sell == 0] = np.nan
        turnover = data['turnover_rate'].values
        
        ratio = -1 * np.nanmean(buy[-n1:] / sell[-n1:], axis = 0)
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
from future_factor import FutureFactor
import numpy as np


class MinuteICIFUpNum_IF(FutureFactor):
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
from future_factor import FutureFactor
import numpy as np


class MinuteHighLowCorr_IF(FutureFactor):
    '''
    Description: corr(high_000300.SH, low_000300.SH, 30)
    Class: Price_Stat
    Author: hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['high', 'low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high_000300.SH'].values[-30:]
        low = data['low_000300.SH'].values[-30:]
        f = np.corrcoef(high, low)[0, 1]
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowAutoCorrSharpeDiff_IF(FutureFactor):
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
        rtn_high = rtn[:, auto_corr > np.percentile(auto_corr, 2 / 3 * 100)]
        rtn_low = rtn[:, auto_corr < np.percentile(auto_corr, 1 / 3 * 100)]
        f = rtn_high.mean() / rtn_high.std() - rtn_low.mean() / rtn_low.std()
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteTtimesTFutureReturnCorr_IF(FutureFactor):
    '''
    Description: mean(rtn_t, 30) * corr(rtn, rtn_t, 240 * 5),
                 rtn = pct_chg(close, 1),
                 rtn_t = pct_chg(close_T, 1).
    Class: Treasure_Future
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 5
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close']}
    data_dict['Other_Variety'] = {'T': ['close']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        t = data['close_T'].values[-240 * self.days_past - 1:]
        close = data['close_000300.SH'].values[-240 * self.days_past - 1:]
        rtn_t = np.diff(t) / t[:-1]
        rtn = np.diff(close) / close[:-1]
        f = np.mean(rtn_t[-30:]) * np.corrcoef(rtn_t, rtn)[0, 1]
        return f

##########
from future_factor import FutureFactor
import numpy as np
from scipy import stats

class  MinuteIndexUniqueBuyRatioSkew_IF(FutureFactor):
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

    
    normalize_size= 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        BuyTradeNum = data['BuyTradeNum'].values
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        df_buy_unique_ratio = BuyUniqueOrderNum / BuyTradeNum
        s = stats.skew(df_buy_unique_ratio[-30:],axis=1,nan_policy='omit',bias=False)

        factor = np.nanmean(np.array(s))

        return factor

##########
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class MinuteIndexHLTurnoverBSBigOrderCountRatioDiff_IF(FutureFactor):
    '''
    Description: mean(ratio(rank > 0.9)) - mean(ratio(rank < 0.1)),
                 ratio = mean(buy_bigorder_count / sell_bigorder_count, 60)
                 rank = rank(mean(turnover_rate, 237))
    Class: Group_Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_count','sell_bigorder_count','turnover_rate']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n1 = 60
        n2 = 237
        threshold = 0.9
        
        buy = data['buy_bigorder_count'].values
        buy[buy == 0] = np.nan
        sell = data['sell_bigorder_count'].values
        sell[sell == 0] = np.nan
        turnover = data['turnover_rate'].values
        
        ratio = np.nanmean(buy[-n1:] / sell[-n1:], axis = 0)
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

class MinuteIndexRtnAutoCorr_IF(FutureFactor):
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


class MinuteNegIFDownICUpNum_IF(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 237
        close_300 = data['close_000300.SH'].values
        close_500 = data['close_000905.SH'].values        
        f = -((close_300[1:] < close_300[:-1]) & (close_500[1:] > close_500[:-1]))[-lb:].sum()
        return f

##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexUniqueBuyQuantityRatio_IF(FutureFactor):
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
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowSuperBigCountReturnDiff_IF(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count', 'sell_superorder_count', 'buy_bigorder_count', 'sell_bigorder_count',
                          'buy_midorder_count', 'sell_midorder_count', 'buy_smallorder_count', 'sell_smallorder_count',
                          'close', 'adjfactor']
    normalize_size = 180
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        buy_superorder_count = data['buy_superorder_count'].values
        sell_superorder_count = data['sell_superorder_count'].values
        buy_bigorder_count = data['buy_bigorder_count'].values
        sell_bigorder_count = data['sell_bigorder_count'].values
        buy_midorder_count = data['buy_midorder_count'].values
        sell_midorder_count = data['sell_midorder_count'].values
        buy_smallorder_count = data['buy_smallorder_count'].values
        sell_smallorder_count = data['sell_smallorder_count'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]

        N = 5*237
        buy_super_big_count_ratio = (buy_superorder_count + buy_bigorder_count) / (buy_superorder_count + buy_bigorder_count + buy_midorder_count + buy_smallorder_count)
        sell_super_big_count_ratio = (sell_superorder_count + sell_bigorder_count) / (sell_superorder_count + sell_bigorder_count + sell_midorder_count + sell_smallorder_count)
        buy_sell_super_big_count_ratio_sum = np.nanmean(buy_super_big_count_ratio[-N:], axis=0) + np.nanmean(sell_super_big_count_ratio[-N:], axis=0)
        buy_sell_super_big_count_ratio_sum_rank = (bn.rankdata(buy_sell_super_big_count_ratio_sum)-1)/(len(buy_sell_super_big_count_ratio_sum)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = -(np.nanmean(r_sum[buy_sell_super_big_count_ratio_sum_rank>0.8]) - np.nanmean(r_sum[buy_sell_super_big_count_ratio_sum_rank<0.2]))
   
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteApb1_IF(FutureFactor):
    '''
    Description: mean(amount / volume, 95) / (sum(amount, 95) / sum(volume, 95))
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['volume', 'amount']}
    normalize_size = 35 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        volume = data['volume_cont_IF'].values
        amount = data['amount_cont_IF'].values
        vwap = amount / volume
        N = 95
        f = np.nanmean(vwap[-N:]) / (np.nansum(amount[-N:]) / np.nansum(volume[-N:]))
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteLocalExtremaOLSBetaMean_IF(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 5
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close']}
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
        lb = 5 * 237
        close = data['close_000300.SH'].values[-lb:]
        lh, ll = self.get_local_extrema(close)
        if (len(ll) >= 3) & (len(lh) >= 3):
            beta_h = np.nanmean((close[lh] - np.nanmean(close[lh])) * (lh - np.nanmean(lh))) / np.nanvar(lh)
            beta_l = np.nanmean((close[ll] - np.nanmean(close[ll])) * (ll - np.nanmean(ll))) / np.nanvar(ll)
            f = (beta_l + beta_h) / 2
        else:
            f = 0
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownSpreadRatio_IF(FutureFactor):
    '''
    Description: cs_mean(ts_mean(where(rtn < 0, spread, nan), 20) / ts_mean(where(rtn > 0, spread, nan), 20)),
                 rtn = pct_chg(close, 1),
                 spread = ask_price / bid_price,
                 ask_price = (AskP0 * AskV0 + AskP1 * AskV1) / (AskV0 + AskV1),
                 bid_price = (BidP0 * BidV0 + BidP1 * BidV1) / (BidV0 + BidV1).
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'BidP0', 'AskP0', 'BidP1', 'AskP1', 'BidV0', 'AskV0', 'BidV1', 'AskV1', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        close = data['close'].values[-lb - 1:]
        close[close == 0] = np.nan
        
        ask_p = []
        bid_p = []
        ask_v = []
        bid_v = []
        for j in range(2):
            ask_p.append(data['AskP{}'.format(j)].values[-lb:])
            bid_p.append(data['BidP{}'.format(j)].values[-lb:])
            ask_v.append(data['AskV{}'.format(j)].values[-lb:])
            bid_v.append(data['BidV{}'.format(j)].values[-lb:])
        ask_p = np.array(ask_p)
        ask_p[ask_p == 0] = np.nan
        bid_p = np.array(bid_p)
        bid_p[bid_p == 0] = np.nan
        ask_v = np.array(ask_v)
        ask_v[ask_v == 0] = np.nan
        bid_v = np.array(bid_v)
        bid_v[bid_v == 0] = np.nan
        
        bid_p_mean = np.sum(bid_p * bid_v, axis=0) / np.sum(bid_v, axis=0)
        ask_p_mean = np.sum(ask_p * ask_v, axis=0) / np.sum(ask_v, axis=0)
        
        spread = ask_p_mean / bid_p_mean
        rtn = close[1:] / close[:-1] - 1
        nan_num = np.isnan(spread).sum(axis=0) + np.isnan(rtn).sum(axis=0)
        spread = spread[:, nan_num == 0]
        rtn = rtn[:, nan_num == 0]
        
        up_spread = np.nanmean(np.where(rtn > 0, spread, np.nan), axis=0)
        down_spread = np.nanmean(np.where(rtn < 0, spread, np.nan), axis=0)
        f = np.nanmean(down_spread / up_spread)

        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteStyleRtnDiff_IF(FutureFactor):
    '''
    Description: mean(rtn_300 - rtn_500, 15) + mean(rtn_300 - rtn_50),
                 rtn_300 = pct_chg((close_000300.SH + high_000300.SH + low_000300.SH) / 3, 1),
                 rtn_500 = pct_chg((close_000905.SH + high_000905.SH + low_000905.SH) / 3, 1),
                 rtn_50 = pct_chg((close_000016.SH + high_000016.SH + low_000016.SH) / 3, 1).
    Class: Multi-Variety
    Author: hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['close', 'high', 'low'], '000300.SH': ['close', 'high', 'low'], '000905.SH': ['close', 'high', 'low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        price_sz = (data['close_000016.SH'].values[-16:] + data['high_000016.SH'].values[-16:] + data['low_000016.SH'].values[-16:]) / 3
        price_hs = (data['close_000300.SH'].values[-16:] + data['high_000300.SH'].values[-16:] + data['low_000300.SH'].values[-16:]) / 3
        price_zz = (data['close_000905.SH'].values[-16:] + data['high_000905.SH'].values[-16:] + data['low_000905.SH'].values[-16:]) / 3
        r_sz = (price_sz[1:] - price_sz[:-1]) / price_sz[:-1]
        r_hs = (price_hs[1:] - price_hs[:-1]) / price_hs[:-1]
        r_zz = (price_zz[1:] - price_zz[:-1]) / price_zz[:-1]
        f = np.nanmean(r_hs - r_zz) + np.nanmean(r_hs - r_sz)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighLowLiquidityReturnDiff_IF(FutureFactor):
    '''
    Description: high_low_diff((AskP0-BidP0)/volume_ratio, 20), cs_mean(r)
    Class: Group_Stat
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 7
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
        N = 20
        r_mean = np.nanmean(r[-N:], axis=0)
        f = np.nanmean(r_mean[liquidity_mean>liquidity_high_limit]) - np.nanmean(r_mean[liquidity_mean<liquidity_low_limit])
            
        return f
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowBuySellTradeNumSumReturnDiff_IF(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'close', 'adjfactor']
    normalize_size = 150
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        BuyTradeNum = data['BuyTradeNum'].values
        SellTradeNum = data['SellTradeNum'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        BuySellTradeNumSum = BuyTradeNum + SellTradeNum
        N = 5 * 237
        BuySellTradeNumSum_mean = np.nanmean(BuySellTradeNumSum[-N:], axis=0)
        BuySellTradeNumSum_mean_rank = (bn.rankdata(BuySellTradeNumSum_mean)-1)/(len(BuySellTradeNumSum_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[BuySellTradeNumSum_mean_rank>0.8]) - np.nanmean(r_sum[BuySellTradeNumSum_mean_rank<0.2])
        
        return f
##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowCorrReturnDiff_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'adjfactor']
    normalize_size = 60
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        stk_index_corr_hs300 = data['stk_index_corr_hs300'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5 * 237
        stk_index_corr_hs300_mean = np.nanmean(stk_index_corr_hs300[-N:], axis=0)
        stk_index_corr_hs300_mean_rank = bn.rankdata(stk_index_corr_hs300_mean) / len(stk_index_corr_hs300_mean)
        
        r_sum = np.nansum(r[-N:], axis=0)
        
        f = np.nanmean(r_sum[stk_index_corr_hs300_mean_rank>0.8]) - np.nanmean(r_sum[stk_index_corr_hs300_mean_rank<0.2])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexNewHighNewLowSizeDiff_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'adjfactor', 'float_shares']
    normalize_size = 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        close = data['close'].values
        high = data['high'].values
        low = data['low'].values
        adjfactor = data['adjfactor'].values
        float_shares = data['float_shares'].values
        close_adj = close * adjfactor
        high_adj = high * adjfactor
        low_adj = low * adjfactor
        
        high_num = np.nansum((np.nanmax(high_adj[-60:], axis=0) > np.max(high_adj[-3*237:-60], axis=0)) * close_adj[-1] * float_shares[-1])
        low_num = np.nansum((np.nanmax(low_adj[-60:], axis=0) < np.min(low_adj[-3*237:-60], axis=0)) * close_adj[-1] * float_shares[-1])
        
        f = high_num - low_num
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class  MinuteFSTurnRatioCloseCorr_IF(FutureFactor):
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

    data_dict['Continuous_Data'] = {'IF':['close']}
    data_dict['Index_Id'] = {'000300.SH':['amount',]}
    data_dict['Other_Future_Instrument'] = {'00':['amount'],'01':['amount'],'02':['amount'],'03':['amount']}
    
    normalize_size= 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_turnover = data['amount_000300.SH'].values
        future_turnover = [data['amount_00'].values[i] + data['amount_01'].values[i] + data['amount_02'].values[i] + data['amount_03'].values[i] for i in range(len(data['amount_02'].values))] 
        index_close =  data['close_cont_IF'].values
        turnover_ratio = []
        for i in range(len(index_turnover)):
            if index_turnover[i] == 0:
                turnover_ratio.append(1)
            else:
                turnover_ratio.append(future_turnover[i] / index_turnover[i])
        factor = -np.corrcoef(turnover_ratio[-90:],index_close[-90:])[0,1]

        return factor

##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowMoneyPerUniqueReturnDiff_IF(FutureFactor):
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
    normalize_size = 20 * 237
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
        MoneyPerUnique = BuyMoneyPerUnique + SellMoneyPerUnique

        N = 60
        MoneyPerUnique_mean = np.nanmean(MoneyPerUnique[-N:], axis=0)
        MoneyPerUnique_mean[np.isnan(MoneyPerUnique_mean)] = np.nanmean(MoneyPerUnique_mean)
        MoneyPerUnique_mean_rank = (bn.rankdata(MoneyPerUnique_mean)-1)/(len(MoneyPerUnique_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[MoneyPerUnique_mean_rank>0.5]) - np.nanmean(r_sum[MoneyPerUnique_mean_rank<0.5])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighLowTurnoverRatioAbs_IF(FutureFactor):
    '''
    Description: abs(cs_mean((ts_mean(where(close > ts_quantile(close, 0.9), amount, nan), 30) 
                - ts_mean(where(close < ts_quantile(close, 0.1), amount, nan),30)) 
                / (ts_mean(where(close > ts_quantile(close, 0.9), amount, nan), 30) 
                + ts_mean(where(close < ts_quantile(close, 0.1), amount, nan), 30))))
    Class: PV_Corr
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','close', 'amount', 'adjfactor']
    normalize_size = 3 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexBidRatioDiff_IF(FutureFactor):
    '''
    Description: cs_weighted_mean(ts_mean(diff(bid_ratio, 1), 30), w=weight),
                 bid_ratio[i, :] = TotalBidVol_adj[i, :] / ts_mean(TotalBidVol_adj[i - n * 237, :], n=1, 2, ..., 5),
                 TotalBidVol_adj = forward_adj(TotalBidVol).
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 7
    data_dict = {}
    data_dict['Stock'] = ['TotalBidVol', 'adjfactor', 'weight']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        bid = data['TotalBidVol'].values[-6 * 237:]
        bid[bid == 0] = np.nan
        adj = data['adjfactor'].values[-6 * 237:]
        adj[adj == 0] = np.nan
        bid = bid / adj * adj[-1]
        weight = data['weight'].values[-1]
        
        bid = bid.reshape(6, 237, -1)
        bid_ratio = bid[-1] / np.nanmean(bid[:-1], axis=0)
        
        g = (bid_ratio[1:] - bid_ratio[:-1])[-30:]
        inf_nan_num = np.isnan(g).sum(axis=0) + np.isinf(g).sum(axis=0)
        g = g[:, inf_nan_num == 0]
        f = np.nansum(np.nanmean(g, axis=0) * weight[inf_nan_num == 0])
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteConsecutiveUpRatio40_IF(FutureFactor):
    '''
    Description: sum(where((delay(close_000300.SH, 2) < delay(close_000300.SH, 1)) & (close_000300.SH < delay(close_000300.SH, 1)), 1, 0), 40)
                / sum(where(delay(close_000300.SH, 1) < close_000300.SH, 1, 0), 40)
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 40
        close = data['close_000300.SH'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        close_temp = close_temp[~np.isnan(close_temp)]
        
        up = (close_temp[1:] > close_temp[:-1]).sum()
        consecutive_up = ((close_temp[:-2] < close_temp[1: -1]) & (close_temp[2:] > close_temp[1: -1])).sum()
       
        return consecutive_up / up
##########
import numpy as np
import pandas as pd
from future_factor import FutureFactor


class  MinuteMaxDrawDownTime_IF(FutureFactor):

    data_type='Future'
    instrument_type='recent'
    days_past= 5
    data_dict=dict()

    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size= 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        lb = 30
        close_index = data['close_000300.SH'].values
        rtn = close_index[1:]/close_index[:-1]-1

        rtn = rtn[-lb:]

        i = np.argmax(np.maximum.accumulate(rtn) - rtn)  # 结束位置
        if i == 0:
            return 0
        j = np.argmax(rtn[:i])  # 开始位置




        return i-j
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBidAskTotVolMA20DiffRatio_IF(FutureFactor):
    '''
    Description: ts_mean((cs_sum(TotalBidVol) - cs_sum(TotalAskVol)) / (cs_sum(TotalBidVol) + cs_sum(TotalAskVol)), 20)
    Class: Bid_Ask
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'adjfactor']
    normalize_size = 1 * 237
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexOrderImbalanceStd_IF(FutureFactor):
    '''
    Description: -ts_mean(cs_std((bid - ask) / (bid + ask)), 5),
                 bid = BidV0 + BidV1 + BidV2 + BidV3 + BidV4,
                 ask = AskV0 + AskV1 + AskV2 + AskV3 + AskV4.
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 5
        bid0 = data['BidV0'].values[-lb:]
        bid0[bid0 == 0] = np.nan
        bid1 = data['BidV1'].values[-lb:]
        bid1[bid1 == 0] = np.nan
        bid2 = data['BidV2'].values[-lb:]
        bid2[bid2 == 0] = np.nan
        bid3 = data['BidV3'].values[-lb:]
        bid3[bid3 == 0] = np.nan
        bid4 = data['BidV4'].values[-lb:]
        bid4[bid4 == 0] = np.nan
        ask0 = data['AskV0'].values[-lb:]
        ask0[ask0 == 0] = np.nan
        ask1 = data['AskV1'].values[-lb:]
        ask1[ask1 == 0] = np.nan
        ask2 = data['AskV2'].values[-lb:]
        ask2[ask2 == 0] = np.nan
        ask3 = data['AskV3'].values[-lb:]
        ask3[ask3 == 0] = np.nan
        ask4 = data['AskV4'].values[-lb:]
        ask4[ask4 == 0] = np.nan
        bid = bid0 + bid1 + bid2 + bid3 + bid4
        ask = ask0 + ask1 + ask2 + ask3 + ask4
        order_imbalance = (bid - ask) / (bid + ask)
        f = -np.nanmean(np.nanstd(order_imbalance, axis=1))
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowSpreadReturnDiff_IF(FutureFactor):
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
        high_level = np.quantile(spread[~np.isnan(spread)], 0.5)
        low_level = np.quantile(spread[~np.isnan(spread)], 0.5)
        rtn_high = np.nanmean(rtn[:, spread > high_level], axis=1)
        rtn_low = np.nanmean(rtn[:, spread < low_level], axis=1)
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioSharpe_IF(FutureFactor):
    '''
    Description: ts_mean(weighted_cs_mean(BuyTradeQuantity / SellTradeQuantity - 1, w=index_weight), 30)
                / ts_std(weighted_cs_mean(BuyTradeQuantity / SellTradeQuantity - 1, w=index_weight), 30)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
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

class MinuteIndexBuyOrderNumQuotationRatio_IF(FutureFactor):
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
    normalize_size = 120
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values
        
        buy_ratio = BuyNumOrdersSumMean / Buy1NumOrdersMean
        
        N = 5        
        f = - np.nanmean(buy_ratio[-N:])
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class  MinuteIndexBSUniqueDiff30Ma_IF(FutureFactor):
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

    normalize_size=20*237
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

class MinuteIndexHighLowBuySellUniqueOrderNumSumReturnDiff_IF(FutureFactor):
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
    normalize_size = 180
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

class MinuteVR1Corr15Sr120_IF(FutureFactor):
    '''
    Description: mean(corr(pct_chg(close, 1), volume, 15), 120) / std(corr(pct_chg(close, 1), volume, 15), 120)
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
              
        volume = data['volume_cont_IF'].values  
        close = data['close_cont_IF'].values
        r = (close[1:] - close[:-1]) / close[:-1]
        r_volume_corr_15 = self.rolling_corr(r, volume[1:], 15)
        N = 120
        f = np.nanmean(r_volume_corr_15[-N:]) / np.nanstd(r_volume_corr_15[- N:], ddof=1)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexWeightedBuySellUniqueOrderNumDiff_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values
        weight = data['weight'].values
        
        BuySellUniqueDiff = BuyUniqueOrderNum - SellUniqueOrderNum

        N = 120
        BuySellUniqueDiff_mean = np.nanmean(BuySellUniqueDiff[-N:], axis=0)
        f = - np.nansum(weight[-1] * BuySellUniqueDiff_mean)
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskVolDiffSharpe_IF(FutureFactor):
    '''
    Description: -cs_mean(ts_mean(ask_g, 20) / ts_std(ask_g, 20)),
                 ask_g = diff(TotalAskVol / adjfactor * adjfactor[-1], 1)
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalAskVol', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['TotalAskVol'].values[-21:]
        ask[ask == 0] = np.nan
        adj = data['adjfactor'].values[-21:]
        adj[adj == 0] = np.nan
        ask = ask / adj * adj[-1]
        ask_g = ask[1:] - ask[:-1]
        nan_num = np.isnan(ask_g).sum(axis=0)
        ask_g = ask_g[:, nan_num < 5]
        f = -np.nanmean(np.nanmean(ask_g, axis=0) / np.nanstd(ask_g, axis=0))
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteLocalHighLowReverse_IF(FutureFactor):
    '''
    Description: 
    Class: Local_High_Low
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 20
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 75
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
        
        index_close = data['close_000300.SH'].values
        
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


class MinuteIndexUniqueSellRatioMA10_IF(FutureFactor):
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
from future_factor import FutureFactor

class MinuteDownsideReSR30_IF(FutureFactor):
    '''
    Description: mean(where(pct_chg(index_close, 1) > 0, 0, pct_chg(index_close, 1)), 30) / std(where(pct_chg(index_close, 1) > 0, 0, pct_chg(index_close, 1)), 30)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''  
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close = data['close_000300.SH'].values
        index_r = np.diff(index_close) / index_close[:-1]
        index_r[index_r>=0] = 0
        N = 30
        f = np.nanmean(index_r[-N:]) / np.nanstd(index_r[-N:])
        if np.isnan(f):
            f = 0
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteDistanceAmountOLSBeta_IF(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['open', 'close', 'high', 'low', 'amount']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        open_px = data['open_000300.SH'].values
        close = data['close_000300.SH'].values
        high = data['high_000300.SH'].values
        low = data['low_000300.SH'].values
        amount = data['amount_000300.SH'].values
        x = amount
        y = 2 * (high - low) - (np.maximum(open_px, close) - np.minimum(open_px, close))
        is_ava = ~((x == 0) | (y == 0) | np.isnan(x) | np.isnan(y))
        x = x[is_ava][-lb:]
        y = y[is_ava][-lb:]
        f = -1 / (x.dot(x)) * (x.dot(y))
        return f

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHLCorrRetDiff_IF(FutureFactor):
    '''
    Description: mean(return((rank(corr) > 0.5), 5days)) - mean(return((rank(corr) < 0.5), 5days))
                 corr = corr(close,close_000300.SH, 5days)
    Class: Group Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        threshold = 0.5
        n = 5 * 237
        adjfactor = data['adjfactor'].values
        stock_close = data['close'].values * adjfactor
        index_close = data['close_000300.SH'].values.flatten()
        
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
import numpy as np
from future_factor import FutureFactor

class MinuteSpotFutureCloseCorr_IF(FutureFactor):
    '''
    Description: corr(close, close_000300.SH, 30)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_cont_IF'].values
        close[close == 0] = np.nan
        index_close = data['close_000300.SH'].values
        index_close[index_close == 0] = np.nan   
        mask = np.isnan(index_close[-lb:]) | np.isnan(close[-lb:])
        
        return np.corrcoef(index_close[-lb:][~mask], close[-lb:][~mask])[0,1]
##########
from future_factor import FutureFactor
import numpy as np
from scipy.stats import pearsonr


class MinuteIndexHighLowRtnStdRatio_IF(FutureFactor):
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
import numpy as np
import pandas as pd
from future_factor import FutureFactor

class MinuteIndexAsk1Bid1Beta_IF(FutureFactor):

    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Bid1AmtMean', 'Ask1AmtMean','weight' ]
    normalize_size =  120
    normalize_type = 'ts_rank'

    def calculate(self, data):

        lb = 237


        Ask1AmtMean =  data['Ask1AmtMean'].values[-lb:]
        Bid1AmtMean =  data['Bid1AmtMean'].values[-lb:]
        weight = data['weight'].values[-1]


        BETA= []
        for i in range(len(Ask1AmtMean[0])):
            Ask1AmtMean_s = Ask1AmtMean[:,i] 
            Bid1AmtMean_s = Bid1AmtMean[:,i]
            beta = (np.nansum(Ask1AmtMean_s*Bid1AmtMean_s)*len(Ask1AmtMean_s)-np.nansum(Ask1AmtMean_s)*np.nansum(Bid1AmtMean_s))/(len(Bid1AmtMean_s)*np.nansum(Bid1AmtMean_s*Bid1AmtMean_s)-np.nansum(Bid1AmtMean_s)*np.nansum(Bid1AmtMean_s))
            BETA.append(beta)
        factor = np.nanmean(BETA*weight)

        return factor
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellSuperorderCountDiff_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count', 'sell_superorder_count']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        buy_superorder_count = data['buy_superorder_count'].values
        sell_superorder_count = data['sell_superorder_count'].values
        buy_superorder_count[np.isnan(buy_superorder_count)] = 0
        sell_superorder_count[np.isnan(sell_superorder_count)] = 0
        diff = buy_superorder_count - sell_superorder_count
        
        N = 10
        f = np.nanmean(np.nanmean(diff[-N:], axis=1))
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteTreasureRtn120Ma_IF(FutureFactor):
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
import numpy as np
from future_factor import FutureFactor

class MinuteSpreadStdMeanRatio_IF(FutureFactor):
    '''
    Description: BidAskVol / BidAskMean
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['BidAskVol', 'BidAskMean']}
    normalize_size = 120
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BidAskVol = data['BidAskVol_cont_IF'].values
        BidAskMean = data['BidAskMean_cont_IF'].values
        
        SpreadStdMeanRatio = BidAskVol / BidAskMean
        
        N = 20
        f = np.nanmean(SpreadStdMeanRatio[-N:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownRtnMean_IF(FutureFactor):
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
        
        lb = 237
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
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteIndexNetNewBidAskDiffSkew_IF(FutureFactor):
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
    normalize_size = 3 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 237
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

class MinuteVolumeSpreadRatio_IF(FutureFactor):
    '''
    Description: mean(volume_ratio / ((AskP0 - BidP0) / (AskP0 + BidP0)), 45)
                 volume_ratio = volume / (the average volume at current time over past 5 trading days)
    Class: Liquidity
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 8
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['volume', 'AskP0', 'BidP0']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        volume = data['volume_cont_IF'].values
        ask_0 = data['AskP0_cont_IF'].values
        bid_0 = data['BidP0_cont_IF'].values
        
        spread = (ask_0 - bid_0) / (ask_0 + bid_0)
        volume_ratio = volume[-240:] / np.nanmean(volume[-1440:-240].reshape(5, 240), axis=0)
            
        N = 45
        liquidity = volume_ratio[-N:] / spread[-N:] 
        liquidity[np.isinf(liquidity)] = np.nan

        f = np.nanmean(liquidity)
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLocalHighLowPredictDistance_IF(FutureFactor):
    '''
    Description: 
    Class: Local_High_Low
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
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
                
        index_close = data['close_000300.SH'].values
        
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

class MinuteVolumeShrinkReturn_IF(FutureFactor):
    '''
    Description: 
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    data_dict['Other_Future_Instrument'] = {'00':['volume'], '01':['volume'], '02':['volume'], '03':['volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        close = data['close_cont_IF'].values
        volume_00 = data['volume_00'].values
        volume_01 = data['volume_01'].values
        volume_02 = data['volume_02'].values
        volume_03 = data['volume_03'].values
        
        volume = (volume_00 + volume_01 + volume_02 + volume_03)
        r = (close[5:] - close[:-5]) / close[:-5]
        volume_ratio = volume[-237:] / np.nansum(volume[-1422:-237].reshape(5, 237), axis=0)
        volume_ratio_change = volume_ratio[5:] - volume_ratio[:-5]
        N = 30
        f = np.nanmean(r[-N:][volume_ratio_change[-N:]<0])
        if np.isnan(f):
            f = 0
        
        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteADL_IF(FutureFactor):
    '''
    Description: mean((ClosePx - OpenPx) / (HighPx - LowPx), 120)
    Class: MTM
    Author:jinpx,  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000300.SH':['close','low', 'open', 'high']}

    normalize_size= 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        lb=120
        factor =(data['close_000300.SH'].values[-lb:]-data['open_000300.SH'].values[-lb:])/(data['high_000300.SH'].values[-lb:]-data['low_000300.SH'].values[-lb:])

        return np.nanmean(factor)

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellOrderNumQuotationRatio_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx 
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'Sell1NumOrdersMean', 'BuyNumOrdersSumMean', 'SellNumOrdersSumMean']
    normalize_size = 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values
        Sell1NumOrdersMean = data['Sell1NumOrdersMean'].values
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values
        SellNumOrdersSumMean = data['SellNumOrdersSumMean'].values
        
        buy_ratio = BuyNumOrdersSumMean / Buy1NumOrdersMean
        sell_ratio = SellNumOrdersSumMean / Sell1NumOrdersMean
        
        N = 20
        f = - (np.nanmean(buy_ratio[-N:]) - np.nanmean(sell_ratio[-N:]))
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteMtmSustainability_IF(FutureFactor):
    '''
    Description: auto_corr(pct_chg(close, 1), 30) * (sum(where(close > delay(close, 1), 1, 0), 30) - 15)
    Class: MTM
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000300.SH'].values
        index_r = np.diff(index_close) / index_close[:-1]
        
        N = 60
        index_r_autocorr = np.corrcoef(index_r[-N:], index_r[-(N+1):-1])[0, 1]
        counter = np.sum(index_r[-N:]>0) - N/2
        f = index_r_autocorr * counter
        
        return f
##########
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class MinuteIndexHLBigSmallOrderCountRatioRetDiff_IF(FutureFactor):
    '''
    Description: mean(return((rank(ratio) > 0.8), 5days)) - mean(return((rank(ratio) < 0.2), 5days)),
                 ratio = mean(buy_smallorder_count + sell_smallorder_count, 5days) / mean(buy_bigorder_count + sell_bigorder_count, 5days)           
    Class: Group Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 5 
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','weight', \
                          'buy_smallorder_count','sell_smallorder_count','buy_bigorder_count','sell_bigorder_count']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        threshold = 0.8
        n1 = 5 * 237
        n2 = 5 * 237
        adjfactor = data['adjfactor'].values
        weight = data['weight'].values[-1]
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        small_buy = data['buy_smallorder_count'].values
        small_buy[small_buy == 0] = np.nan
        small_sell = data['sell_smallorder_count'].values
        small_sell[small_sell == 0] = np.nan
        big_buy = data['buy_bigorder_count'].values
        big_buy[big_buy == 0] = np.nan
        big_sell = data['sell_bigorder_count'].values
        big_sell[big_sell == 0] = np.nan
        
        small = np.nanmean(small_buy[-n1:], axis = 0) + np.nanmean(small_sell[-n1:], axis = 0)
        big = np.nanmean(big_buy[-n1:], axis = 0) + np.nanmean(big_sell[-n1:], axis = 0)
        ratio = small / big
        rank = bk.rankdata(ratio) / len(ratio)
        ret = (close[-1] / close[-(n2 + 1)] - 1) * weight 
        factor_value = np.nanmean(ret[rank > threshold]) - np.nanmean(ret[rank <= (1 - threshold)])
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexNewHighNewLowRatio_IF(FutureFactor):
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
        
        lb = 237
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexEMV_IF(FutureFactor):
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
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        high = data['high'].values[-lb - 1:]
        high[high == 0] = np.nan
        low = data['low'].values[-lb - 1:]
        low[low == 0] = np.nan
        volume = data['volume'].values[-lb:]
        volume[volume == 0] = np.nan
        adj = data['adjfactor'].values[-lb - 1:]
        adj[adj == 0] = np.nan
        high = high * adj
        low = low * adj
        volume = volume / adj[-lb:]
        mid = (high + low) / 2
        mid_g = np.diff(mid, axis=0)
        hml = high[-lb:] - low[-lb:]
        emv = mid_g * hml * volume
        f = np.nanmean(np.nanmean(emv, axis=0))
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteBounceUpStdRatio_IF(FutureFactor):
    '''
    Description: max((close_000300.SH - cum_min(low_000300.SH)) / cum_min(low_000300.SH), 30) /
                 std(where(close_000300.SH > delay(close_000300.SH, 1), pct_chg(close_000300.SH, 1), 30))
    Class: Return_Risk
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_000300.SH'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        low = data['low_000300.SH'].values
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


class MinuteWilliamsR_IF(FutureFactor):
    '''
    Description: -(TodayHigh - close) / (TodayHigh - TodayLow)
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = {}
    data_dict['Continuous_Data'] = {'IF':['close', 'TodayHigh', 'TodayLow']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        f = -(data['TodayHigh_cont_IF'].values[-1] - data['close_cont_IF'].values[-1]) / (data['TodayHigh_cont_IF'].values[-1] - data['TodayLow_cont_IF'].values[-1])
        return f

##########
from future_factor import FutureFactor
import numpy as np


class  MinuteIndexUDRtnMeanDiff_IF(FutureFactor):
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

    
    normalize_size=237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close'].values
        open_ = data['open'].values

        rtn = close/open_-1
        rtn[np.isinf(rtn)] = np.nan
        up_rtn = np.nanmean(np.where(rtn>0,rtn, np.nan),axis=1)

        down_rtn = np.nanmean(np.where(rtn<0,rtn, np.nan),axis=1)
        factor= np.nanmean(up_rtn[-120:])+ np.nanmean(down_rtn[-120:])
            
        return factor

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowWeightReturnDiff_IF(FutureFactor):
    '''
    Description: ts_mean(cs_mean(rtn_high), 20) - ts_mean(cs_mean(rtn_low), 20),
                 rtn_high = pct_chg(close * adjfactor, 1)[:, weight[-1] > quantile(weight[-1], 0.8)],
                 rtn_low = pct_chg(close * adjfactor, 1)[:, weight[-1] < quantile(weight[-1], 0.2)].
    Class: Group_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        weight = data['weight'].values[-1]
        close = data['close'].values[-21:]
        close[close == 0] = np.nan
        adj = data['adjfactor'].values[-21:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        rtn_high = np.nanmean(rtn[:, weight > np.nanquantile(weight, 0.8)], axis=1)
        rtn_low = np.nanmean(rtn[:, weight < np.nanquantile(weight, 0.2)], axis=1)
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexOmega_IF(FutureFactor):
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexSharpeMean60_IF(FutureFactor):
    '''
    Description: cs_weighted_mean(ts_mean(rtn, 60) / ts_std(rtn, 60), w=weight),
                 rtn = pct_chg(close * adjfactor, 1).
    Class: MTM
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        weight = data['weight'].values[-1]
        close = data['close'].values[-lb - 1:]
        close[close == 0] = np.nan
        adj = data['adjfactor'].values[-lb - 1:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = close[1:] / close[:-1] - 1
        inf_nan_num = np.isnan(rtn).sum(axis=0) + np.isinf(rtn).sum(axis=0)
        rtn = rtn[:, inf_nan_num == 0]
        sharpe = np.nanmean(rtn, axis=0) / np.nanstd(rtn, axis=0)
        f = np.nansum(sharpe * weight[inf_nan_num == 0])
        return f

##########
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIFIHReturnDiff_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: 
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close'], '000016.SH':['close']}
    normalize_size = 40 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        close_if = data['close_000300.SH'].values
        close_ih = data['close_000016.SH'].values
        
        r_if = np.diff(close_if) / close_if[:-1]
        r_ih = np.diff(close_ih) / close_ih[:-1]

        N = 20
        f = np.nanmean(r_if[-N:]) - np.nanmean(r_ih[-N:])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighVolumeCorr_IF(FutureFactor):
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
        
        high = data['high'].values
        volume = data['volume'].values
        adjfactor = data['adjfactor'].values
        high_adj = high * adjfactor
        volume_adj = volume / adjfactor
        
        N = 60
        c = np.array([])
        for i in range(len(high_adj[-1])):
            c = np.append(c, np.corrcoef(high_adj[-N:,i], volume_adj[-N:,i])[0,1])
        
        f = np.abs(np.nanmean(c))
        
        return f
##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteIndexTSSkewSharpe_IF(FutureFactor):
    '''
    Description: cs_mean(ts_skew(pct_chg(close, 1), 30)) / cs_std(ts_skew(pct_chg(close, 1), 30))
    Class: Price_TS_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
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

class MinuteCloseTurnoverRatioCorrAbs_IF(FutureFactor):
    '''
    Description: abs(corr(close_000300.SH, amount_ratio, 60)),
                 amount_ratio =  / (the average amount_000300.SH at current time over past 5 trading days)
    Class: PV_Corr
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_000300.SH'].values
        close[close == 0] = np.nan
        turn = data['amount_000300.SH'].values
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

class MinuteIndexTradeMoneyRatioDiff_IF(FutureFactor):
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

        buy_sell_ratio = buy_trade_money / ask_amt - sell_trade_money / bid_amt
        buy_sell_ratio[np.isinf(buy_sell_ratio)] = np.nan

        factor_value = np.nanmean(np.nanmean(buy_sell_ratio[-n:]))

        return factor_value
##########
from future_factor import FutureFactor
import numpy as np


class  MinuteNetAmtRatio_IF(FutureFactor):
    '''
    Description: "(sum(where(pct_chg(ClosePx, 1) > rtn_mean + 2 * rtn_std, Turnover, 0), 120) - sum(where(pct_chg(ClosePx, 1) < rnt_mean - 2 * rtn_std, Turnover, 0), 120)) /
    (sum(where(pct_chg(ClosePx, 1) > rtn_mean + 2 * rtn_std, Turnover, 0), 120) + sum(where(pct_chg(ClosePx, 1) < rnt_mean - 2 * rtn_std, Turnover, 0), 120)),
    rtn_mean = mean(pct_chg(ClosePx, 1), 5days), rtn_std = std(pct_chg(ClosePx, 1), 5days) / (10 ** 0.5)"
    Class:MTM
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=6
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IF':['close','amount']}

    normalize_size=237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close_lastdays = data['close_cont_IF'].values[:240*5]
        amount_lastdays = data['amount_cont_IF'].values[:240*5]

        rtn_list_lastdays = close_lastdays[1:]/close_lastdays[:-1]-1
        rtn_mean = np.nanmean(rtn_list_lastdays)
        rtn_std = np.nanstd(rtn_list_lastdays)/np.sqrt(10)

        close = data['close_cont_IF'].values
        amount = data['amount_cont_IF'].values
        rtn_list= close[1:]/close[:-1]-1

        turnover_up_array = amount[-240:][rtn_list[-240:] > rtn_mean+2*rtn_std]
        turnover_down_array =amount[-240:][rtn_list[-240:] < rtn_mean-2*rtn_std]

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
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowAbsPxPathReturnDiff_IF(FutureFactor):
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownLimitNumDiff_IF(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 60
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

class MinuteIndexUpRatio_IF(FutureFactor):
    '''
    Description: ts_mean(cs_sum(pct_chg(close, 1) > 0), 20)
    Class: MTM
    Author: liuz, modified by jinpx
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor

        N = 30
        r = np.diff(close_adj[-N:], axis=0) / close_adj[-N:][:-1]
        up_num = np.sum(r>0, axis=1)
        f = np.nanmean(up_num)
            
        return f
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHighLowBuyRatio_IF(FutureFactor):
    '''
    Description: MA(ts_mean(where(close_000905.SH > quantile(close_000905.SH, 1/2, 30), buyratio, nan), 30)
                / ts_mean(where(close_000905.SH < quantile(close_000905.SH, 1/2, 30), buyratio, nan), 30), 5),
                buyratio = cs_mean(BuyTradeMoney / (BuyTradeMoney + SellTradeMoney))
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 30 * 237
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
            rank = bn.rankdata(close_temp)
            
            f = buy_sell_ratio[rank<=15].mean() / buy_sell_ratio[rank>15].mean()
            
            if np.isnan(f) or np.isinf(f):
                factor_temp_list.append(1)
            else:
                factor_temp_list.append(f)
                
        return np.mean(factor_temp_list)
##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexBidAskRtnStdRatio_IF(FutureFactor):
    '''
    Description: cs_weighted_mean((bid_std - ask_std) / (bid_std + ask_std), w=weight),
                 bid_std = ts_std(pct_chg(bid_price, 1), 10),
                 ask_std = ts_std(pct_chg(ask_price, 1), 10),
                 bid_price = (BidP0 * BidV0 + BidP1 * BidV1 + BidP2 * BidV2 + BidP3 * BidV3 + BidP4 * BidV4) / (BidV0 + BidV1 + BidV2 + BidV3 + BidV4) * adjfactor,
                 ask_price = (AskP0 * AskV0 + AskP1 * AskV1 + AskP2 * AskV2 + AskP3 * AskV3 + AskP4 * AskV4) / (AskV0 + AskV1 + AskV2 + AskV3 + AskV4) * adjfactor.
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4',
                         'BidP0', 'BidP1', 'BidP2', 'BidP3', 'BidP4', 'AskP0', 'AskP1', 'AskP2', 'AskP3', 'AskP4', 'adjfactor', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 11
        
        adj = data['adjfactor'].values[-lb:]
        weight = data['weight'].values[-1]
        
        bid_p = []
        bid_v = []
        ask_p = []
        ask_v = []
        
        for j in range(5):
            bid_p.append(data['BidP{}'.format(j)].values[-lb:])
            bid_v.append(data['BidV{}'.format(j)].values[-lb:])
            ask_p.append(data['AskP{}'.format(j)].values[-lb:])
            ask_v.append(data['AskV{}'.format(j)].values[-lb:])
            
        bid_p = np.array(bid_p)
        bid_p[bid_p == 0] = np.nan
        bid_v = np.array(bid_v)
        bid_v[bid_v == 0] = np.nan
        ask_p = np.array(ask_p)
        ask_p[ask_p == 0] = np.nan
        ask_v = np.array(ask_v)
        ask_v[ask_v == 0] = np.nan
        
        bid_p_mean = np.nansum(bid_p * bid_v, axis=0) / np.nansum(bid_v, axis=0) * adj
        bid_rtn = bid_p_mean[1:] / bid_p_mean[:-1] - 1
        
        ask_p_mean = np.nansum(ask_p * ask_v, axis=0) / np.nansum(ask_v, axis=0) * adj
        ask_rtn = ask_p_mean[1:] / ask_p_mean[:-1] - 1
        
        inf_nan_num = np.isnan(bid_rtn).sum(axis=0) + np.isinf(bid_rtn).sum(axis=0) + np.isnan(ask_rtn).sum(axis=0) + np.isinf(ask_rtn).sum(axis=0)
        bid_std = np.std(bid_rtn[:, inf_nan_num == 0], axis=0)
        ask_std = np.std(ask_rtn[:, inf_nan_num == 0], axis=0)
        f = np.nansum((bid_std - ask_std) / (bid_std + ask_std) * weight[inf_nan_num == 0])
        return f

##########
from future_factor import FutureFactor
import numpy as np


class  MinuteSignedRangeMean_IF(FutureFactor):
    '''
    Description: mean(where(ClosePx > OpenPx, HighPx / LowPx, -HighPx / LowPx), 120)
    Class:MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()

    data_dict['Index_Id'] = {'000300.SH': ['high', 'low','open', 'close']}
    normalize_size= 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        open_ = data['open_000300.SH'].values 
        close = data['close_000300.SH'].values 
        high = data['high_000300.SH'].values 
        low = data['low_000300.SH'].values 
        
        range_ =high/low
        sign = np.sign(close-open_)
        
        signed_range = (sign*range_)
        factor = np.nanmean(signed_range[-15:])
        return  factor

##########
import numpy as np
from future_factor import FutureFactor


class MinuteAccUpDownAmountRatio_IF(FutureFactor):
    
    def __init__(self):
        super().__init__()
        self.acc_up_amount = 0
        self.acc_down_amount = 0
        self.acc_up_amount_list = []
        self.acc_down_amount_list = []

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH': ['close', 'amount']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close = data['close_000300.SH'].values
        amount = data['amount_000300.SH'].values

        if close[-1] < close[-2]:
            self.acc_up_amount = amount[-1]
            self.acc_down_amount += amount[-1]
        else:
            self.acc_up_amount += amount[-1]
            self.acc_down_amount = amount[-1]

        self.acc_up_amount_list.append(self.acc_up_amount)
        self.acc_down_amount_list.append(self.acc_down_amount)

        factor_value = np.nanmean(np.array(self.acc_up_amount_list[-60:]) / np.array(self.acc_down_amount_list[-60:]))

        if np.isinf(factor_value):
            factor_value = 1

        return factor_value
##########
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverUniqueSellRatioDiff_IF(FutureFactor):
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
        rank_value = bn.rankdata((sign * arr),axis=axis)
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexCSSkewSharpe_IF(FutureFactor):
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
    normalize_size = 1 * 237
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
from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexUniqueBuyRatioMA10_IF(FutureFactor):
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
from scipy.stats import skew


class MinuteIndexOrderImbalanceSkew_IF(FutureFactor):
    '''
    Description: cs_mean(ts_skew((bid - ask) / (bid + ask), 30)),
                 bid = BidV0 + BidV1 + BidV2 + BidV3 + BidV4,
                 ask = AskV0 + AskV1 + AskV2 + AskV3 + AskV4.
    Class: Bid_Ask
    Author: hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        bid0 = data['BidV0'].values[-lb:]
        bid0[bid0 == 0] = np.nan
        bid1 = data['BidV1'].values[-lb:]
        bid1[bid1 == 0] = np.nan
        bid2 = data['BidV2'].values[-lb:]
        bid2[bid2 == 0] = np.nan
        bid3 = data['BidV3'].values[-lb:]
        bid3[bid3 == 0] = np.nan
        bid4 = data['BidV4'].values[-lb:]
        bid4[bid4 == 0] = np.nan
        ask0 = data['AskV0'].values[-lb:]
        ask0[ask0 == 0] = np.nan
        ask1 = data['AskV1'].values[-lb:]
        ask1[ask1 == 0] = np.nan
        ask2 = data['AskV2'].values[-lb:]
        ask2[ask2 == 0] = np.nan
        ask3 = data['AskV3'].values[-lb:]
        ask3[ask3 == 0] = np.nan
        ask4 = data['AskV4'].values[-lb:]
        ask4[ask4 == 0] = np.nan
        bid = bid0 + bid1 + bid2 + bid3 + bid4
        ask = ask0 + ask1 + ask2 + ask3 + ask4
        order_imbalance = (bid - ask) / (bid + ask)
        inf_nan_num = np.isinf(order_imbalance).sum(axis=0) + np.isnan(order_imbalance).sum(axis=0)
        order_imbalance = order_imbalance[:, inf_nan_num == 0]
        f = np.nanmean(skew(order_imbalance, axis=0))
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteStyleSharpeDiff237_IF(FutureFactor):
    '''
    Description: 2 * mean(rtn_300, 237) / std(rtn_300, 237) - mean(rtn_500, 237) / std(rtn_500, 237) - mean(rtn_50, 237) / std(rtn_50, 237),
                 rtn_300 = pct_chg(close_000300.SH, 1),
                 rtn_500 = pct_chg(close_000905.SH, 1),
                 rtn_50 = pct_chg(close_000016.SH, 1).
    Class: Multi-Variety
    Author: hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['close'], '000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 238
        price_sz = data['close_000016.SH'].values[-lb:]
        price_hs = data['close_000300.SH'].values[-lb:]
        price_zz = data['close_000905.SH'].values[-lb:]
        r_sz = (price_sz[1:] - price_sz[:-1]) / price_sz[:-1]
        r_hs = (price_hs[1:] - price_hs[:-1]) / price_hs[:-1]
        r_zz = (price_zz[1:] - price_zz[:-1]) / price_zz[:-1]
        f = 2 * np.nanmean(r_hs) / np.nanstd(r_hs) - np.nanmean(r_zz) / np.nanstd(r_zz) - np.nanmean(r_sz) / np.nanstd(r_sz)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteAmountRatioMean_IF(FutureFactor):
    '''
    Description: mean(amount_ratio, 20),
                 amount_ratio[i] = amount_000300.SH[i] / mean(amount_000300.SH[i - n * 237], n=1, 2, ..., 5).
    Class: Liquidity
    Author: hefj
    '''
    data_type = 'Future'
    days_past = 7
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['amount']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        amount = data['amount_000300.SH'].values[-6 * 237:].reshape(6, -1)
        amount_ratio = amount[-1] / np.nanmean(amount[:-1], axis=0)
        f = np.mean(amount_ratio[-20:])
        return f

##########
import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteResidualRtnSkew_IF(FutureFactor):
    '''
    Description: skew(residual_return, 30),
                residual_return = close_000300.SH / predicted_price - 1,
                predicted_price = linear_regression(x=range(1, 31), y=close_000300.SH[-30:], intercept=True).predict(x=range(1, 31))
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_000300.SH'].values
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
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowBetaRtnDiff_IF(FutureFactor):
    data_type = 'IndexStock'
    days_past = 6
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000300.SH': ['close']}
    normalize_size = 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 5 * 237
        adj = data['adjfactor'].values
        close = (data['close'].values * adj / adj[-1])[-lb - 1:]
        rtn = close[1:] / close[:-1] - 1
        zero_num = (np.abs(rtn) < 1 / 10000).sum(axis=0)
        rtn = rtn[:, zero_num < (lb / 2)]
        
        index_close = data['close_000300.SH'].values[-lb - 1:]
        index_close = index_close.reshape(len(index_close), -1)
        index_rtn = index_close[1:] / index_close[:-1] - 1
        
        beta = np.mean((rtn - np.mean(rtn, axis=0)) * (index_rtn - np.mean(index_rtn)), axis=0) / np.var(index_rtn)
        median = np.nanmedian(beta)
        
        rtn_high = rtn[:, beta > median]
        rtn_low = rtn[:, beta <= median]
        
        f = np.nanmean(rtn_high) - np.nanmean(rtn_low)
        return f

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHighLowTurnoverRateReturnDiff_IF(FutureFactor):
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
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk

class MinuteIndexVolatilityLongShortReturnDiff_IF(FutureFactor):
    
    data_type = 'IndexStock'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close']
    normalize_size = 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        lb_long = 237*5
        lb_short = 120
        close =  data['close'].values 

        rtn = close[1:]/close[:-1]-1
        volatility = np.nanstd(rtn[-lb_long:],axis=0)

        close_rtn_short = close[-1] / close[-lb_short] - 1

        close_rtn_long_rank =  bk.rankdata(volatility)/len(volatility)

        factor = np.nanmean(close_rtn_short[close_rtn_long_rank>=0.5])-np.nanmean(close_rtn_short[close_rtn_long_rank<=0.5])

        return factor
##########
from future_factor import FutureFactor
import numpy as np


class MinuteStyleSharpeDiff30_IF(FutureFactor):
    '''
    Description: mean(rtn_300 - rtn_500, 30) / std(rtn_300 - rtn_500, 30) + mean(rtn_300 - rtn_50, 30) / std(rtn_300 - rtn_50, 30),
                 rtn_300 = pct_chg(close_000300.SH, 1),
                 rtn_500 = pct_chg(close_000905.SH, 1),
                 rtn_50 = pct_chg(close_000016.SH, 1).
    Class: Multi-Variety
    Author: hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['close'], '000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 31
        price_sz = data['close_000016.SH'].values[-lb:]
        price_hs = data['close_000300.SH'].values[-lb:]
        price_zz = data['close_000905.SH'].values[-lb:]
        r_sz = (price_sz[1:] - price_sz[:-1]) / price_sz[:-1]
        r_hs = (price_hs[1:] - price_hs[:-1]) / price_hs[:-1]
        r_zz = (price_zz[1:] - price_zz[:-1]) / price_zz[:-1]
        f = np.nanmean(r_hs - r_zz) / np.nanstd(r_hs - r_zz) + np.nanmean(r_hs - r_sz) / np.nanstd(r_hs - r_sz)
        return f

##########
from future_factor import FutureFactor
import numpy as np


class  MinuteMACDPriceCorr_IF(FutureFactor):
    '''

'''
    data_type='Future'
    instrument_type='recent'
    days_past= 3
    data_dict=dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}

    
    normalize_size= 120
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        
        def ewma_vectorized(data, alpha, offset=None, dtype=None, order='C', out=None):
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
        
        def MACD(close):

            window_short = 12
            window_long = 26
            window_mid = 9

            ema_short = ewma_vectorized(close, 2/(window_short+1))
            ema_long = ewma_vectorized(close, 2/(window_long+1))
            dif = ema_short[-(len(close)-window_long):] - ema_long[-(len(close)-window_long):]
            dea = ewma_vectorized(dif, 2/(window_mid+1))

            macd = dif[-(len(dif)-window_mid):] - dea[-(len(dif)-window_mid):]

            return macd
        
        lb = 10
        index_close = data['close_000300.SH'].values

        macdhist = MACD(index_close)

        
        factor = np.corrcoef(macdhist[-lb:], index_close[-lb:])[0][1]
                
        return factor
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioAutoCorrSharpe_IF(FutureFactor):
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
    normalize_size = 20 * 237
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
from future_factor import FutureFactor
import numpy as np


class  MinuteIndexHighBetaRtn_IF(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000300.SH':['close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        index_close = data['close_000300.SH'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values

        close_adj = close*adjfactor
        rtn = close_adj[1:]/close_adj[:-1]-1

        index_rtn = index_close[1:] / index_close[:-1] - 1

        rtn[np.isinf(rtn)] = np.nan
        index_rtn[np.isinf(index_rtn)] = np.nan

        adj_rtn_237 = rtn[-120:]
        index_rtn_237 = index_rtn[-120:]
        adj_rtn_30 = rtn[-30:] 
        cov_matrix = np.cov(adj_rtn_237.T,index_rtn_237.reshape(120,-1).T)
        cov_rtn = cov_matrix[-1][:-1]
        index_rtn_std = np.nanstd(index_rtn_237)

        beta = cov_rtn / np.power(index_rtn_std,2)
        factor = np.nanmean(np.nanmean(adj_rtn_30[:,beta > 3],axis=0))

        if np.isnan(factor):
            factor = 0
            
            
        return factor

##########
from future_factor import FutureFactor
import numpy as np


class  MinuteIndexObLevelsDiff_IF(FutureFactor):
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

        factor = np.nanmean(np.nanmean((bid_levels-ask_levels)[-120:],axis=0))
        
        return factor

##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexCorrWeightedReturn_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        stk_index_corr_hs300 = data['stk_index_corr_hs300'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[-1]
        
        f = np.nanmean(np.nansum(r[-1185:], axis=0) * stk_index_corr_hs300[-1])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteLongTermDistance2Rtn_IF(FutureFactor):
    '''
    Description: Sum(r, 240) / Sum(Abs(r), 240)
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000300.SH'].values
        index_high = data['high_000300.SH'].values
        index_low = data['low_000300.SH'].values
        index_typical = index_close + index_high + index_low
        index_typical_r = np.diff(index_typical) / index_typical[:-1]
        
        N = 237
        f = np.sum(index_typical_r[-N:]) / np.sum(np.abs(index_typical_r[-N:]))

        return f
##########
from future_factor import FutureFactor
import numpy as np


class MinuteAllIndexTurnoverShrinkReturn_IF(FutureFactor):
    '''
    Description: "mean(where((index_turnover_ratio_IC < shift(index_turnover_ratio_IC, 1)) & (index_turnover_ratio_IF < shift(index_turnover_ratio_IF, 1)
                    & (index_turnover_ratio_IH < shift(index_turnover_ratio_IH, 1), pct_chg(Index_ClosePx, 1), nan), 45),
                    index_turnover_ratio = Index_Turnover / (the average Index_Turnover at current time over past 5 trading days)"
    Class: PV_Corr
    Author: jinpx  modeified by liuz
    '''    
    data_type='Future'
    instrument_type='recent'
    days_past=8
    data_dict=dict()
    data_dict['Index_Id'] = {'000300.SH':['close','amount'],'000905.SH':['amount'],'000016.SH':['amount']}

    normalize_size= 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        IF_close = data['close_000300.SH'].values
        IC_amt = data['amount_000905.SH'].values
        IF_amt = data['amount_000300.SH'].values
        IH_amt = data['amount_000016.SH'].values

        r_IF = np.diff(IF_close) / IF_close[:-1]
        IC_turnover_ratio = IC_amt[-237:] / np.nanmean(IC_amt[-1422:-237].reshape(5, 237), axis=0)
        IF_turnover_ratio = IF_amt[-237:] / np.nanmean(IF_amt[-1422:-237].reshape(5, 237), axis=0)
        IH_turnover_ratio = IH_amt[-237:] / np.nanmean(IH_amt[-1422:-237].reshape(5, 237), axis=0)

        N = 60
        f = np.nanmean(r_IF[-N:][np.logical_and.reduce([np.diff(IC_turnover_ratio)[-N:]<0, np.diff(IF_turnover_ratio)[-N:]<0, np.diff(IH_turnover_ratio)[-N:]<0])])
        return f

##########
from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowStdRtnDiff_IF(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 120
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
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class MinuteIndexHLTurnoverRateUniqueSellRatioDiff_IF(FutureFactor):
    '''
    Description: mean(ratio(rank > 0.8)) - mean(ratio(rank < 0.2)),
                 ratio = -1 * mean(SellTradeNum / SellUniqueOrderNum, 20)
                 rank = rank(mean(turnover_rate, 60))
    Class: Group_Stat
    Author: lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum','SellTradeNum','turnover_rate']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n1 = 20
        n2 = 60
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
from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute60_10Speed_IF(FutureFactor):
    '''
    Description: pct_chg(ema(ClosePx, 60), 10)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = int(1 * 237)
    normalize_type = 'ts_rank'

    def __init__(self):
        super().__init__()
        self.ema_list = []

    def calculate(self, data):
        close = data['close_cont_IF'].values
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
        rank_value = (sign * arr).argsort(axis=axis).argsort(axis=axis) + 1
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
import numpy as np
from future_factor import FutureFactor

class MinuteIndexTotalAskBidVolSum_IF(FutureFactor):
    '''
    Description: TotalAskVol / (Mean of TotalAskVol during past 5 days at the same minute) + TotalBidVol / (Mean of TotalBidVol during past 5 days at the same minute)
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['TotalAskVol', 'TotalBidVol']
    normalize_size = 60 
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        TotalAskVol = data['TotalAskVol'].values
        TotalBidVol = data['TotalBidVol'].values
        
        TotalAskVol_ratio = TotalAskVol[-237:] / np.nanmean(TotalAskVol[-1422:-237].reshape(5, 237, len(TotalAskVol[0])), axis=0)
        TotalBidVol_ratio = TotalBidVol[-237:] / np.nanmean(TotalBidVol[-1422:-237].reshape(5, 237, len(TotalBidVol[0])), axis=0)
        
        f = np.nansum(TotalAskVol_ratio[-1]) + np.nansum(TotalBidVol_ratio[-1])
        
        return f
##########
import numpy as np
from future_factor import FutureFactor

class MinuteIndexMoneyUniqueConsistency_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BuyTradeMoney = data['BuyTradeMoney'].values
        SellTradeMoney = data['SellTradeMoney'].values
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values 
        
        N = 30
        BuyMoneyPerTrade_new = np.nansum(BuyTradeMoney[-N:], axis=0) / np.nansum(BuyUniqueOrderNum[-N:], axis=0)
        BuyMoneyPerTrade_old = np.nansum(BuyTradeMoney[-2*N:-N], axis=0) / np.nansum(BuyUniqueOrderNum[-2*N:-N], axis=0)
        BuyUniqueOrderNum_new = np.nansum(BuyUniqueOrderNum[-N:], axis=0)
        BuyUniqueOrderNum_old = np.nansum(BuyUniqueOrderNum[-2*N:-N], axis=0)
        
        up_num = np.nansum(np.logical_and(BuyMoneyPerTrade_new>BuyMoneyPerTrade_old, BuyUniqueOrderNum_new>BuyUniqueOrderNum_old))
        down_num = np.nansum(np.logical_and(BuyMoneyPerTrade_new<BuyMoneyPerTrade_old, BuyUniqueOrderNum_new<BuyUniqueOrderNum_old))
        
        f = up_num - down_num
        
        return f
##########
