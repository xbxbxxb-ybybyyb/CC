from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class MinBus(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.buytradenum_minute"]

    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        numtrade = database.depend_data['FactorData.Basic_factor.buytradenum_minute']
        numtrade = pd.DataFrame(numtrade.values / numtrade.sum().values, index=numtrade.index, columns=numtrade.columns)
        return -numtrade.skew()
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).mean()