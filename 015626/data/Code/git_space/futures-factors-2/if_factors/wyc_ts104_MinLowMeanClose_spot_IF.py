from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

def ts_rank(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
    return output
    
class wyc_ts104_MinLowMeanClose_spot_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'low']} 
    normalize_size = 1000
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        low = data['low_000300.SH'].values[-155:]
        close = data['close_000300.SH'].values[-155:]
        
        r = bk.move_min(low, 30, 15) / bk.move_mean(close, 15, 7)
        factor = ts_rank(r[-125:], 120)
        factor = np.nanmean(factor[-5:]) * -1
        
        return factor