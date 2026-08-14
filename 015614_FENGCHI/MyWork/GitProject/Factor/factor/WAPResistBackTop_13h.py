from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class WAPResistBackTop_13h(BaseFactor):

    '''
    * WAPResistBackTop_13h
    * 描述：45min的High-WAP与WAP-Low的比值的10%分位
    * 逻辑：当WAP离支撑位近，离阻力位远表示涨幅空间越大，反弹越强。选出当日内反弹强度最强的股票。
    * 因子参数：分钟数据的收高低、换手、体量
    * 作者：孔剑阳
    * 日期：2019.10.10
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        h = database.depend_data['FactorData.Basic_factor.high_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        MinuteClose_pct = c / c.shift() - np.ones(c.shape)
        TWAP = c.rolling(45,1).mean()
        HIGH = h.rolling(45,1).max()
        LOW = l.rolling(45,1).min()
        VWAP = (a / v).rolling(45,1).mean()
        WAP = (TWAP +VWAP) / (2 * np.ones(VWAP.shape))
        RankMinute = ((HIGH-WAP)/(WAP-LOW)).rank(axis=1, ascending=False)
        return RankMinute.quantile(0.1)