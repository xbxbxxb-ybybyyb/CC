# coding: utf-8
# Author：fengchi863
# Date ：2023/4/13 21:43

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_pct7_120(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    factor_name = 'fc_pct7_120'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -150)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['pct_chg'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data.loc[((md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824')) | md_data['stock_code'].str.startswith('68'), 'pct_chg'] = \
        md_data.loc[((md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824')) | md_data['stock_code'].str.startswith('68'), 'pct_chg'] / 2

    flag = md_data['pct_chg'].unstack() > 7
    ret = flag.rolling(120).sum().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret
    return factor_df