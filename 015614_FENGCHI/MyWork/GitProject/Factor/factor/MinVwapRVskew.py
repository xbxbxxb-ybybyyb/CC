# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinVwapRVskew(BaseFactor):
    
    '''
    * 因子名：MinVwapRVskew
    * 逻辑：该因子是一个分钟因子，是MinVwapRV的偏度，反映了MinVwapRV分布的趋势，
    *      当偏度越大时，分布右偏时，说明有优势信息的投资者在不断高位出货，趋势延续
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2018.12.25
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute", \
    "FactorData.Basic_factor.low_minute","FactorData.Basic_factor.open_minute","FactorData.Basic_factor.amt_minute",\
    "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20
    

    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        fmt = '%Y-%m-%d' 
        date = np.unique(MinuteClose.index.strftime(fmt))[0] 
        df_ratio = pd.DataFrame(index=[pd.Timestamp(date)], columns=MinuteClose.columns) 
    
        min_close = MinuteClose.loc[date]
        min_open = MinuteOpen.loc[date]
        arr = (min_close / min_open).values - 1
        min_return = pd.DataFrame(arr,index=min_open.index,columns=min_open.columns)
        min_turn = MinuteTurnover.loc[date]
        min_volume = MinuteVolume.loc[date]
        min_RV = np.abs(min_return) / min_volume

        arr = min_RV.values > np.nanquantile(min_RV.values,0.8,axis=0)
        RV_flag = pd.DataFrame(arr,index=min_RV.index,columns=min_RV.columns)

        # RV_flag = (min_RV > min_RV.quantile(0.8))
        vwap_RV = min_turn[RV_flag].sum() / min_volume[RV_flag].sum()
        vwap_allday = min_turn.sum() / min_volume.sum()
        df_ratio.loc[date] = vwap_RV / vwap_allday
        return df_ratio.iloc[-1]


    def reform(self, dailyf):
        '''
        * 因子实现：RV = 跌幅/成交量，筛选出RV值前20%的时段，求vwap比值，20日偏度
        '''
        alpha = dailyf.rolling(window=self.reform_window, min_periods=10).skew()
        return alpha
