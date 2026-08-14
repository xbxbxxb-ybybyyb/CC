# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np

class SwingHighLowPriceCorr(BaseFactor):
    """
    *因子名 : SwingHighLowPriceCorr
    *因子功能描述 : 振幅与当日最高价相关性，振幅与当日最低价相关性，取两者之和

    *因子参数 : swing -- 振幅，low -- 当日最低价， high -- 当日最高价，n -- 计算相关性天数
    *作者 : 徐志鑫
    *因子创建日期 : 2019.02.26
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.swing", "FactorData.Basic_factor.low", "FactorData.Basic_factor.high"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 4

    def calc_single(self, database):
        n = 5
        low = database.depend_data['FactorData.Basic_factor.low']
        high = database.depend_data['FactorData.Basic_factor.high']
        swing = database.depend_data['FactorData.Basic_factor.swing']

        # corr_high = swing.rolling(window=n).corr(high)
        corr_high = Util.array_coef(swing.iloc[-n:], high.iloc[-n:])
        # corr_low = swing.rolling(window=n).corr(low)
        corr_low = Util.array_coef(swing.iloc[-n:], low.iloc[-n:])
        result = corr_high + corr_low
        
        result[np.isinf(result)] = np.nan
        return -result

   
    
