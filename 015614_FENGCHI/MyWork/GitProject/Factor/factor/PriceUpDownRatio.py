"""
    *因子名 : PriceUpDownRatio
    *因子功能描述 : 从开盘到十一点半价格上涨分钟区间均价和价格上升分钟区间均价之比。表示多空力量对价格影响，值越大多头力量越大，超额越高。

    *因子参数 : MinuteVolume -- 分钟成交量, MinuteTurnover -- 分钟成交额, MinuteOpen -- 分钟开盘价, MinuteClose -- 分钟收盘价
    *作者 : 徐志鑫
    *因子创建日期 : 2019.07.09
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
"""
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class PriceUpDownRatio(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute','FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.open_minute','FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop","merge"])

        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        dates = sorted(np.unique(MinuteVolume.index.strftime(fmt)))

        today = dates[-1]
        
        today_volume = MinuteVolume.loc[today]
        today_turnover = MinuteTurnover.loc[today]


        price = today_turnover / today_volume
        
        _open = MinuteOpen.loc[today]
        close = MinuteClose.loc[today]

        price_diff = close - _open

        price_diff_up = pd.DataFrame(price_diff.values >= 0, index=price_diff.index, columns=price_diff.columns)
        price_diff_down = pd.DataFrame(price_diff.values < 0, index=price_diff.index, columns=price_diff.columns)

        price_diff[price_diff_up] = 1
        price_diff[price_diff_down] = -1
        
        price_diff_one = pd.DataFrame(price_diff.values == 1, index=price_diff.index, columns=price_diff.columns)
        price_diff_minus_one = pd.DataFrame(price_diff.values == -1, index=price_diff.index, columns=price_diff.columns)
        
        price_up = (price_diff[price_diff_one] * price).mean()
        price_down = (-price_diff[price_diff_minus_one] * price).mean()
        
        ratio = price_up / price_down
        
        return ratio

    # def definition(self, MinuteVolume, MinuteTurnover, MinuteOpen, MinuteClose):
    #     ratio = self.minute_help(self.minute, 'PriceUpDownRatio_13hHelp', MinuteVolume, MinuteTurnover, MinuteOpen, MinuteClose)
    #     return ratio.rolling(1).mean()

    # def minute(self, MinuteVolume, MinuteTurnover, MinuteOpen, MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     dates = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     today = dates[-1]
        
    #     today_volume = MinuteVolume.loc[today]
    #     today_turnover = MinuteTurnover.loc[today]

    #     price = today_turnover / today_volume
        
    #     _open = MinuteOpen.loc[today]
    #     close = MinuteClose.loc[today]
        
    #     price_diff = close - _open
    #     price_diff[price_diff >= 0] = 1
    #     price_diff[price_diff < 0] = -1
        
    #     price_up = np.mean(price_diff[price_diff == 1] * price)
    #     price_down = np.mean(-price_diff[price_diff == -1] * price)
        
    #     ratio = price_up / price_down
        
    #     return ratio
        

