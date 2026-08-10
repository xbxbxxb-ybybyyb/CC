from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k5_volstd_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_alla', 'amount_alla']
        super(wyc_if_2hour_return_nr_as_cfg, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        zz500_stock_list = self.get_mdconstant('zz500_stock_list')
        cif = df['close_alla'][zz500_stock_list].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount_alla'][zz500_stock_list].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 40)
        factor = ts_rank(factor, 5 * 242)

        factor = factor.at_time(trade_stop_time)
        factor.index = pd.to_datetime(factor.index.date)
        factor.columns = [columnname]

        return factor