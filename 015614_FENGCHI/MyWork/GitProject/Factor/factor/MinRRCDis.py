from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinRRCDis(BaseFactor):  # 派生一个因子类
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.close_minute","FactorData.Basic_factor.open_minute"]
    reform_window = 40

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        high = database.depend_data['FactorData.Basic_factor.high_minute'].iloc[120:]
        low = database.depend_data['FactorData.Basic_factor.low_minute'].iloc[120:]
        close = database.depend_data['FactorData.Basic_factor.close_minute'].iloc[120:]
        open_ = database.depend_data['FactorData.Basic_factor.open_minute'].iloc[120:]

        min_return = (close-open_)/open_
        min_range = high - low
        ratio = Util.array_coef(min_range, min_return)       
        return ratio

     

    def  reform(self, temp_result):
        A = temp_result - temp_result.rolling(10,1).min()
        return -A.rolling(10,1).mean()
        