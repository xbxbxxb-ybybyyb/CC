import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# 
class fac_24(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close']

        super(fac_24, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb):
        t_pcor = pd.concat([data['high'], data['close']], axis = 1)
        t_pcor2 =  t_pcor.rolling(aa, min_periods = 1).corr(pairwise=True).unstack()
        t_pcor2 = t_pcor2[('high', 'close')]
        t_pcor2[t_pcor2 == np.inf] = 0
        factor = t_pcor2 * (data['close'].diff(aa))

        
        factor = ts_rank(factor, bb * 300).to_frame() 
        factor.columns = [self.__class__.__name__]
        return factor
