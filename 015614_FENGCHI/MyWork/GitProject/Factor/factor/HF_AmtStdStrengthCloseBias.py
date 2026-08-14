from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class HF_AmtStdStrengthCloseBias(BaseFactor):
    """
    *因子名 : HF_AmtStdStrengthCloseBias_13h
    *因子功能描述 : 成交额波动率与收盘价的相关性,取平均偏离值;值越大，表示放量超买，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteTurnover-分钟成交额
    *作者 : hezq
    *因子创建日期 : 2019.08.02
    """
    factor_type = "FIX"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    depend_data = [s_close_min, s_amt_min]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        amt_min = database.depend_data[self.s_amt_min]
        return self.minute(close_min, amt_min)
        # df[np.isinf(df)] = np.nan
        # df = df-df.rolling(window=rd,min_periods=1).mean()
        return df

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result.rolling(self.reform_window, 1).mean() - temp_result

    def minute(self,MinuteClose,MinuteTurnover): 
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        amt_today = MinuteTurnover.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        
        amt_std = amt_today.rolling(window=5,min_periods=1).std()
        res = Util.array_coef(close, amt_std)
        return res
