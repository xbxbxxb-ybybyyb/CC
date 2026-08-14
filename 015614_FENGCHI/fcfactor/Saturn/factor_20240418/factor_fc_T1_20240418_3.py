# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240418_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_TRADES_SMALL_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_TRADES_SMALL_ORDER'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['SELL_TRADES_SMALL_ORDER'].unstack().rolling(3, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2日卖出小单的单数相对于近3日卖出小单单数的比值
    =====>>>> 24.583 0.04 840.3933192532655 1698.0557703840507 fc_T1_20240321_13，fc_T1_20240321_3，fc_T1_20240321_11 0.7674，0.6272，0.607
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df