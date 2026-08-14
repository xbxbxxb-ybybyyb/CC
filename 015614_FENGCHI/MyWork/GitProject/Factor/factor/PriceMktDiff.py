# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class PriceMktDiff(BaseFactor):
    
    factor_type = 'FIX'
    depend_data = ['FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.adjfactor_minute' ]
    lag = 1
    minute_lag = 1
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])

        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor_minute']

        df = pd.DataFrame(volume.iloc[:240].values * adjfactor.iloc[-1].values / adjfactor.iloc[0].values,
                           index=volume.iloc[:240].index,
                           columns=volume.iloc[:240].columns)
        volume = df.append(volume.iloc[240:])  # 复权成交量

        arr = amt.iloc[-240:].values / volume.iloc[-240:].values
        vwap = pd.DataFrame(arr, index=volume.iloc[-240:].index, columns=volume.iloc[-240:].columns).\
            fillna(method='pad')  # 取最近240分钟成交均价

        r = pd.DataFrame(vwap.values / vwap.shift(1).values - 1,
                         index=vwap.index,
                         columns=vwap.columns)

        p_mkt = r.mean(axis=1).cumsum()
        p_mkt = (p_mkt - p_mkt.mean()) / p_mkt.std()  # 标准化全市场等权指数

        p = r.cumsum()
        arr = (p.values - p.mean().values) / p.std().values
        p = pd.DataFrame(arr, index=p.index, columns=p.columns)  # 标准化价格

        arr = p.values - p_mkt.values.reshape(p.shape[0], 1)
        e = pd.DataFrame(arr, index=p.index, columns=p.columns)

        a = amt.iloc[-240:]
        a = pd.DataFrame(a.values / a.sum().values, index=a.index, columns=a.columns)  # 以成交额占过去240分钟的总成交额比例作为加权权重
        m = pd.DataFrame(e.values * a.values, index=e.index, columns=a.columns).abs().sum()  # 取T-1日下午开盘至T日11:30的加权面积
        return -m