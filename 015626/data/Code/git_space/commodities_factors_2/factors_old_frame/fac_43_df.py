import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num

# ulb_zscore_ma
class fac_43_df(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'main_mask']

        super(fac_43_df, self).__init__(required_columns=required_columns
                                  )
        
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        
        close = data['close'].copy()#.rolling(2, min_periods = 1).mean()
        high = data['high'].rolling(2, min_periods = 1).max()
        low = data['low'].rolling(2, min_periods = 1).min()
        mask = data['main_mask'].copy()
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        
        ##### calc factor #####
        def calc_ulb_zscore(close, high, low, roll_win=20, min_pct=0.9):
            upper = SMA(high, roll_win, 1)
            lower = SMA(low, roll_win, 1)
            ulb = upper - lower
            ulb_avg = ulb.rolling(roll_win, int(roll_win * min_pct)).mean()
            ulb_std = ulb.rolling(roll_win, int(roll_win * min_pct)).std()
            mid = (upper + lower) / 2
            ulb_zscore = ((close - mid) - ulb_avg) / ulb_std
            return ulb_zscore

        """ulb_zscore_ma"""
        factor_name = 'ulb_zscore_ma'
        roll_win = 10
        ma_win = 4
        ts_pct_win = 1500
        score_raw = calc_ulb_zscore(close, high, low, roll_win)[mask].mean(axis = 1)
        score_raw = score_raw.rolling(ma_win, min_periods = 1).mean()
        vol = cross_hub_num(data['close'], 10)[mask].mean(axis = 1) + 1
        
        ulb_zscore_ma = ts_rank(score_raw / r(vol), ts_pct_win)
        ##### format factor #####
        ulb_zscore_ma.name = self.__class__.__name__
        factor = pd.DataFrame(ulb_zscore_ma)
        return factor