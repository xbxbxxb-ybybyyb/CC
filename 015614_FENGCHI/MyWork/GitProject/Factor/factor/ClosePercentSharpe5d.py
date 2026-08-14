from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time
from collections import Counter




class ClosePercentSharpe5d(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute',]    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
   
    '''
    *因子名：ClosePercentSharpe5d
    *因子功能描述：收盘价百分比5日sharpe
    *因子参数：[MinuteClose]: 分钟收盘价
               [n]: 回看天数

    *作者：周璇
    *因子创建日期：2019.5.21
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
        
    '''
    


    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']

        # print(close.shape)
        # for date in datelist:
        #     close = MinuteClose.loc[date]
        close_arr = close.values
        # print(close.shape)
        result = np.array([np.nan]*close.shape[1])
        for j in range(close.shape[1]):
            mylist = close_arr[:,j]
            if ~np.isnan(close_arr[-1,j]) and Counter(np.isnan(mylist))[0]>=200:
                ind = np.where(~np.isnan(mylist))[0]
                sort = np.sort((mylist)[ind])
                if close_arr[-1,j]<sort[0]:
                    result[j] = (close_arr[-1,j]-sort[0])/abs(sort[0])
                elif close_arr[-1,j]>=sort[-1]:
                    result[j]=1+(close_arr[-1,j]-sort[-1])/abs(sort[-1])
                else:
                    bigger_this_data = np.where(sort>=close_arr[-1,j])[0]
                    result[j] = (bigger_this_data[0]+1)/(len(sort)+1)
        ClosePercent = pd.Series(result, index = close.columns)

        ClosePercent[~np.isfinite(ClosePercent)]=np.nan

        # ClosePercent = close.rank().iloc[-1,:] / close.shape[0]

        return ClosePercent


    def  reform(self, temp_result):
        A = temp_result.rolling(5,4).mean() / temp_result.rolling(5,4).std()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return -A