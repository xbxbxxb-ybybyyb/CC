from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k210_multimean_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k210_multimean_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].copy()
        mm5 = ts_mean(close, 5).between_time(data_morning_begin, trade_stop_time)
        mm10 = ts_mean(close, 10).between_time(data_morning_begin, trade_stop_time)
        mm20 = ts_mean(close, 20).between_time(data_morning_begin, trade_stop_time)
        mm30 = ts_mean(close, 30).between_time(data_morning_begin, trade_stop_time)
        mm60 = ts_mean(close, 60).between_time(data_morning_begin, trade_stop_time)
        mm120 = ts_mean(close, 120).between_time(data_morning_begin, trade_stop_time)
        mm240 = ts_mean(close, 240).between_time(data_morning_begin, trade_stop_time)
        close = close.between_time(data_morning_begin, trade_stop_time)

        mm5 = mm5.groupby(mm5.index.date).last()
        mm10 = mm10.groupby(mm10.index.date).last()
        mm20 = mm20.groupby(mm20.index.date).last()
        mm30 = mm30.groupby(mm30.index.date).last()
        mm60 = mm60.groupby(mm60.index.date).last()
        mm120 = mm120.groupby(mm120.index.date).last()
        mm240 = mm240.groupby(mm240.index.date).last()
        close = close.groupby(close.index.date).last()

        factor = (mm5  > close).astype('int').replace(0,-1) + (mm10 > mm5).astype('int').replace(0,-1) + (mm20 > mm10).astype('int').replace(0,-1) + (mm30 > mm20).astype('int').replace(0,-1)
        + (mm60 > mm30).astype('int').replace(0,-1) + (mm120 > mm60).astype('int').replace(0,-1) + (mm240 > mm120).astype('int').replace(0,-1)
        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor