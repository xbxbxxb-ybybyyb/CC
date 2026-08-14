# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 19:50

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()


def weighted_smaller_than_n(series, m=200):
    num = series <= m  # 序列中小于n的次数
    weight = np.arange(1, (22 + 1), 1) / 22
    temp = (num * weight).sum()  # 序列中小于n的加权次数
    return temp

def factor_fc_loser_225(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_loser_225'

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -23)[0])  #向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_,end_date],columns = ['pct_chg']
                           ,alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'pct_chg'] = md_data.loc[
                                                                                                                (md_data['stock_code'].str.startswith('3')) & (
                                                                                                                   md_data['datelist'] >= '20200824'), 'pct_chg'] / 2

    pct_chg = md_data['pct_chg']
    pct_chg = pct_chg.unstack()
    ans = pd.DataFrame(pct_chg.rank(ascending=True, axis=1).values, index=pct_chg.index, columns=pct_chg.columns)
    ret = ans.rolling(22).apply(weighted_smaller_than_n)
    ret = ret.loc[pd.to_datetime(str(start_date)):]

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret.stack()
    return factor_df