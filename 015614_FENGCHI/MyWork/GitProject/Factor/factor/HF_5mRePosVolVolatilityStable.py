from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HF_5mRePosVolVolatilityStable(BaseFactor):
    """
    * 因子名：HF_5mRePosVolVolatilityStable_13h
    * 因子功能描述：在五分钟线上，对于正收益对应路径上的成交量的波动率，该波动率越低，且短期内保持稳定（5日sharpe），说明异常炒作越少。
    * 因子参数：MinuteClose, MinuteVolume
    * 因子创建日期：20190827
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = 'FIX'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_close_min, s_vol_min]
    minute_lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        vol_min = database.depend_data[self.s_vol_min]
        return self.minute(close_min, vol_min)
    
    def reform(self, temp_result):
        factor = -(temp_result - temp_result.rolling(self.reform_window).mean()) / temp_result.rolling(self.reform_window).std()

        for i in range(len(factor)):
            if len(factor.dropna()) == 0: 
                factor.iloc[i] = 0

        return factor

    def minute(self, MinuteClose, MinuteVolume):
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1] 
        
        close_df = MinuteClose.loc[compute_date]
        volume_df = MinuteVolume.loc[compute_date]
        re_5m = close_df.pct_change(5)
        
        result = volume_df[re_5m>0].std()
        result = result[~np.isinf(result)]
        
        return result