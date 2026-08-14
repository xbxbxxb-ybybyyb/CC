# dtj
# mean/std，2日均值
# -0.04,24
# roll_3_mean_xly：15
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_ms_delta_2_update'
def factor_qyh_m5_ms_delta_2_update(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 4.79,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -60)[0])
    vol_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    vol_data['mean'] = vol_data.mean(axis=1)
    vol_data['mean'] = vol_data['mean'].apply(lambda x:round_(x,5))
    vol_data['std'] = vol_data.std(axis=1)
    vol_data['std'] = vol_data['std'].apply(lambda x:round_(x,5))
    vol_data['ms'] = vol_data['mean'] / vol_data['std']
    vol_data['ms'] = vol_data['ms'].apply(lambda x: 10000 if x > 10000 else x if x > -10000 else -10000)
    res = pd.DataFrame(vol_data['ms'])
    res['ms'] = np.log(res['ms'].unstack().rolling(2,2).mean().stack()+1)
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res