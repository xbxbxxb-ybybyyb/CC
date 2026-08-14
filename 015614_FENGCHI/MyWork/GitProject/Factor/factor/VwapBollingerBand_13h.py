from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VwapBollingerBand_13h(BaseFactor):
    """
    * 因子名：VwapBollingerBand_13h
    * 因子功能描述：前一小时上布林带以上的偏离之和除以上布林带高度之和.是一个反转因子，值大则看跌
    * 因子参数： MinuteTurnover, MinuteVolume
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        turnover = a.iloc[-60:]
        volume = v.iloc[-60:]
        vwap = turnover / volume
        mean_vwap = vwap.rolling(window=10, min_periods=1).mean()
        std_vwap = vwap.rolling(window=10, min_periods=1).std()
        boll_up = mean_vwap + np.ones(std_vwap.shape) * 2 * std_vwap
        up_range = vwap - boll_up
        uprange_pct = (up_range[up_range > np.zeros(up_range.shape)] / boll_up)
        ratio = -uprange_pct.sum()

        return ratio