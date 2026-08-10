from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf9_sbuymratio(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        required_columns=['buy_smallorder_money_500','BuyTradeMoney_500']
        lookback_bars=2000
        super(wyc_mf9_sbuymratio, self).__init__(*args, required_columns=required_columns,
                                  lookback_bars=lookback_bars, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        #  散户主买金额占比
        superorder = df['buy_smallorder_money_500']
        data = df['BuyTradeMoney_500']

        superorder = superorder.loc[superorder.index.time <= datetime.time(14,49)]
        data = data.loc[data.index.time <= datetime.time(14,49)]

        fall = data.groupby(data.index.date).sum().sum(axis = 1)
        fs = superorder.groupby(superorder.index.date).sum().sum(axis = 1)

        factor = fs / fall

        factor = ts_rank(factor, 30).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor