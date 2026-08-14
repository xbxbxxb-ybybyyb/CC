from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinHVSmin(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute',
                    'FactorData.Basic_factor.high_minute',
                    'FactorData.Basic_factor.amt_minute',]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    # lag = 20
    reform_window = 10

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
                
        volume = volume.replace(0.,np.nan)
        vwap = amt.cumsum() / volume.cumsum()
        skew = (high - vwap).skew()
        return -skew
                
                        
                                                                      
                
    def  reform(self, temp_result):
        A = temp_result.rolling(10,1).min()
        return A