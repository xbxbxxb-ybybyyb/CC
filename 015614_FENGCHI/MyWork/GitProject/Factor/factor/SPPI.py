# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class SPPI(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.high",
    "FactorData.Basic_factor.open","FactorData.Basic_factor.low","FactorData.Basic_factor.volume",
    "FactorData.Basic_factor.free_float_shares","FactorData.Basic_factor.amt"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    def calc_single(self,database):
        close = database.depend_data['FactorData.Basic_factor.close']
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        Open = database.depend_data['FactorData.Basic_factor.open']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        free_float_cap=free_float_shares*close
        free_float_cap = pd.DataFrame(free_float_cap.values*10000,index=free_float_cap.index,columns=free_float_cap.columns)
        n=5
        ochl = Open+high+low+close
        Bk = ochl.rolling(n).mean()
        VRBP =Bk/Bk.shift(1)-1
        SPPI =(amt-Bk*volume)/(free_float_cap*Bk.shift(1))
        return SPPI.iloc[-1,:]