# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_UpVolumeSkewSeasonalBias(BaseFactor):
    """
    * 因子名：HF_UpVolumeSkewSeasonalBias_13h
    * 因子功能描述：因子上线路径上的成交量的偏度，表示投资者的信心，将其与季度均值做差得到其偏离度，表示过度信心导致的泡沫，因子越大，泡沫越多。
    * 因子参数：MinuteClose, MinuteVolume
    * 因子创建日期：20190821
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.close_minute"]
    lag = 1
    reform_window = 60
    
    # def definition(self, MinuteClose, MinuteVolume):
    #     factor = self.minute_help(self.minute, 'HF_UpVolumeSkewSeasonalBias_13hHelp', MinuteClose, MinuteVolume)
    #     result = factor-factor.rolling(60).mean()
    #     for i in range(len(result)):
    #         # if a row is full of missing data, set them all to zero
    #         if len(result.iloc[i].dropna())==0: result.iloc[i] = 0.
    #     return result
    
    # def minute(self, MinuteClose, MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     compute_date = date_list[-1] 
        
    #     close_df = MinuteClose.loc[compute_date]
    #     volume_df = MinuteVolume.loc[compute_date]
    #     re = close_df.pct_change()
        
    #     result = volume_df[re>0].skew()
    #     result = result[~np.isinf(result)]
        
    #     return -1*result

    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1] 
        
        close_df = MinuteClose.loc[compute_date]
        volume_df = MinuteVolume.loc[compute_date]
        # re = close_df.pct_change()
        re = (close_df - close_df.shift(1))/close_df
        
        # result = volume_df[re>0].skew()
        result = volume_df[pd.DataFrame(re.values>0, index=re.index,columns=re.columns)].skew()
        result = result[~np.isinf(result)]
        
        return -1*result

    def reform(self, factor):
        result = factor-factor.rolling(60).mean()
        for i in range(len(result)):
            # if a row is full of missing data, set them all to zero
            if len(result.iloc[i].dropna())==0: result.iloc[i] = 0.
        return result


