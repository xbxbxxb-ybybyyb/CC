import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from rolling_adj import *
# td
class fac_41_5min_df(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'main_mask', 'close']

        super(fac_41_5min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        aaa = 2
        bbb = 150
        ccc = 10
        ddd = 10

        mask = data['main_mask']
        hclose = data['close'][mask].mean(axis = 1)
        #temp1 = data['low'].rolling(aaa, min_periods = 1).min()-data['low'].rolling(bbb, min_periods = 1).min()
        temp2 = data['high'].rolling(aaa, min_periods = 1).max() - data['high'].rolling(bbb, min_periods = 1).max()
        factor = (temp2)[mask].mean(axis = 1)      
        factor = irr_ma(factor, ccc)
        factor = ts_rank(factor, ddd * 300)
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        cs = factor.rolling(int(coef), min_periods = 5).corr(hclose)
        cl = factor.rolling(int(coef * 5) ,min_periods = 5).corr(hclose)
        factor[(cs <cl) | (cl < 0)] = 0
        factor = factor.to_frame()
        factor.columns = [self.__class__.__name__]
        return factor
