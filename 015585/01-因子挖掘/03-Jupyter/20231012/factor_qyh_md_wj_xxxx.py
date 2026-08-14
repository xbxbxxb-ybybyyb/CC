import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_wj_xxxx'
# dtj,zcz
def factor_qyh_md_wj_xxxx(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.01,'data':['MD','minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -100)[0])
    close = IO.read_data([start_date, end_date], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    open = IO.read_data([start_date, end_date], alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    md_data = IO.read_data([start_date, end_date],columns = ['pre_close'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # close_day = md_data.loc[close.index, 'close']
    bid_pct = (close - open).divide((1e-3 + close + open), axis=0)
    selectcols = ['m1400', 'm1405', 'm1410', 'm1415', 'm1420', 'm1425', 'm1430',
                  'm1435', 'm1440', 'm1445', 'm1450', 'm1455']
    # selectcols = ['m1430',
    #               'm1435', 'm1440', 'm1445', 'm1450', 'm1455']
    md_data[factor_name] = (bid_pct[selectcols]).mean(1)
    # -------------------------------------------------------------------------------------------------------------------
    return md_data[[factor_name]]
