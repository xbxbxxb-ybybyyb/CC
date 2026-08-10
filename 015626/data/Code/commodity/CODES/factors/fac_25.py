import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# ERET_CC_IF
class fac_25(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume']

        super(fac_25, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, i_data, aa, bb, ccc, dd):

        ret = i_data['close'] - i_data['close'].shift(aa)
        ret_std = i_data['close'].diff().rolling(bb, min_periods = 1).std()

        ret_weight = ret * ret_std * (i_data['volume'].rolling(aa, min_periods = 2).mean())
        factor = ret_weight.rolling(ccc, min_periods = 1).mean()#[i_data['main_mask']].sum(axis = 1)
        #factor = ts_rank(factor, 2400)
        
        factor = ts_rank(factor, dd * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor