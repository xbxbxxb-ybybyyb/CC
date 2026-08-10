import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, rolling_norm
import bottleneck as bk

def ts_mean2(data, d, min_periods = 1):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if (d == 1) or (len(data) < d):
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=min_periods, axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=min_periods, axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=min_periods, axis=0),
                               index=data.index, name=data.name)
    return output

# 
class fac_15(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'tday']

        super(fac_15, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb):
 
        spot_if = data['close']

        
        spot_ma_intraday = spot_if.groupby(data['tday']).apply(lambda x: ts_mean2(x, len(x), 1))
        spot_ma_5_intraday = spot_if.groupby(data['tday']).apply(lambda x: ts_mean2(x, int(np.sqrt(aaa)), 1))
        temp = (spot_ma_5_intraday - spot_ma_intraday)

        factor = ts_rank(temp, bbb * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return -factor