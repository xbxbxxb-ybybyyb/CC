# dtj
# 5min涨幅与成交量的corr均值，5日平均
# -0.04,10
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_corr_pct_amt_5'
def factor_qyh_m5_corr_pct_amt_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    pct_data = close_data / open_data - 1
    amt_data_array = amt_data.values
    pct_data_array = pct_data.values
    res_array = []
    for i in range(len(amt_data_array)):
        x = amt_data_array[i]
        y = pct_data_array[i]
        x_y_norm = (np.isnan(x)|np.isnan(y))==False
        x = x[x_y_norm]
        y = y[x_y_norm]
        res_array.append(np.corrcoef([x, y])[0][1])

    res = pd.DataFrame(res_array,columns = [factor_name],index = amt_data.index)\
        .unstack().rolling(20,5).mean().stack()
    # res = pd.DataFrame(amt_data.T.corrwith(pct_data.T,method = 'spearman')).unstack().rolling(20,1).mean().stack()
    # res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res