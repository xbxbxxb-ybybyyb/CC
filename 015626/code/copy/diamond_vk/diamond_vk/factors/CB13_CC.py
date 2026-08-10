from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB13_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB13_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        high = df['close'][-500:] / df['open'][-500:]
        close = df['close_stk'][-500:] / df['open_stk'][-500:]
        s = ts_std(high, 120)
        f = ts_std(close, 120)
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(120, min_periods=30).cov(close) / (s * f)

        factor = t_pcor2.between_time(datetime.time(13, 0), trade_stop_time)
        factor = factor.groupby(factor.index.date).mean()
        factor = factor.replace([-np.inf, np.inf], np.nan)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor