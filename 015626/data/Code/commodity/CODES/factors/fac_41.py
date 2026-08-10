import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# td
class fac_41(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high']

        super(fac_41, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):

        temp1 = data['low'].rolling(aaa, min_periods = 1).min()-data['low'].rolling(bbb, min_periods = 1).min()
        temp2 = data['high'].rolling(aaa, min_periods = 1).max()-data['high'].rolling(bbb, min_periods = 1).max()
        temp = temp1 + temp2
        factor = temp.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc * 300)


        return factor
