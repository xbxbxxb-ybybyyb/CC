import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
  
class wyc_on31_DownBarNumPm_spot(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH','open_000905.SH','high_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=10, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        close_spot = df['close_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        open_spot = df['open_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        high_spot = df['high_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)

        down1 = close_spot < open_spot
        down2 = high_spot < open_spot.shift(1)
        down = down1 & down2

        down = down.groupby(down.index.date).sum()

        factor = down.to_frame()

        factor.index.name = 'dt'
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]
        return factor