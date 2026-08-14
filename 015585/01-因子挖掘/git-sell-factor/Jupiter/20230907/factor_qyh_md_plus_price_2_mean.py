
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
def factor_qyh_md_plus_price_2_mean(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='qyh_md_plus_price_2_mean'

    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0.0012, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close','high','low','pre_close']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['plus'] = 2 * f_data['close'] - f_data['high'] - f_data['low']
    f_data['plus'] = f_data['plus'] / f_data['pre_close']
    # f_data[factor_name] = f_data['plus'].unstack().rolling(2,1).mean().stack()
    f_data[factor_name] = (f_data['plus']*3 + f_data['plus'].unstack().shift(1).stack()*2)/5
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。