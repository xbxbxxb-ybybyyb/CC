# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class HF_VolumeTopVwapRatio(BaseFactor):
    """
    * 因子名：HF_VolumeTopVwapRatio_13h
    * 因子功能描述：T日成交量高分位数时刻和其他时刻对应的Vwap之比，值越大，说明大量交易发生在相对高价，未来越容易下跌
    * 因子参数：MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.9.24
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 20

    # def definition(self,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteVolume,MinuteTurnover)
    #     factor = - factor / self.rolling_max(factor,window=20)
    #     return factor

    # def minute(self,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
        
    #     volume = MinuteVolume.loc[compute_date]
    #     amt = MinuteTurnover.loc[compute_date]
    #     cond = volume > volume.quantile(0.9)               
    #     vwap_top = amt[cond].sum() / volume[cond].sum()
    #     vwap_all = amt[~cond].sum() / volume[~cond].sum()
    #     ratio =  vwap_top / vwap_all     
    #     return -1*ratio

    def rolling_max(self,factor,window):
        return factor.rolling(window=window,min_periods=1).max()

    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        volume = MinuteVolume.loc[compute_date]
        amt = MinuteTurnover.loc[compute_date]
        # cond = volume > volume.quantile(0.9) 
        cond = pd.DataFrame(np.subtract(volume.values, volume.quantile(0.9).values) > 0,
            index=volume.index,columns=volume.columns)
        vwap_top = amt[cond].sum() / volume[cond].sum()
        vwap_all = amt[~cond].sum() / volume[~cond].sum()
        ratio =  vwap_top / vwap_all     
        return -ratio

    def reform(self, factor):
        factor = - factor / self.rolling_max(factor,window=20)
        return factor