# coding: utf-8
# Author：fengchi863
# Date ：2023/3/29 10:57

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()


def factor_fc_abn_amt_ret(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_abn_amt_ret'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -65)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['amt', 'pct_chg', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'pct_chg'] = md_data.loc[
                                                                                                                    (md_data['stock_code'].str.startswith('3')) & (
                                                                                                                            md_data['datelist'] >= '20200824'), 'pct_chg'] / 2

    amt = md_data['amt']
    pct_chg = md_data['pct_chg']

    abn_amt = (amt.unstack().rolling(window=60, min_periods=1).mean() + amt.unstack().rolling(window=60, min_periods=1).std() * 0.66).stack(dropna=False)
    abn_amt = abn_amt[amt.index]
    pct_chg[amt < abn_amt] = 0
    ret = pct_chg.unstack().rolling(60).sum().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret
    return factor_df