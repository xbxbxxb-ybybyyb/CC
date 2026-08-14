import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
import sys
s = FactorData()

df_portfolio = pd.read_pickle('/data/user/015585/01-因子挖掘/20250619-基金持仓/file/portfolio_2010_202309.pkl')
df_basicinfo = s.get_factor_value('WIND_ChinaMutualFundDescription')

'''
1、基金数量
基金总数、股票型/混合型基金数量

2、覆盖率
总体覆盖率：统计16-19年，前一年所有报告中，涉及neptune策略对应标的的基金数量
统计有覆盖、有20只以上覆盖、占基金净值比例百1以上超过20只的覆盖率
分期覆盖率：统计16-19年，离当前日期最近的报告期中，涉及neptune策略对应标的的基金数量
'''
# =============基金数量==================
print('记录在册的基金总数：',len(df_basicinfo))
print('目前未到期的基金总数：', len(df_basicinfo[df_basicinfo['F_INFO_MATURITYDATE'].isna()]))
print(df_basicinfo[df_basicinfo['F_INFO_MATURITYDATE'].isna()].groupby('F_INFO_FIRSTINVESTTYPE').count()['F_INFO_WINDCODE'])

# =============总体覆盖率================
df_neptune = pd.read_hdf('/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
df_portfolio['year'] = df_portfolio['F_PRT_ENDDATE'].map(lambda x : int(x[:4]))
df_count = df_portfolio.groupby(['year','S_INFO_STOCKWINDCODE']).apply(lambda x : len(set(x['S_INFO_WINDCODE']))).to_frame(name='count')
df_count_baiyi = df_portfolio[df_portfolio['F_PRT_STKVALUETONAV'] >= 1].groupby(['year','S_INFO_STOCKWINDCODE']).apply(lambda x : len(set(x['S_INFO_WINDCODE']))).to_frame(name='count_1%')

df_neptune['year_last'] = df_neptune.index.get_level_values(0).map(lambda x : x.year-1)

df_neptune_addcount = pd.merge(df_neptune.reset_index(), df_count.reset_index(), left_on=['Ticker','year_last'], right_on=['S_INFO_STOCKWINDCODE','year'], how='left')
df_neptune_addcount = pd.merge(df_neptune_addcount.drop(['year','S_INFO_STOCKWINDCODE'], axis=1), df_count_baiyi.reset_index(), left_on=['Ticker','year_last'], right_on=['S_INFO_STOCKWINDCODE','year'], how='left')
df_neptune_addcount['count'] = df_neptune_addcount['count'].fillna(0)
df_neptune_addcount['count_1%'] = df_neptune_addcount['count_1%'].fillna(0)
print('16-19，neptune有基金覆盖的比率：',df_neptune_addcount[df_neptune_addcount['count'] > 0].shape[0] / df_neptune_addcount.shape[0])
print('16-19，neptune有20只以上基金覆盖的比率：',df_neptune_addcount[df_neptune_addcount['count'] > 20].shape[0] / df_neptune_addcount.shape[0])
print('16-19，neptune有20只以上基金覆盖，且在基金净值占比超过1%的比率：',df_neptune_addcount[df_neptune_addcount['count_1%'] > 20].shape[0] / df_neptune_addcount.shape[0])






