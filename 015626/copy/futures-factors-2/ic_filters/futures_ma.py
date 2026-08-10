from future_factor import FutureFactor
from operators_wsc_for_srch import *


class futures_ma(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC': ['vwap']} 
    normalize_size = 0
    normalize_type = 'ts_rank' 

    def calculate(self, df):
        vwap = df['vwap_cont_IC']
        ma10 = vwap.groupby(vwap.index.date).apply(lambda x: x.rolling(10, min_periods=1).mean())
        ma30 = vwap.groupby(vwap.index.date).apply(lambda x: x.rolling(30, min_periods=1).mean())
        diff = ma10 - ma30
        return diff.iloc[-1]
