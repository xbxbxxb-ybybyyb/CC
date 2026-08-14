from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
class VwapmaLowDiffSkew_13h(BaseFactor):
    '''
    * 因子名称：VwapmaLowDiffSkew_13h
    * 描述：滚动成交均价与最低价之差的偏度
    * 因子逻辑：滚动成交均价可视为市场的平均持仓成本，它与最低价的距离呈右厚尾分布说明多头观察到多次大的亏损，根据前景理论，亏损状态下投资者风险偏好程度更高，股价有较强支撑
    * 因子参数：分钟数据的成交额、成交量、最低价
    * 作者：何丰敬
    * 日期：2019.8.14
    * 函数修改日期:尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.low_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        vwapma = a.cumsum() / v.cumsum()  # 滚动成交均价
        return (vwapma - l).skew()
