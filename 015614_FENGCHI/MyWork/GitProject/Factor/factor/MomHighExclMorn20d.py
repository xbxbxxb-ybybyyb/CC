from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MomHighExclMorn20d(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.amt',
                    'FactorData.Basic_factor.dealnum']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 20
    minute_lag=0
    # fix_times = ["1500"]
    reform_window = 20
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    '''
    *因子名：MomHighExclMorn20d
    *因子功能描述：过去20天高单笔成交额市场下的非早盘复合收益率
    *因子参数：[MinuteClose]: 分钟收盘价
               [amt]: 成交额
               [dealnum]: 成交笔数
               [n]: 回看天数

    *作者：周璇
    *因子创建日期：2019.1.23
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
        
    '''


    # def definition(self, MinuteClose,amt,dealnum,n):
        
    #     re = self.minute_help(self.minute,'ReExclMornHelp',MinuteClose)

    #     D = amt/dealnum
    #     D[np.isinf(D)] = np.nan
    #     D_median = D.rolling(window=n,min_periods=int(n*0.8)).median()
    #     M_high = pd.DataFrame(index=amt.index[2*n:],columns=amt.columns)
    #     for date in amt.index[2*n:]:
    #         D_temp = D.loc[:date].iloc[-n:]
    #         D_med = pd.DataFrame([D_median.loc[date].values.tolist()]*n,index=D_temp.index,columns=D_temp.columns)
    #         higher = D_temp>=D_med
    #         M_high.loc[date] = (((re.loc[D_temp.index])[higher]+1).prod(axis=0)-1).values
    #     M_high=M_high.convert_objects(convert_numeric=True)

    #     return -M_high

    def calc_single(self, database):

        amt = database.depend_data['FactorData.Basic_factor.amt']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        
        D = pd.DataFrame(amt.values/dealnum.values, index=amt.index, columns=amt.columns)
        D[np.isinf(D.astype(float))] = np.nan
        D_median = D.median()
        # D_median = D.rolling(window=20,min_periods=int(20*0.8)).median().iloc[-1,:]

        re = close.iloc[239]/close.iloc[60]-1
        flag = (D.iloc[-1,:] >= D_median)
        re[~flag] = np.nan

        R = 1. + re * flag

        return R


    def  reform(self, temp_result):
        A = temp_result.rolling(20,1).apply(np.nanprod) - 1.
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return -A