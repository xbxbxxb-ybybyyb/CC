from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k16_vturnoverrate_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume','B_INFO_OUTSTANDINGBALANCE']
        super(wyc_k16_vturnoverrate_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)
        cbondamount = df['B_INFO_OUTSTANDINGBALANCE']
        tickerlist = list(set(cbondamount.columns.tolist()) & set(volume.columns.tolist()))
        cbondamount = cbondamount[tickerlist]
        volume = volume[tickerlist]

        factor = volume / (cbondamount / 100)
        factor = factor.replace([np.inf, -np.inf, 0], np.nan)
        factor = factor.rank(axis = 1, pct = True)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor