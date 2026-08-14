from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HFPVCorr(BaseFactor):

    '''
    * 因子名：HFPVCorr_13h
    * 逻辑：最高价和最低价的差和均价相关性乘以负1。高低差越大说明短期波动大，炒作可能性更高，价格和其相关性越小受其影响越小，获得超额概率越大。
    * 因子参数：分钟数据高低量额
    * 作者：xust
    * 日期：2019.7.8
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = 'FIX'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_high_min, s_low_min, s_amt_min, s_volume_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        amt_min = database.depend_data[self.s_amt_min]
        volume_min = database.depend_data[self.s_volume_min]
        return self.minute(high_min, low_min, amt_min, volume_min)
        # return self.minute_help(self.minute, 'HFPVCorr_13h', MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume)

    def minute(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
        # dt = sorted(np.unique(MinuteTurnover.index.strftime('%Y-%m-%d')))
        p = (MinuteTurnover / MinuteVolume).iloc[5:120]
        d = (MinuteHigh - MinuteLow).iloc[5:120]
        df = - Util.array_coef(p, d)
        return df