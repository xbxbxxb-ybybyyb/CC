# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteTLSTRvs(BaseFactor):
    """

    *因子名 : MinuteHTRtnRvs
    *因子功能描述 : 最后十五分钟多头成交额与空头成交额差在最后十五分钟总成交额中的占比
    *因子参数 : MinuteClose-分钟末端价格, MinuteTurnover-分钟末端成交额
    *作者 : 沈天琦(shentq)
    *因子创建日期 : 2019.05.14
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5
        


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']        
        
        fmt = '%Y-%m-%d'
        
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        date = date_list[-1]

        minute_close = MinuteClose.loc[date]
        minute_turnover = MinuteTurnover.loc[date]
        
        df_factor = pd.DataFrame(index=[pd.Timestamp(date)], columns=MinuteClose.columns)
        
        arr = (minute_close/minute_close.shift(1)).values-1
        minute_close_return = pd.DataFrame(arr,index=minute_close.index,columns=minute_close.columns)

        arr = minute_close_return > 0
        minute_close_return_big = pd.DataFrame(arr,index=minute_close_return.index,columns=minute_close_return.columns)
        arr = minute_close_return < 0
        minute_close_return_small = pd.DataFrame(arr,index=minute_close_return.index,columns=minute_close_return.columns)

        long_turnover = minute_turnover[-15:][minute_close_return_big]
        short_turnover = minute_turnover[-15:][minute_close_return_small]

        df_factor.loc[date] = (short_turnover.sum() - long_turnover.sum()) / minute_turnover[-15:].sum()

#################orig code##############
        # fmt = '%Y-%m-%d'
        
        # date_list = np.unique(MinuteClose.index.strftime(fmt))
        # date = date_list[-1]

        # minute_close = MinuteClose.loc[date]
        # minute_turnover = MinuteTurnover.loc[date]
        
        # df_factor = pd.DataFrame(index=[pd.Timestamp(date)], columns=MinuteClose.columns)
        
        # minute_close_return = minute_close.pct_change(1)

        # long_turnover = minute_turnover[-15:][minute_close_return > 0]
        # short_turnover = minute_turnover[-15:][minute_close_return < 0]

        # df_factor.loc[date] = (short_turnover.sum() - long_turnover.sum()) / minute_turnover[-15:].sum()
         
        return df_factor.iloc[-1]

    def reform(self, factor_values):
        # 计算n日波动率
        factor_values = factor_values.rolling(window=5, min_periods=1).mean()
        
        return factor_values                    
