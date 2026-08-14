# 逻辑：5日amt的cv
# -0.03,7
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_amt_5_cv'
def factor_qyh_md_amt_5_cv(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.78,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['amt']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['mean5'] = f_data['amt'].unstack().rolling(5,2).mean().stack()
    f_data['std5'] = f_data['amt'].unstack().rolling(5,2).std().stack()
    f_data['mean5'] = f_data['mean5'].apply(lambda x: np.nan if abs(x) <= 0.0001 else x)#最近停牌或其他问题的，作为0处理
    f_data['mean5'] = f_data['mean5'].unstack().fillna(method='ffill',limit=20).stack()
    f_data['std5'] = f_data['std5'].apply(lambda x: np.nan if abs(x) <= 0.0001 else x)#最近停牌或其他问题的，作为0处理
    f_data['std5'] = f_data['std5'].unstack().fillna(method='ffill',limit=20).stack()
    f_data[factor_name] = f_data['std5'] / f_data['mean5']
    f_data[factor_name] = f_data[factor_name] - f_data[factor_name].unstack().shift(1).stack()
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。