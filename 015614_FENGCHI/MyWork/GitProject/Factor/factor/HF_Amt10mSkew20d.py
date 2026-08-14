from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class HF_Amt10mSkew20d(BaseFactor):
    """
    * 因子名：HF_Amt10mSkew20d_13h
    * 因子功能描述：成交额10分钟线的偏度，该值表示流动性的偏移程度，值越小，收益回归力度越大，累计20日表示月度的浮盈亏偏度
    * 因子参数：MinuteTurnover
    * 因子创建日期：20190813
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """

    factor_type = 'FIX'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    depend_data = [s_amt_min]
    minute_lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        return self.minute(amt_min)

    def reform(self, temp_result):
        res = -temp_result.rolling(self.reform_window).mean()
        for i in range(len(res)):
            if len(res.iloc[i].dropna()) == 0: res.iloc[i] = 0
        return res
    
    def minute(self,MinuteTurnover):
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        compute_date = date_list[-1] 
        tov_df = MinuteTurnover.loc[compute_date]
        result = tov_df.rolling(10).sum().skew(axis = 0)
        
        return result
