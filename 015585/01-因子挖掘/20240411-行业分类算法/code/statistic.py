import pandas as pd
import IO
import numpy as np
import os
from xquant.factordata import FactorData
import datetime as dt
'''
统计同花顺、wind、通联的一些指标
1、概念总数、每个概念的成分股个数、每个股票的所属概念数
'''
# 通联
tl_correlation = pd.read_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/correlation_all.pkl')
theme_num_tl = len(set(tl_correlation['themeID']))
stocknum_pertheme = tl_correlation.groupby(['dt','themeID'])['corr'].count().mean()
themenum_perstock = tl_correlation.groupby(['dt','Ticker'])['themeID'].count().mean()
print('通联2019-2024','概念总数：{}，每个概念的成分股个数：{}，每个股票的所属概念数：{}'.format(theme_num_tl, stocknum_pertheme, themenum_perstock))
# 同花顺
ths_theme_stock_heat = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock.pkl')
ths_theme_stock_heat = ths_theme_stock_heat[~ths_theme_stock_heat['Ticker'].str.contains('.BJ')]
ths_theme_stock_heat = ths_theme_stock_heat[ths_theme_stock_heat['dt'] >= pd.Timestamp('20190101')]
theme_num_ths = len(set(ths_theme_stock_heat['theme_id']))
stocknum_pertheme_ths = ths_theme_stock_heat.groupby(['dt','theme_id'])['is_theme_stock'].count().mean()
themenum_perstock_ths = ths_theme_stock_heat.groupby(['dt','Ticker'])['theme_id'].count().mean()
print('同花顺2019-2024','概念总数：{}，每个概念的成分股个数：{}，每个股票的所属概念数：{}'.format(theme_num_ths, stocknum_pertheme_ths, themenum_perstock_ths))