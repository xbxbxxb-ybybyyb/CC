# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_7(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VALUE_L'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['MONEYFLOW_PCT_VALUE_L'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨天主力净流入额占比相对于近1个星期的差值
    =====>>>> 13.625 0.041 1.2159414450270696 1.6337210458545541 wj_last_lflow_rate，sss_chip_up_20 0.5536，0.5504
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df