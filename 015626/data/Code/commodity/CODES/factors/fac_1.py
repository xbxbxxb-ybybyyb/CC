import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *

def calc_atr(h,l,c,window):
    TR_df = pd.DataFrame(columns = ['H-L','H-C', 'L-C'])
    TR_df['H-L'] = h-l
    TR_df['H-C'] = abs(h-c.shift(1))
    TR_df['L-C'] = abs(l-c.shift(1))
    TR = TR_df.max(axis=1)
    ATR = TR.rolling(window).mean()
    return ATR

def calc_rwi(h,l,c,window):
    atr = calc_atr(h,l,c,window)
    rwi_high = (h - l.rolling(window).min())/atr
    rwi_low = (h.rolling(window).max() - l)/atr
    return rwi_high, rwi_low


class fac_1(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low']

        super(fac_1, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, i_data, a = 30, b = 10 ,c = 5):

        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']
        
        rwi_high, rwi_low = calc_rwi(spot_h, spot_l, spot_c,a)
        rwi_fac = ((rwi_high-rwi_low)/r((rwi_high+rwi_low)).rolling(b).mean())
        factor = ts_rank(rwi_fac, c * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor