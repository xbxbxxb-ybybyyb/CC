from overnight.factor_generator import FactorGenerator
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_mf9_sbuymratio(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_zz500' ,'amount_zz500']
        super(wyc_mf9_sbuymratio, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=3, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        cif = df['close' + suffix].between_time(datetime.time(9, 30), datetime.time(14, 49))
        # cif[abs(cif) < 1e-8] = np.nan
        # ifreturn = cif / cif.shift(1) - 1
        # factor = ts_mean(ifreturn, 200)

        # factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix].between_time(datetime.time(9, 30), datetime.time(14, 49))
        factor = cif * a
        factor = factor.sum(axis=1).to_frame()

        # factor = ts_rank(factor, 50)
        # factor = ts_mean(factor, 40)
        # factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        # factor = factor.loc[factor.index.time == datetime.time(14, 49)]
        factor = factor.groupby(factor.index.date).last()
        # factor = factor.iloc[-1][columnname]
        return factor