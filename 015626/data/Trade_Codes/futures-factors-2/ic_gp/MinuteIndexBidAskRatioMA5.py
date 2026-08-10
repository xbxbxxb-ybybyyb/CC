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

