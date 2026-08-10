from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k11_doublelow_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close', 'close_stk', 'CB_ANAL_CONVPRICE']
        super(wyc_k11_doublelow_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # 双低策略因子
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
        conv_premium = kzz_close - conv_value # 转股溢价
        conv_premium_ratio = conv_premium / conv_value # 转股溢价率

        conv_premium_ratio_1449 = conv_premium_ratio.between_time(data_morning_begin, trade_stop_time)
        conv_premium_ratio_1449 = conv_premium_ratio_1449.groupby(conv_premium_ratio_1449.index.date).last()
        conv_premium_ratio_1449.index = pd.to_datetime(conv_premium_ratio_1449.index) # 14点49分的转股溢价率

        close_1449 = df['close'][clist].between_time(data_morning_begin, trade_stop_time)
        close_1449 = close_1449.groupby(close_1449.index.date).last()
        close_1449.index = pd.to_datetime(close_1449.index)

        factor = close_1449 + conv_premium_ratio_1449 * 100
        factor = factor.rank(axis = 1, pct = True)
        factor = abs(factor - 0.5)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor