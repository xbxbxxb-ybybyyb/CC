import pandas as pd
import IO
import numpy as np
import os
from xquant.factordata import FactorData
import datetime as dt
s = FactorData()
'''
1、个股的过去20个交易日的涨跌幅pearson相关性
2、个股T-1交易日的通联共同概念占比
3、个股T-1是否属于同一中信行业
输入：个股代码、交易日
输出：全市场相关性最高的100只股票
'''
res_correlation = pd.read_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/correlation_all.pkl')
stock = '003027.SZ'
date = '20240221'
n_del_small = 10 # 剔除不需要的概念:10个or以下
start_date_ = int(s.tradingday(date, -40)[0])
end_date_ = int(s.tradingday(date, -2)[0]) # T-1
md_data = IO.read_data([start_date_, end_date_],
                      columns=['pct_chg']
                      , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
## 剔除不需要的概念:10个or以下，以及列表中
theme_basicinfo = pd.read_pickle('/dfs/user/015585/20240318-通联概念热度/file_ori/theme_basicinfo.pkl')
res_correlation_num_T_1 = res_correlation.loc[pd.Timestamp(str(end_date_))].groupby('themeID').count()['corr'].sort_values(ascending = False)
list_small = list(res_correlation_num_T_1[res_correlation_num_T_1 <= n_del_small].index)
list_big = [202159,
141028,
6349363,
388576,
6349494,
8490299,
6349315,
6349562,
6349403,
6349521,
388582,
6349146,
6349261,
23029,
]
list_del = list_small + list_big
# 涨跌幅corr
corr_pct = md_data['pct_chg'].unstack().tail(20).fillna(0).corr()
corr_pct_stock = corr_pct[stock].sort_values(ascending = False)
# T-1的通联共同概念占比
res_correlation_T_1 = res_correlation.loc[pd.Timestamp(str(end_date_))].reset_index()
res_correlation_T_1 = res_correlation_T_1[~res_correlation_T_1['themeID'].isin(list_del)]
res_correlation_T_1 = res_correlation_T_1[res_correlation_T_1['corr'] >= 0.003]
res_correlation_T_1 = res_correlation_T_1.set_index(['Ticker','themeID'])
res_correlation_T_1['is_member'] = 1
res_correlation_T_1 = res_correlation_T_1['is_member'].unstack()
res_common_theme = pd.DataFrame(columns = ['ratio'])
for Ticker in res_correlation_T_1.index: # 此处可以用CORR代替 tmp = pd.DataFrame(res_correlation_T_1.T).fillna(0).corr() tmp[stock].sort_values(ascending = False).head(5)
     num_common_theme_Ticker = (res_correlation_T_1.loc[stock] + res_correlation_T_1.loc[Ticker]).sum()/2
     num_all_theme_Ticker = res_correlation_T_1.loc[stock].sum() + res_correlation_T_1.loc[Ticker].sum() - num_common_theme_Ticker
     res_common_theme.loc[Ticker, 'ratio'] = num_common_theme_Ticker / num_all_theme_Ticker
res_common_theme = res_common_theme.sort_values('ratio',ascending = False)
res_common_theme['rank'] = res_common_theme['ratio'].rank(ascending = False)
# tmp
tmp = res_correlation_T_1.loc['003027.SZ']
tmp = tmp[tmp>0]
print(theme_basicinfo[theme_basicinfo['themeID'].isin(tmp.index)]['themeName'])