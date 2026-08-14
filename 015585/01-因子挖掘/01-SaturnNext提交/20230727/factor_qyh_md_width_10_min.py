# -*- coding: utf-8 -*-
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
# dtj
# boll线窗口（4*收盘价20日标准差和20日均价的比例，一般<0.1认为股价会发生变动），
# 因为涨停会导致窗口变大，取10日最小值以获取涨停前的窗口值
# 22,-0.068
# xxx:22
def factor_qyh_md_width_10_min(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='qyh_md_width_10_min'
    import numpy as np
    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0.249, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['mean_10'] = f_data['close'].unstack().rolling(10, 5).mean().stack()
    f_data['std_10'] = f_data['close'].unstack().rolling(10, 5).std().stack()
    f_data['std_10'] = f_data['std_10'].apply(lambda x: 0 if abs(x) <= 0.0001 else x)#标准差接近0的，作为空值处理
    f_data['std_10'].replace(0, np.nan,inplace = True)
    f_data[factor_name] = (4 * f_data['std_10'] / f_data['mean_10'])
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data
