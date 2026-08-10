from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k29_cstd_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k29_cstd_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        factor = abs(close / ts_mean(close, 20) - 1)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
        # 因子开发时保存因子错误，保存成k28了
        # close = df['close'].between_time(data_morning_begin, trade_stop_time)
        # close = close.groupby(close.index.date).last()
        # close.index = pd.to_datetime(close.index)

        # N = 30
        # factor = ts_std(close, N)
        # factor = factor.replace([np.inf, -np.inf], np.nan)

        # factor = factor.iloc[-1].to_frame()
        # columnname = self.__class__.__name__
        # factor.columns = [columnname]
        # return factor