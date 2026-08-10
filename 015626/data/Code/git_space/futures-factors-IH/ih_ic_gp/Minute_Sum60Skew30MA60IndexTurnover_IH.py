from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_Sum60Skew30MA60IndexTurnover_IH(FutureFactor):
    '''
    Description: Sum_60(Skew_30(MA_60(Index_Turnover)))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH': ['amount']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        turnover_ma_60 = bn.move_mean(data['amount_000016.SH'].values, 60)
        turnover_ma_60[np.isnan(turnover_ma_60)] = 0

        rolling_mean = bn.move_mean(turnover_ma_60, 30)
        # Skew_Bias = True, which equals scipy.stats.skew(a) or standard skew formula
        skew_30 = (pd.Series(turnover_ma_60).rolling(30).skew() * (30 - 2) / np.sqrt((30 - 1) * 30)).fillna(0).values

        factor_value = np.nansum(skew_30[-60:])

        if np.isnan(factor_value):
            factor_value = 0

        return factor_value