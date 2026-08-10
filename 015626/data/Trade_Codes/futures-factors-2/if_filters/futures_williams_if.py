from future_factor import FutureFactor
from operators_wsc_for_srch import *


class futures_williams_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF': ['vwap']} 
    normalize_size = 0
    normalize_type = 'ts_rank' 

    def calculate(self, df):
        vwap = df['vwap_cont_IF']
        h_intraday = vwap.groupby(vwap.index.date).apply(lambda x: x.expanding().max())
        l_intraday = vwap.groupby(vwap.index.date).apply(lambda x: x.expanding().min())
        williams = (2 * vwap - h_intraday - l_intraday) / (h_intraday - l_intraday)
        return williams.iloc[-1]
