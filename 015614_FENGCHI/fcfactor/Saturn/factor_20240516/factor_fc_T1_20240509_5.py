# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240509_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VOLUME_MED_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VOLUME_MED_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['SELL_VOLUME_MED_ORDER'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日中户卖出总量相对于前一日的差异
    =====>>>> 24.208 0.066 21121.5652468867 47742.13631590607 fc_T1_20240321_1，xly_newsat_md3_3_0，xly_newsat_md10 0.73，0.6524，0.5734
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df