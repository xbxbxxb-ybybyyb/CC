from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_mf17_dealhigh(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla' ,'volume_alla']
        super(wyc_mf17_dealhigh, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=3, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        zz500_stock_list = self.get_mdconstant('zz500_stock_list')
        volume_500 = df['volume_alla'][zz500_stock_list].between_time(futures_data_morning_begin, trade_stop_time)

        close_500 = df['close_alla'][zz500_stock_list].between_time(futures_data_morning_begin, trade_stop_time)

        vol = volume_500.groupby(volume_500.index.date).sum()
        vol = vol.reindex(volume_500.index, method='pad').replace(0,np.nan)

        vwap = volume_500 / vol * close_500
        vwap = vwap.groupby(vwap.index.date).sum().replace(0,np.nan)

        twap = close_500.groupby(close_500.index.date).mean().replace(0,np.nan)

        factor = vwap / twap - 1

        factor = factor.sum(axis = 1).to_frame() * -1 

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]

        return factor