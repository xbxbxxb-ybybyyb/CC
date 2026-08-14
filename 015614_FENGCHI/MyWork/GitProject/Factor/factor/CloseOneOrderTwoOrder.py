from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




    # * 因子名：CloseOneOrderTwoOrder_13h
    # * 描述：Close一阶变化率和二阶变化率30分钟方差的相关性的负数
    # * 逻辑：一阶、二阶变化率方差相关性为负表明反转，有获利机会
    # * 因子参数：分钟数据的收
    # * 作者：孔剑阳
    # * 日期：2019.7.23
    # * 函数修改日期：尚未修改
    # * 修改人：尚未修改
    # * 修改原因：尚未修改

class CloseOneOrderTwoOrder(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_adj_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 1
    minute_lag=1
    # fix_times = ["1300"]
    reform_window = 3

    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        OneOrder = MinuteClose.rolling(window=10).mean()
        # .pct_change(1)
        OneOrder = OneOrder.diff()/OneOrder.shift()
        TwoOrder = OneOrder.rolling(window=3).mean().diff(1)
        # factor = -OneOrder.rolling(30).std().corrwith(TwoOrder.rolling(30).std())
        factor = Util.array_coef(OneOrder.rolling(30).std(), TwoOrder.rolling(30).std())
        return -factor


    def  reform(self, temp_result):
        A = temp_result.rolling(3).mean()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A
        