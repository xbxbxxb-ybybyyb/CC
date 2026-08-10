import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
   

class wyc_on34_BaseUpDown_spot(FactorGenerator):
    
    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH','open_000905.SH','low_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        close = df['close_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        opendf = df['open_000905.SH'].groupby(df['open_000905.SH'].index.date).first()
        low = df['low_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()

        factor = (opendf > (low*1.008)) & (close > (low*1.015)) | (opendf > (close*1.015)) | ((opendf*1.015) < close)
        factor = factor.astype('int')
        factor = factor.to_frame()

        factor.index.name = 'dt'
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]
        return factor