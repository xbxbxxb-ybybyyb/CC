# -*- coding: utf-8 -*-
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 前日收盘价 / 10日最低价 - 1
# -0.081,38
# wj_last10_bbi:30
def factor_qyh_md_relaprice_10(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='qyh_md_relaprice_10'

    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0.1, 'data':['MD']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -30)[0])  #向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_,end_date],columns = ['low','close']
                           ,alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['zcz'] = (((md_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                         md_data.reset_index()['dt'] >= '2020-08-24'))
                     | (md_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    md_data['low5'] = md_data['low'].unstack().rolling(10,5).min().stack()
    md_data[factor_name] = md_data['close'] / md_data['low5'] - 1
    md_data.loc[md_data['zcz'] == 1,factor_name] = md_data[factor_name]/2
    # -------------------------------------------------------------------------------------------------------------------
    return pd.DataFrame(md_data[factor_name])
