from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf11_nmgjd(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['BuyTradeQuantity_500','SellTradeQuantity_500']
        
        super(wyc_mf11_nmgjd, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=60, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        data = df['BuyTradeQuantity_500']
        databm = data.loc[data.index.time == datetime.time(9,30)]
        databn = data.loc[data.index.time == datetime.time(14,49)]

        data1 = df['SellTradeQuantity_500']
        datasm = data1.loc[data1.index.time == datetime.time(9,30)]
        datasn = data1.loc[data1.index.time == datetime.time(14,49)]

        bsm = (databm - datasm).sum(axis = 1)
        bsn = (databn - datasn).sum(axis = 1)

        factor = (bsm.groupby(bsm.index.date).mean() - bsn.groupby(bsn.index.date).mean()).to_frame() * -1

        # factor = ts_rank(factor, 60).to_frame() * -1

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor