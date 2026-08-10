from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf5_ssellvol(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['sell_smallorder_volume_500']
        
        super(wyc_mf5_ssellvol, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=30, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # 小单主卖量
        
        sell_smallorder_volume_500 = df['sell_smallorder_volume_500']

        sell_smallorder_volume_500 = sell_smallorder_volume_500.loc[sell_smallorder_volume_500.index.time <= datetime.time(14,49)]


        sell_small_volume = sell_smallorder_volume_500.groupby(sell_smallorder_volume_500.index.date).sum().sum(axis = 1)
        factor = sell_small_volume.to_frame()
        # factor = ts_rank(factor, 30).to_frame()

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor