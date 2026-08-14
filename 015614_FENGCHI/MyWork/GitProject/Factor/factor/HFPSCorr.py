from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class HFPSCorr(BaseFactor):

    '''
    * 因子名：HFPSCorr_13h
    * 逻辑：10分钟均价和均价标准差相关性乘以负1。均价标准差越大说明短期波动大，炒作可能性更高，价格和其相关性越小受其影响越小，获得超额概率越大。
    * 因子参数：分钟数据量额
    * 作者：xust
    * 日期：2019.7.12
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = 'FIX'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_amt_min, s_volume_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        volume_min = database.depend_data[self.s_volume_min]
        return self.minute(amt_min, volume_min)

    def minute(self, MinuteTurnover, MinuteVolume):
        dt = sorted(np.unique(MinuteTurnover.index.strftime('%Y-%m-%d')))
        p = (MinuteTurnover.rolling(window=10, min_periods=10).sum() / MinuteVolume.rolling(window=10, min_periods=10).sum()).iloc[10:]
        d = (MinuteTurnover / MinuteVolume).rolling(window=10, min_periods=10).std().iloc[10:]
        df = - Util.array_coef(p, d)
        return df