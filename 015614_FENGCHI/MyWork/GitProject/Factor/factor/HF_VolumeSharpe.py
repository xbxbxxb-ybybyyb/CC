# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class HF_VolumeSharpe(BaseFactor):
    """
    * 因子名：HF_VolumeSharpe_13h
    * 因子功能描述：T-2日到T日成交量比例的夏普值，代表了成交量增长的稳定性，稳定性越好，未来价格稳步上涨可能越大
    * 因子参数：MinuteVolume
    * 作者：游加平
    * 因子创建日期： 2019.10.11
    """
    # def definition(self,MinuteVolume):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteVolume)
    #     return factor

    # def minute(self,MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]        
    #     ppre_date = date_list[-3]
 
    #     volume = MinuteVolume.loc[ppre_date:compute_date]
    #     volume = volume.div(volume.mean(axis=0),axis=1)      
    #     volume_smooth = volume.groupby(pd.Grouper(freq='15min')).mean()
    #     sharpe = volume_smooth.mean() / volume_smooth.std()
    #     return sharpe
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 2


    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]        
        ppre_date = date_list[-3]
 
        volume = MinuteVolume.loc[ppre_date:compute_date]
        # volume = volume.div(volume.mean(axis=0),axis=1)      
        volume = np.divide(volume, volume.mean(axis=0).values)
        volume_smooth = volume.groupby(pd.Grouper(freq='15min')).mean()
        sharpe = volume_smooth.mean() / volume_smooth.std()
        return sharpe
