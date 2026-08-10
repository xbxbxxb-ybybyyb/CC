from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf13_nmdiffstknum(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['BuyOrderQtySumMean_500']
        
        super(wyc_mf13_nmdiffstknum, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=30, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        data = df['BuyOrderQtySumMean_500']
        data = data.loc[(data.index.time >= datetime.time(9,40))&(data.index.time <= datetime.time(11,29))]

        data1 = df['BuyOrderQtySumMean_500']
        data1 = data1.loc[(data1.index.time >= datetime.time(13,0))&(data1.index.time <= datetime.time(14,49))]

        fm = data.groupby(data.index.date).sum()
        fn = data1.groupby(data1.index.date).sum()

        factor = np.sign(fn - fm)
        factor = factor.sum(axis = 1).to_frame()

        # factor = ts_rank(factor, 30).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor