from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k12_convvalue_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','close_stk','CB_ANAL_CONVPRICE']
        super(wyc_k12_convvalue_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        conv = df['CB_ANAL_CONVPRICE'] # 转股价
        kzz_close = df['close']
        clist = list(set(kzz_close.columns) & set(conv.columns))
        clist.sort()
        conv = conv[clist]
        kzz_close = kzz_close[clist]
        stk_close = df['close_stk'][clist]
        conv_minute = conv.reindex(kzz_close.index, method='pad') # 转股价reindex到分钟

        conv_minute = conv_minute.replace(0, np.nan)
        conv_value = 100 * stk_close / conv_minute # 转股价值

        factor = conv_value.between_time(data_morning_begin, trade_stop_time)
        factor = factor.groupby(factor.index.date).last()
        factor.index = pd.to_datetime(factor.index) # 14点49分的转股溢价
        factor = factor.replace([np.inf, -np.inf], np.nan)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor