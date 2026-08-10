from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_ar_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','amount_zz500']
        lookback_bars=2000
        super(wyc_ts419_ar_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * (2 * df['amount_zz500'].rank(axis=1, pct=True) - 1)

        factor = factor.sum(axis=1).to_frame()
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 5 * 242)

        factor[factor < -0.5] = 0

        return factor

from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_ar_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[-0.5,1]'
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-60:]
        low = df['low_preadj'][-60:]
        high = df['high_preadj'][-60:]
        volume = df['volume_preadj'][-60:]
        
        amount = df['amount'][-20:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-50:]
        finaldf = bk.move_mean(factor, 30, 15, axis = 0)[-20:]

        factor = finaldf * (2 * amount.rank(axis=1, pct=True).values - 1)

        factor = np.nansum(factor, axis=1)
        factor = np.nanmean(factor)

        return factor

from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def ts_sum(A,d):
    # time-series sum over the past d days
    output = A.rolling(d,min_periods=int(round(d/2))).sum()
    output.iloc[:d-1] = np.nan
    return output

def ts_mean(A, d):
    # moving time-series average for the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_mean(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output

class wyc_ts419_ar_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[-0.5,1]'
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-80:]
        low = df['low_preadj'][-80:]
        high = df['high_preadj'][-80:]
        volume = df['volume_preadj'][-80:]
        
        amount = df['amount'][-80:]
        
        factor = ts_sum(((close - low) - (high - close)) / (high - low) * volume, 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * (2 * amount.rank(axis=1, pct=True) - 1)

        factor = factor.sum(axis=1).to_frame()
        factor = ts_mean(factor, 20)

        return factor.values[-1]