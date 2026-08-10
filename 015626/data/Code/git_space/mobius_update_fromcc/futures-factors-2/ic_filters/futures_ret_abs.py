from future_factor import FutureFactor
from operators_wsc_for_srch import *


class futures_ret_abs(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC': ['vwap']} 
    normalize_size = 0
    normalize_type = 'ts_rank' 

    def calculate(self, df):
        vwap = df['vwap_cont_IC']
        ret = vwap.groupby(vwap.index.date).apply(lambda x: x.pct_change(1))
        ret_abs = ret.abs().rolling(240, min_periods=1).mean()
        return ret_abs.iloc[-1]
