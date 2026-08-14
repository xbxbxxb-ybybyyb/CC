import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_days_listdate'
# 上市时间距离
def factor_qyh_days_listdate(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -600)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    from xquant.thirdpartydata.factordata import FactorData
    FD = FactorData()
    df_info = FD.get_factor_value('WIND_AShareDescription', factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE'])
    df_ori = pd.merge(df_ori.reset_index(), df_info, left_on='Ticker', right_on='S_INFO_WINDCODE')
    df_ori['S_INFO_LISTDATE'] = df_ori['S_INFO_LISTDATE'].apply(lambda x : pd.Timestamp(str(x)))
    df_ori[factor_name] = (df_ori['dt'] - df_ori['S_INFO_LISTDATE']).apply(lambda x:x.days)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name,'dt','Ticker']].set_index(['dt','Ticker'])
