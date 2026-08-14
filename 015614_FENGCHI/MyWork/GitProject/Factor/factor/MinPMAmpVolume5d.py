# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinPMAmpVolume5d(BaseFactor):
    """

    *因子名 : MinPMAmpVolume5d
    *因子功能描述 : 下午时间段的分钟最高价和分钟最低价之间的volume占比乘上符号。
              如果最高价出现在最低价之后，则符号为正，反之为负。rolling 5日ema
               
       
    *因子参数 : MinuteHigh-分钟最高价, MinuteLow-分钟最低价，MinuteVolume-分钟成交量,
            Minute_Status-分钟数据是否合法，is_valid_raw-是否合法
    *作者 : wulb
    *因子创建日期 : 2019.1.22
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute", \
    "FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        fmt = '%Y-%m-%d'
        date = np.unique(MinuteHigh.index.strftime(fmt))[0]
        minute_factor = pd.DataFrame(index=[pd.Timestamp(date)],columns=MinuteHigh.columns)
        
                   
        high_adj = MinuteHigh.loc[date]
        low_adj = MinuteLow.loc[date]
        volume = MinuteVolume.loc[date]
        
        high_adj = high_adj[120:]
        low_adj = low_adj[120:]
        
        day_factor = pd.Series(np.nan, index=high_adj.columns)
        
        for stock in high_adj.columns:
            stock_high = high_adj[stock].max()
            stock_high_pos = pd.to_datetime(np.argmax(high_adj[stock]))
            stock_low = low_adj[stock].min()
            stock_low_pos = pd.to_datetime(np.argmin(low_adj[stock]))

            stock_volume_sum = volume[stock].sum()
            if stock_volume_sum == 0:
                day_factor[stock] = np.nan
                continue

            if pd.isnull(stock_high_pos):
                day_factor[stock] = np.nan
            else:
                if stock_high_pos > stock_low_pos:
                    stock_volume = volume[stock][stock_low_pos:stock_high_pos+pd.Timedelta(minutes=1)].sum()
                    factor = stock_volume / stock_volume_sum
                    day_factor[stock] = factor

                else:
                    stock_volume = volume[stock][stock_high_pos:stock_low_pos+pd.Timedelta(minutes=1)].sum()
                    factor = -1 * stock_volume / stock_volume_sum
                    day_factor[stock] = factor                        
        
        #print(minute_factor)
        return day_factor
        
    def reform(self, minute_factor_df):        

        minute_factor_df = minute_factor_df.ewm(span=self.reform_window).mean()
        minute_factor_df = -minute_factor_df
        
        return minute_factor_df        