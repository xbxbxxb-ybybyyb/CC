from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinuteDCDTA5d(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.amt_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        # MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        # MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']


        # cr = MinuteClose.pct_change()
        # tr = (MinuteTurnover)[MinuteTurnover!=0].pct_change()
        # df = tr.iloc[-15:].corrwith(cr.iloc[-15:])
        # return df.rank(ascending=False, pct=True)

        # cr = close.pct_change()
        cr = close.diff()/close.shift(1)
        # cr = (close - close.shift()) / close.shift()
        
        
        # flag = (amt.values>0)
        # print(flag.shape)
        # print(flag.dtype)
        # print(flag)
        flag = pd.DataFrame((amt.values>0.), index=amt.index, columns=amt.columns)
        # tr=tr.pct_change()
        tr = amt[flag]
        # tr = (tr - tr.shift()) / tr.shift()
        tr = tr.pct_change()

        # tr = tr.diff()/tr.shift(1)
        
        df = Util.array_coef(tr.iloc[-15:,:], cr.iloc[-15:,:])
        df = df.rank(ascending=False, pct=True,)
        return df

    def  reform(self, temp_result):
        A = temp_result.rolling(window=5, min_periods=1).mean()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A
