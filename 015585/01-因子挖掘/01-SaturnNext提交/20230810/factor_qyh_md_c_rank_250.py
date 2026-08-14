
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_c_rank_250'
def factor_qyh_md_c_rank_250(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.16,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -500)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['close'] = f_data['close'].unstack().fillna(method='ffill',limit=200).stack()
    import bottleneck as bn
    res = pd.DataFrame(bn.move_rank(f_data['close'].unstack(),window = 250,min_count = 50,axis=0))
    res.index = f_data['close'].unstack().index
    res.columns = f_data['close'].unstack().columns
    res = pd.DataFrame(res.stack())
    res.columns = [factor_name]
    f_data = pd.DataFrame(res[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。