from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time



class MinuteValidRet(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute',"FactorData.Basic_factor.is_valid"]    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series


    

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        Close = database.depend_data['FactorData.Basic_factor.close_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        is_valid=is_valid.iloc[-1,:]
        stocks_not_valid = list(is_valid[is_valid==0].index)

        ret = (Close.iloc[-1] - Close.iloc[60])/Close.iloc[60]
        ret[stocks_not_valid] = np.nan
        return ret




    def  reform(self, temp_result):
        A = (-temp_result).rolling(self.reform_window).mean() / (temp_result).rolling(self.reform_window).std()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A



