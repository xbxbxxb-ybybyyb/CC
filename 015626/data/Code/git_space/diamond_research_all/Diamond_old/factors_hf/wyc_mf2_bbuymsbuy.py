from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf2_bbuymsbuy(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        required_columns=['buy_superorder_volume_500','buy_smallorder_volume_500']
        lookback_bars=2000
        super(wyc_mf2_bbuymsbuy, self).__init__(*args, required_columns=required_columns,
                                  lookback_bars=lookback_bars, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        #机构主买量与散户主买量之差
        
        buy_superorder_volume_500 = df['buy_superorder_volume_500']
        buy_smallorder_volume_500 = df['buy_smallorder_volume_500']

        buy_superorder_volume_500 = buy_superorder_volume_500.loc[buy_superorder_volume_500.index.time <= datetime.time(14,49)]
        buy_smallorder_volume_500 = buy_smallorder_volume_500.loc[buy_smallorder_volume_500.index.time <= datetime.time(14,49)]

        buy_super_volume = buy_superorder_volume_500.groupby(buy_superorder_volume_500.index.date).sum().sum(axis = 1)

        buy_small_volume = buy_smallorder_volume_500.groupby(buy_smallorder_volume_500.index.date).sum().sum(axis = 1)

        factor = buy_super_volume - buy_small_volume

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)
        factor = factor * -1
        factor = ts_rank(factor, 40).to_frame()

        factor.columns = [columnname]
        return factor