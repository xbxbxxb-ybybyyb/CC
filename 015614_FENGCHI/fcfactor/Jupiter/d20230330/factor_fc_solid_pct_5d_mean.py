# coding: utf-8
# Author：fengchi863
# Date ：2023/3/30 15:54

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_solid_pct_5d_mean(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_solid_pct_5d_mean'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -11)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['close', 'high', 'low', 'open']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    # 实体柱的比例
    md_data['ret'] = (md_data['open'] - md_data['close']).abs() / (md_data['high'] - md_data['low'])
    md_data['ret'] = md_data['ret'].unstack().rolling(5).mean().stack()

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.index.get_level_values(0).strftime('%Y%m%d')
    md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist']>='20200824'), 'ret'] = md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist']>='20200824'), 'ret'] /2

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['ret']
    return factor_df