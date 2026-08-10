from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k15_yue_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','B_INFO_OUTSTANDINGBALANCE']
        super(wyc_k15_yue_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tickerlist = df['close'].columns.tolist()
        cbondamount = df['B_INFO_OUTSTANDINGBALANCE']
        cbondamount = cbondamount[list(set(cbondamount.columns.tolist()) & set(tickerlist))]
        factor = -1 * cbondamount
        factor = factor.replace([np.inf, -np.inf, 0], np.nan)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor