from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf1_tbuy(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        required_columns=['BuyTradeMoney_500']
        lookback_bars=2000
        super(wyc_mf1_tbuy, self).__init__(*args, required_columns=required_columns,
                                  lookback_bars=lookback_bars, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # 尾盘主买金额
        BuyTradeMoney_500 = df['BuyTradeMoney_500']
        BuyTradeMoney_500 = BuyTradeMoney_500.loc[BuyTradeMoney_500.index.time <= datetime.time(14,49)]
        mbm = BuyTradeMoney_500.loc[BuyTradeMoney_500.index.time >= datetime.time(14, 30)]

        factor = mbm.groupby(mbm.index.date).sum().sum(axis = 1)
        factor = ts_rank(factor, 70).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor