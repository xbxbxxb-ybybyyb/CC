# -*- coding: utf-8 -*-
'''
* 因子名称： CyqHhi_13h
* 描述： 筹码分布的HHI指数的倒数
* 因子逻辑： 如果筹码集中分布在某一个价位，当后续股票高于这个价位则容易被大规模卖出获利了结，当后续股价低于这个价位则容易被大规模卖出止损，因此要挑选筹码均匀分布的股票
* 因子参数： 分钟数据的成交额、成交量，复权因子
* 作者： 何丰敬
* 日期： 2019.10.22
* 函数修改日期: 尚未修改
* 修改人： 尚未修改
* 修改原因： 尚未修改
'''
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import datetime as dt

class CyqHhi(BaseFactor):
    
    factor_type = 'FIX'
    
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    s_adj_min = 'FactorData.Basic_factor.adjfactor_minute'
    depend_data = [s_amt_min, s_vol_min, s_adj_min]
    minute_lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        vol_min = database.depend_data[self.s_vol_min]
        adj_min = database.depend_data[self.s_adj_min]
        return self.minute(amt_min, vol_min, adj_min)
    
    def reform(self, temp_result):
        return (1 / temp_result).rolling(self.reform_window).mean()

    def minute(self, MinuteTurnover, MinuteVolume, adj_min):
        # MinuteVolume = (MinuteVolume.iloc[:240] * adj_min.iloc[-1] / adj_min.iloc[0]).append(MinuteVolume.tail(240)) # 复权成交量
        MinuteTurnover, MinuteVolume = MinuteTurnover.tail(240), MinuteVolume.tail(240)  # 取最近240分钟数据
        vwap = (MinuteTurnover / MinuteVolume).fillna(method='pad')
        quantile = vwap.quantile(np.arange(0, 1.2, 0.2))  # 对每只股票按成交均价分成5档
        volume = pd.DataFrame(0.0, index=range(5), columns=MinuteVolume.columns)
        vwap_arr = vwap.values
        quantile_arr = quantile.values
        for i in range(5):
            volume.iloc[i] = MinuteVolume[pd.DataFrame((vwap_arr >= quantile_arr[i]) & (vwap_arr <= quantile_arr[i+1]), index=vwap.index, columns=vwap.columns)].sum()  # 统计每一档的成交量
        volume = volume.values / volume.sum().values  # 成交量在每个档位的分布
        print(adj_min.index[-1])
        return pd.Series((volume * volume).sum(axis=0), index = adj_min.columns)  # HHI