from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k223_lowWeightedAmount_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount_daily', 'low_daily', 'low']
        super(wyc_k223_lowWeightedAmount_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        low_noon = df['low'].between_time(datetime.time(14,0), trade_stop_time)
        low_noon = low_noon.groupby(low_noon.index.date).min()
        low_noon.index = pd.to_datetime(low_noon.index)

        factor = low_noon / df['low_daily'] - 1
        factor = factor * df['amount_daily']
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor