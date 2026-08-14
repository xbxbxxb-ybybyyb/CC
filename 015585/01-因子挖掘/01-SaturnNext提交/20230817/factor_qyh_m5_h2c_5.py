
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_h2c_5'
def factor_qyh_m5_h2c_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.03,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    high_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/high.h5')
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    close_data['high'] = high_data.max(axis=1)
    for col in close_data.columns:
        close_data[col] = (close_data['high'] - close_data[col]) / close_data['high']
    close_data = close_data.drop(['high'],axis=1)
    close_data = close_data * amt_data
    res1 = close_data.sum(axis=1).unstack().rolling(5,2).sum().stack()
    res2 = amt_data.sum(axis=1).unstack().rolling(5,2).sum().stack()
    res2[res2 < 10] = np.nan
    res = pd.DataFrame(res1 / res2)
    res.columns = [factor_name]
    # res = pd.DataFrame(amt_data.T.corrwith(pct_data.T,method = 'spearman')).unstack().rolling(20,1).mean().stack()
    # res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res