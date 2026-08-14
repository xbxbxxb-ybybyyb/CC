from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrVWAPBollingUpDown(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_adj_minute', 
                    'FactorData.Basic_factor.close_adj_minute','FactorData.Basic_factor.amt_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=1
    # fix_times = ["1300"]
    reform_window = 5


    '''
    * 因子名：CorrVWAPBollingUpDown_13h
    * 描述：VWAP与上下Bolling带相关性的最大值（上为正下为负）的五日平均
    * 逻辑：VWAP靠近上下布林带表示超买超卖，是反转信号
    * 因子参数：分钟数据的收，换手，体量
    * 作者：孔剑阳
    * 日期：2019.8.1
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']


        t1=time.time()
        MinuteVWAP = MinuteTurnover / MinuteVolume
        boll = pd.DataFrame(MinuteClose.rolling(10).std().values*2, index=MinuteClose.index, columns=MinuteClose.columns)
        MinuteClose_bolling_up = boll + MinuteClose
        MinuteClose_bolling_do = MinuteClose - boll
        # corr_up = MinuteVWAP.corrwith(MinuteClose_bolling_up)
        corr_up = Util.array_coef(MinuteVWAP, MinuteClose_bolling_up)
        # corr_do = MinuteVWAP.corrwith(MinuteClose_bolling_do)
        corr_do = Util.array_coef(MinuteVWAP, MinuteClose_bolling_do)
        corr = corr_up*(corr_up>corr_do) - corr_do*(corr_do>=corr_up)
        
        return -corr


    def  reform(self, temp_result):
        A = temp_result.rolling(5).mean()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A