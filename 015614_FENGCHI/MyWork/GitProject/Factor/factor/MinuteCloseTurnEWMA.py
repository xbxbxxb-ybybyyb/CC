from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseTurnEWMA(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']

        a_ma = a.iloc[-5:].mean() / a.iloc[-30:].mean()
        c_ma = c.iloc[-5:].mean() / c.iloc[-30:].mean()
        
        if a.index[-1].strftime('%Y%m%d') in ['20160104', '20160107']:
            a_ma = a.iloc[-245:].mean() / a.iloc[-270:].mean()
            c_ma = c.iloc[-245:].mean() / c.iloc[-270:].mean()

        a_ma_norm = (a_ma - a_ma.min()) / (a_ma.max() - a_ma.min())
        c_ma_norm = (c_ma - c_ma.min()) / (c_ma.max() - c_ma.min())

        return -1 * a_ma_norm * c_ma_norm
    
    def reform(self, temp):
        return temp.ewm(span=2).mean()