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
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['amount']
    data_dict['Index_Id'] = {'000905.SH': ['amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        index_amount = data['amount_000905.SH'].values
        amount = data['amount'].values

        index_amount[index_amount == 0] = np.nan
        amount[amount == 0] = np.nan

        mean_ratio = np.nanmean(index_amount) / np.nanmean(amount)

        factor_value = 0 if (np.isnan(mean_ratio) or np.isinf(mean_ratio)) else mean_ratio

        return factor_value