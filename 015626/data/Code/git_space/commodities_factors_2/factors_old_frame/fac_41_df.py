import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# td
class fac_41_df(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'main_mask']

        super(fac_41_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        aaa = 2
        bbb = 90
        ccc = 2
        ddd = 10

        mask = data['main_mask']
        if aaa == bbb:
            factor = data['high'][mask].mean(axis = 1).to_frame()
        else:
            #temp1 = data['low'].rolling(aaa, min_periods = 1).min()-data['low'].rolling(bbb, min_periods = 1).min()
            temp2 = data['high'].rolling(aaa, min_periods = 1).max() - data['high'].rolling(bbb, min_periods = 1).max()
            vol = data['high'].diff().rolling(60, min_periods = 5).std()[mask].mean(axis = 1)
            factor = (temp2)[mask].mean(axis = 1)       
            factor = ts_rank((factor).rolling(int(ccc), min_periods = 1).mean() * r(np.sqrt(vol)), ddd * 300).to_frame()
            factor.columns = [self.__class__.__name__]
        return factor
