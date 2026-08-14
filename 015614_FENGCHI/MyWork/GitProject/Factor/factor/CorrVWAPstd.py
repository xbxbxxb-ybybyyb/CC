from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class CorrVWAPstd(BaseFactor):

    '''
    * 因子名：CorrVWAPstd_13h
    * 描述：VWAP收益率10分钟变化的方差与VWAP的相关性
    * 逻辑：VWAP变大方差变小是涨的趋势，VWAP变小方差变小是反转的趋势
    * 因子参数：分钟数据的换手，体量
    * 作者：孔剑阳
    * 日期：2019.8.12
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "FIX"
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_amt_min, s_vol_min]
    minute_lag = 1
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        vol_min = database.depend_data[self.s_vol_min]
        df_single_day = self.minute(amt_min, vol_min)
        return df_single_day
    
    def minute(self, MinuteTurnover,MinuteVolume):
        MinuteVWAP = MinuteTurnover / MinuteVolume
        MinuteVWAPDiffabs = MinuteVWAP.diff().applymap(abs)
        VWAPstd = MinuteVWAPDiffabs.rolling(10).std()
        # corr = VWAPstd.corrwith(MinuteVWAP)
        corr = Util.array_coef(VWAPstd, MinuteVWAP)
        return -corr
