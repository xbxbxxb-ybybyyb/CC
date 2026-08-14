# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class HF_VolSwing5mToAll(BaseFactor):

    """
    * 因子名：HF_VolSwing5mToAll_13h
    * 因子功能描述：成交量振幅（最后5m）/全天成交量振幅，该值越大，尾部流动性增量越好，交易越活越。因子值越大越好。
    * 因子参数：MinuteOpen, MinuteClose
    * 因子创建日期：20190813
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 1
    minute_lag=1
    reform_window = 0
    
    # def definition(self,MinuteVolume):
    #     result = self.minute_help(self.minute, 'HF_VolSwing5mToAll_13hHelp',MinuteVolume)
    #     for i in range(len(result)):
    #         # if a row is full of missing data, set them all to zero
    #         if len(result.iloc[i].dropna())==0: result.iloc[i] = 0.
    #     return result
    
    # def minute(self,MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteVolume.index.strftime(fmt))
    #     compute_date = date_list[-1] 
        
    #     volume_df = MinuteVolume.loc[compute_date]
    #     volume_df_5m = volume_df.iloc[-5:]
    #     vol_swing_5m = (volume_df_5m.max()-volume_df_5m.min())
    #     vol_swing_day = (volume_df.max()-volume_df.min())
    #     result = vol_swing_5m/vol_swing_day
        
    #     return result
    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteVolume = pd.DataFrame(MinuteVolume.values*100, index=MinuteVolume.index,columns=MinuteVolume.columns)
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))
        compute_date = date_list[-1] 
        
        volume_df = MinuteVolume.loc[compute_date]
        volume_df_5m = volume_df.iloc[-5:]
        vol_swing_5m = (volume_df_5m.max()-volume_df_5m.min())
        vol_swing_day = (volume_df.max()-volume_df.min())
        result = vol_swing_5m/vol_swing_day
        return result

    def reform(self, result):
        for i in range(len(result)):
            # if a row is full of missing data, set them all to zero
            if len(result.iloc[i].dropna())==0: result.iloc[i] = 0.
        return result
