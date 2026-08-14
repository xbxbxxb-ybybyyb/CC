import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# 北向资金：最近5日/20日持股市值占股票市值比例，缺失值直接用中位数填充
'''

'''
#
factor_name = 'qyh_md_20231130_test6'
def factor_qyh_md_20231130_test6(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:26.2,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -80)[0])
    ind_data = IO.read_data([start_date_, end_date], columns=['amt','free_float_shares'],
                            alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    ind_data['Industry'] = IO.read_data([start_date_, end_date], columns=['Industry'],
                                        alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231128_北向资金/file/north_funds.pkl')
    df_ori['qty'] = df_ori['qty'].unstack().fillna(method = 'ffill',limit = 20).stack()
    ind_data[factor_name] = df_ori['qty'] / ind_data['free_float_shares']
    para = 20
    ind_data[factor_name] = ind_data[factor_name].unstack().rolling(para,5).mean().stack()
    #
    # ind_data = ind_data.reset_index().set_index(['dt', 'Industry', 'Ticker'])
    # tmp = ind_data.groupby(['dt', 'Industry'])[factor_name].mean()
    # ind_data.loc[ind_data[factor_name].isna(), factor_name] = tmp
    # ind_data = ind_data.reset_index().set_index(['dt','Ticker'])
    # -------------------------------------------------------------------------------------------------------------------
    return ind_data[[factor_name]]
