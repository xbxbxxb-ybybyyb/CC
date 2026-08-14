# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 14:27

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_dis_pct_ma10(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    factor_name='fc_dis_pct_ma10'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -15)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['amt', 'pct_chg', 'open', 'close', 'high', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['open'] = md_data['open'] * md_data['adjfactor']
    md_data['close'] = md_data['close'] * md_data['adjfactor']
    md_data['high'] = md_data['high'] * md_data['adjfactor']

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data['ma10'] = md_data['close'].unstack().rolling(10).mean().stack()
    md_data['dis_pct_ma10'] = md_data['close'] / md_data['ma10'] - 1
    md_data.loc[((md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824')) | md_data['stock_code'].str.startswith('68'), 'dis_pct_ma10'] = \
        md_data.loc[((md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824')) | md_data['stock_code'].str.startswith('68'), 'dis_pct_ma10'] / 2

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['dis_pct_ma10']
    return factor_df