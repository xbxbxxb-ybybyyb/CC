import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *


class fac_8(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low', 'open']

        super(fac_8, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):

        temp_df = pd.concat([data['open'], data['close']], axis = 1)
        temp1 = temp_df.max(axis = 1)
        temp2 = temp_df.min(axis = 1)
        t_pcor = (data['high']-temp1)/(data['high'] - temp1).rolling(aaa, min_periods = 1).mean()
        t_pcor2 = (data['close']-data['low'].rolling(aaa, min_periods = 1).min())/r(data['high'].rolling(aaa, min_periods = 1).max()-data['low'].rolling(aaa, min_periods = 1).min())
        t_pcorr = (t_pcor2 - t_pcor).rolling(bbb, min_periods = 1).mean()
        factor = t_pcorr.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 300 * ccc)
        return factor
