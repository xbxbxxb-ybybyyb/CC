from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrVWAPdt(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_adj_minute',
                    'FactorData.Basic_factor.volume_adj_minute', 
                    'FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.open_adj_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 1
    minute_lag=1
    # fix_times = ["1300"]
    # reform_window = 5



    '''
    * 因子名：CorrVWAPdt_13h
    * 描述：前一日VWAP与High的约化距离(VWAP-High)/Open与VWAP的相关性
    * 逻辑：单日的High-VWAP的差与VWAP相关性越小，表明反转信号强。注：代码中VWAP-High省却了负号
    * 因子参数：分钟数据的收，换手，体量
    * 作者：孔剑阳
    * 日期：2019.8.1
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_adj_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']

        MinuteVWAP = MinuteTurnover / MinuteVolume
        dt = (MinuteVWAP - MinuteHigh)/MinuteOpen
        alpha = Util.array_coef(dt,MinuteVWAP) 
        return alpha
