from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime

def get_max_drawdone(sharpedailyreturn):
    if isinstance(sharpedailyreturn, pd.Series):
        sharpedailyreturn = sharpedailyreturn.to_frame()
    sharpedailyreturn['equity_curve'] = sharpedailyreturn.cumsum()
    sharpedailyreturn = sharpedailyreturn.reset_index()
    sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
    sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
    return sharpedailyreturn['dd2here'].min()
        
class wyc_mf14_mdgjd(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['BuyOrderQtySumMean_500','SellOrderQtySumMean_500']
        
        super(wyc_mf14_mdgjd, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=60, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        data = df['BuyOrderQtySumMean_500']
        data = data.loc[data.index.time <= datetime.time(14,49)]

        data1 = df['SellOrderQtySumMean_500']
        data1 = data1.loc[data1.index.time <= datetime.time(14,49)]

        factor = (data-data1).sum(axis = 1) * -1

        factor = factor.groupby(factor.index.date).apply(lambda x:get_max_drawdone(x)).to_frame() * -1

        # factor = ts_rank(t, 60).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor