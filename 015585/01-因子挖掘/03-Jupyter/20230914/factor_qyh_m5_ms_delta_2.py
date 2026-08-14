# dtj
# mean/std，2日均值
# -0.04,24
# roll_3_mean_xly：15
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_ms_delta_2'
def factor_qyh_m5_ms_delta_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 4.78,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    vol_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    vol_data['mean'] = vol_data.mean(axis=1)
    vol_data['std'] = vol_data.std(axis=1)
    vol_data['ms'] = vol_data['mean'] / vol_data['std']
    # vol_data['cv_delta'] = vol_data['cv'] - vol_data['cv'].unstack().shift(1).stack()

    res = pd.DataFrame(vol_data['ms'])
    res['ms'] = np.log(res['ms'].unstack().rolling(2,2).mean().stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res