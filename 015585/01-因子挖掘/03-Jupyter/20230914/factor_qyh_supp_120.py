import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'factor_qyh_supp_120'
import sys
#
# 120日压力筹码占比，即在次日涨停价上方的成交额占比
# 纯粹120日：0.016，14
# 在接近次日涨停价 到 上浮10%的区间：-0.03，
# 把上述区间考虑线性加权，离得越近的成交量认为越有说服力：
def factor_qyh_supp_120(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    res_df = pd.read_pickle('/data/user/015585/01-因子挖掘'
                            '/03-Jupyter/20230914/factor_qyh_presu_120_new.pkl')
    start_date = int(s.tradingday(str(start_date), -5)[0])
    # df_ori = IO.read_data([start_date, end_date],
    #                       columns=['pct_chg'],
    #                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['pct20'] = df_ori['pct_chg'].unstack().rolling(20,10).mean().stack()
    # df_ori['median'] = df_ori['pct20'].unstack().median(axis=1)
    # df_ori['is_up'] = df_ori['pct20'] > df_ori['median']
    res_df = res_df.unstack().shift(-1).stack()
    res_df = pd.DataFrame(res_df)
    res_df.columns = [factor_name]
    # res = pd.concat([df_ori['is_up'],res_df[factor_name]],axis=1)
    # res[factor_name] = res[factor_name] * res['is_up']
    # -------------------------------------------------------------------------------------------------------------------
    return res_df[[factor_name]]
