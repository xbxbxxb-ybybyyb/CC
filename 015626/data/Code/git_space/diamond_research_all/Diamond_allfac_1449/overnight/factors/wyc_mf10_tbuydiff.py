from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf10_tbuydiff(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['BuyTradeQuantity_500']
        
        super(wyc_mf10_tbuydiff, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=60, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        #  日内主买量是否在下午突然增加，使用后50分钟的主买量均值与前三个小时的主买量均值进行相减，差值越大，说明尾盘买入力量越大
        data = df['BuyTradeQuantity_500']

        data = data.sum(axis = 1)
        dataall = data.loc[data.index.time <= datetime.time(13,59)]
        data2 = data.loc[(data.index.time >= datetime.time(14,0)) & (data.index.time <= datetime.time(14,49))]

        fall = dataall.groupby(dataall.index.date).mean()
        f2 = data2.groupby(data2.index.date).mean()

        factor = (f2 - fall).to_frame()

        # factor = ts_rank(factor, 60).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor