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
    data_dict['Future_Data'] = ['AskP0', 'BidP0', 'interest']
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        bid_p_0 = data['BidP0'].values[-n:]
        ask_p_0 = data['AskP0'].values[-n:]
        interest = data['interest'].values[-n:]

        spread = (ask_p_0 - bid_p_0) / (ask_p_0 + bid_p_0)

        factor_value = -np.corrcoef(interest, spread)[0, 1]

        if np.isinf(factor_value) or np.isnan(factor_value):
            factor_value = 0

        return factor_value