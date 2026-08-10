from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k218_noonWeightedAmount_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_daily', 'open', 'amount']
        super(wyc_k218_noonWeightedAmount_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        _open = df['open'].between_time(data_afternoon_begin, trade_stop_time)
        _open = _open.groupby(_open.index.date).first()
        _open.index = pd.to_datetime(_open.index)

        _amount = df['amount'].between_time(data_afternoon_begin, trade_stop_time)
        _amount = _amount.groupby(_amount.index.date).sum()
        _amount.index = pd.to_datetime(_amount.index)

        factor = (df['close_daily'] / _open - 1) * _amount

        factor = factor.replace([np.inf,-np.inf], np.nan)
        factor = abs(factor.sub(factor.mean(axis = 1), axis = 0))

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor