from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf3_mbuyvol(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['buy_midorder_volume_500','sell_midorder_volume_500']
        
        super(wyc_mf3_mbuyvol, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=50, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # 中单成交量
        
        buy_midorder_volume_500 = df['buy_midorder_volume_500']
        sell_midorder_volume_500 = df['sell_midorder_volume_500']

        buy_midorder_volume_500 = buy_midorder_volume_500.loc[buy_midorder_volume_500.index.time <= datetime.time(14,49)]
        sell_midorder_volume_500 = sell_midorder_volume_500.loc[sell_midorder_volume_500.index.time <= datetime.time(14,49)]


        buy_mid_volume = buy_midorder_volume_500.groupby(buy_midorder_volume_500.index.date).sum().sum(axis = 1)
        sell_mid_volume = sell_midorder_volume_500.groupby(sell_midorder_volume_500.index.date).sum().sum(axis = 1)
        factor = (sell_mid_volume + buy_mid_volume).to_frame()
        # factor = ts_rank(factor, 50).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor