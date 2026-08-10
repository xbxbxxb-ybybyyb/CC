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
    instrument_type='main'
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
