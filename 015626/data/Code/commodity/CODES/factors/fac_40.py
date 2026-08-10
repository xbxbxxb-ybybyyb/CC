import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# SYXWR
class fac_40(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low', 'high', 'open']

        super(fac_40, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):

        temp1 = pd.Series(np.where(data['open']>data['close'], data['open'], data['close']))
        temp2 = pd.Series(np.where(data['open']>data['close'], data['close'], data['open']))
        temp1.index = data['close'].index
        temp2.index = data['close'].index
        t_pcor = (data['high']-temp1)/r((data['high'] - temp1).rolling(aaa, min_periods = 1).mean())
        t_pcor2 = (data['close']-data['low'].rolling(aaa, min_periods = 1).min())/r(data['high'].rolling(aaa, min_periods = 1).max()-data['low'].rolling(aaa, min_periods = 1).min())
        t_pcorr = (t_pcor2 - t_pcor).rolling(bbb, min_periods = 1).mean()
        factor = t_pcorr.to_frame()
        
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc * 300)
        return factor
