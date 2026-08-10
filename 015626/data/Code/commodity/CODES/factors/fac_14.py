import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *

def ts_max(data, d, mc = 1):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=mc, axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=mc, axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=mc, axis=0),
                               index=data.index, name=data.name)
    return output

def ts_min(data, d, mc = 1):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_min(data, window=d, min_count=mc, axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_min(data, window=d, min_count=mc, axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_min(data, window=d, min_count=mc, axis=0),
                               index=data.index, name=data.name)
    return output


#MinuteWilliamR
class fac_14(FactorGenerator):
    def __init__(self):
        required_columns=['close','low', 'high', 'tday']

        super(fac_14, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, ccc):
 
        spot_h = data['high']
        spot_l = data['low']
        spot_c = data['close']

        today_high  = data['high'].groupby(data['tday']).apply(lambda x: ts_max(x, len(x), 1))
        today_low  = data['low'].groupby(data['tday']).apply(lambda x: ts_min(x, len(x), 1))

        factor = -(today_high - data['close']) / r(today_high - today_low)
        factor = ts_rank(factor, ccc * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor