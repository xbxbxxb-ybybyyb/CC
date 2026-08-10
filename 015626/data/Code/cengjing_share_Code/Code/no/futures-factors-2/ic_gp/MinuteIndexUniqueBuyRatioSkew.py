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
        try:
            BuyTradeNum = data['BuyTradeNum'].values
            BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
            df_buy_unique_ratio = BuyUniqueOrderNum / BuyTradeNum
            s = skew(df_buy_unique_ratio[-5:],axis=1,nan_policy='omit',bias=False)

            factor = np.nanmean(np.array(s))
        except:
            factor = np.nan
        return factor


