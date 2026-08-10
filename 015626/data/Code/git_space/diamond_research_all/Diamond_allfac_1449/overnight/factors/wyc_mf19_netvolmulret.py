from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf19_netvolmulret(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['WeightSellOrderQtySumMean_500','WeightBuyOrderQtySumMean_500','close_spot']
        
        super(wyc_mf19_netvolmulret, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=12, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        # 10档盘口加权买量与10档盘口加权卖量的差值与指数收益率的乘积
        close_spot = df['close_spot']

        close_spot_pm = close_spot.loc[close_spot.index.time == datetime.time(14,49)]
        close_spot_am = close_spot.loc[close_spot.index.time == datetime.time(9,30)]
        close_spot_ret = close_spot_pm.groupby(close_spot_pm.index.date).sum() / close_spot_am.groupby(close_spot_am.index.date).sum()

        WeightBuyOrderQtySumMean_500 = df['WeightBuyOrderQtySumMean_500']
        WeightBuyOrderQtySumMean_500 = WeightBuyOrderQtySumMean_500.loc[WeightBuyOrderQtySumMean_500.index.time <= datetime.time(14,49)]
        WeightSellOrderQtySumMean_500 = df['WeightSellOrderQtySumMean_500']
        WeightSellOrderQtySumMean_500 = WeightSellOrderQtySumMean_500.loc[WeightSellOrderQtySumMean_500.index.time <= datetime.time(14,49)]

        numdiff = WeightBuyOrderQtySumMean_500 - WeightSellOrderQtySumMean_500
        numdiff = numdiff.groupby(numdiff.index.date).sum().sum(axis = 1)
        
        numdiff = numdiff.loc[numdiff.index.isin(close_spot_ret.index)]
        close_spot_ret = close_spot_ret.loc[close_spot_ret.index.isin(numdiff.index)]

        factor = (numdiff * (close_spot_ret - 1)).to_frame() * -1
        # factor = ts_mean(factor, 3)
        # factor = ts_rank(factor, 12).to_frame()
        
        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor