# -*- coding: utf-8 -*-
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
import numpy as np
import decimal
def round_(x, n=0):
    if n>0:
        res=float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1'%('0'*(n-1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res=int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

# 提交
# 过去120日的wvad
def factor_wj_20231221_1(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='wj_20231221_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0, 'data':['MD']}
    start_date_ = int(s.tradingday(str(start_date), -180)[0])  #向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_,end_date],
                           columns=['close', 'open', 'high', 'low','volume'],
                           alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['wvad'] = ((md_data['close'] - md_data['open']+1e-3)/(md_data['high'] - md_data['low']+1e-3) * md_data['volume']).apply(lambda x: round_(x,10))
    md_data[factor_name] = md_data['wvad'].rolling(120,1).mean().apply(lambda x: round_(x,10))
    tmp_df = (md_data['high'] - md_data['low']+1e-3) * md_data['volume']
    index_nan = tmp_df[tmp_df.abs() < 1e-10].index.tolist()
    md_data.loc[index_nan, factor_name] = np.nan
    # -------------------------------------------------------------------------------------------------------------------
    return md_data[[factor_name]]