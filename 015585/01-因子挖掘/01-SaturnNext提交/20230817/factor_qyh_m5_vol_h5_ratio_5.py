
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_vol_h5_ratio_5'
def factor_qyh_m5_vol_h5_ratio_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.15,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    vol_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    vol_data['total'] = vol_data.sum(axis=1)
    res = []
    vol_data_values = vol_data.drop(['total'],axis=1).values
    for i in vol_data_values:
        i.sort()
        res.append(i[-5:].sum())
    vol_data['head5'] = res
    vol_data['ratio'] = vol_data['head5'] / vol_data['total']
    vol_data[factor_name] = vol_data['ratio'].unstack().rolling(5,1).mean().stack()
    res = pd.DataFrame(vol_data[factor_name])
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res