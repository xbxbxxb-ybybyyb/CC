from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf1_tbuy(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['BuyTradeMoney_500']
        
        super(wyc_mf1_tbuy, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=70, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # 尾盘主买金额
        BuyTradeMoney_500 = df['BuyTradeMoney_500']
        BuyTradeMoney_500 = BuyTradeMoney_500.loc[BuyTradeMoney_500.index.time <= datetime.time(14,49)]
        mbm = BuyTradeMoney_500.loc[BuyTradeMoney_500.index.time >= datetime.time(14, 30)]

        factor = mbm.groupby(mbm.index.date).sum().sum(axis = 1).to_frame()
        # factor = ts_rank(factor, 70).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor