import numpy as np
import pandas as pd
import os
import sys
'''
因为每个个股可能同一时间段属于多个主题，选取 europa样本个股关联度最高的主题/最高的N个主题 的平均概念热度值，作为个股的“所属行业热度值”
1、拼接每个主题的热度指数，用主题上线时间切分，只取“该主题上线后的热度指数”
index = dt themeid
columns = 主题上线时间 热度指数值
2、拼接个股和主题的关联度
index = dt Ticker
columns = themeid 关联度 热度 主题上线时间
'''
#
theme_basicinfo = pd.read_pickle('/data/user/015585/01-因子挖掘/20240318-通联概念热度/file_ori/theme_basicinfo.pkl')
theme_basicinfo['insertTime'] = theme_basicinfo['insertTime'].apply(lambda x : pd.Timestamp(x))
theme_basicinfo['updateTime'] = theme_basicinfo['updateTime'].apply(lambda x : pd.Timestamp(x))
# 拼接主题的热度指数
# path1 = '/dfs/user/015585/20240318-通联概念热度/file_ori/theme_heat/'
# theme_file_list = list(os.listdir(path1))
# theme_file_list = [x for x in theme_file_list if x.endswith('.pkl')]
# print('共有{}个主题'.format(str(len(theme_file_list))))
# res_theme_heat = pd.DataFrame()
# for theme_file in theme_file_list:
#     theme = theme_file[:-4]
#     df_theme = pd.read_pickle(path1 + theme_file)
#     df_theme = df_theme[['themeID', 'hotScore', 'effectiveTime']]
#     df_theme = df_theme.rename(columns={'hotScore': 'heat', 'effectiveTime': 'dt_time'})
#     df_theme['dt_time'] = df_theme['dt_time'].apply(lambda x: pd.Timestamp(x))
#     df_theme['dt'] = df_theme['dt_time'].apply(lambda x: x.date())
#     df_theme = pd.DataFrame(df_theme.groupby(['dt', 'themeID'])['heat'].mean())
#     df_theme.columns = ['heat']
#     res_theme_heat = pd.concat([res_theme_heat,df_theme],axis = 0)
#     sys.stdout.write('\r' + str(len(res_theme_heat)))
#     sys.stdout.flush()
# res_theme_heat = pd.merge(res_theme_heat.reset_index(),theme_basicinfo[['themeID','insertTime']],left_on = 'themeID',right_on = 'themeID',how = 'left')
# res_theme_heat['dt'] = res_theme_heat['dt'].apply(lambda x : pd.Timestamp(x)) # 强制type为datetime64
# res_theme_heat.to_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/res_theme_heat.pkl')
# 拼接个股和主题的关联度
res_theme_heat = pd.read_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/res_theme_heat.pkl')
path2 = '/dfs/user/015585/20240318-通联概念热度/file_ori/correlation/'
correlation_file_list = list(os.listdir(path2))
correlation_file_list = [x for x in correlation_file_list if x.endswith('.pkl')]
print('共有{}个个股被考察关联度'.format(str(len(correlation_file_list))))
res_correlation = pd.DataFrame()
for correlation_file in correlation_file_list:
    correlation_name = correlation_file[:-4]
    df_correlation = pd.read_pickle(path2 + correlation_file)[['themeID', 'statDate', 'secID','score']]
    df_correlation = df_correlation.rename(columns={'statDate': 'dt', 'secID': 'Ticker','score':'corr'})
    df_correlation['dt'] = df_correlation['dt'].apply(lambda x: pd.Timestamp(x).date())
    df_correlation['Ticker'] = df_correlation['Ticker'].apply(lambda x : x.replace('XSHE','SZ').replace('XSHG','SH'))
    df_correlation = df_correlation.sort_values(['dt','Ticker','corr'],ascending = [True,True,False]).set_index(['dt','Ticker'])
    df_correlation['corr_rank'] = df_correlation.groupby(['dt','Ticker'])['corr'].rank(ascending = False)
    # df_correlation = df_correlation[df_correlation['corr_rank'] <=3 ] # 只取相关度最高的3个主题，否则df太大
    #
    res_correlation = pd.concat([res_correlation,df_correlation],axis = 0)
    sys.stdout.write('\r' + str(len(res_correlation)))
    sys.stdout.flush()
#
res_correlation.to_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/correlation_all.pkl') # all代表不限定3个主题
res = pd.merge(res_correlation.reset_index(),res_theme_heat,left_on=['dt','themeID'],right_on=['dt','themeID'],how = 'left')
res = res.set_index(['dt','Ticker'])
res = res.sort_values(['dt','Ticker','corr'],ascending = [True,True,False])
res.to_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/res_all.pkl')
# 统计概念从19-24年成分股情况
'''
定义：如果一个个股的所属概念在个股的所有概念中相关度排名前3，则认为该个股属于该概念
1、5年里，每个概念每日成分股的均值
2、5年里，每个概念累计进入/流出股票数量的均值（算法：对每个概念，计算每天的进入/流出数量，求当日所有概念和，求每日和，除以这段时间的总概念数
# '''
# print('每个概念每日成分股的均值(只考虑当日有成分股的概念):')
# print(res.groupby(['dt','themeID'])['corr'].count().mean())
#
# res = res.reset_index().set_index(['dt','Ticker','themeID'])
# res['tmp_count'] = 1
# res['tmp_count_y'] = res['tmp_count'].unstack().unstack().shift(1).stack().stack()
# res['tmp_count_y'] = res['tmp_count_y'].fillna(0)
# res['tmp_delta_t'] = res['tmp_count'].unstack().unstack().shift(-1).stack().stack()
# res['tmp_delta_t'] = res['tmp_delta_t'].fillna(0)
# print('每个概念累计新增的均值:')
# print(res[res['tmp_count_y']==0].groupby(['dt','themeID'])['Ticker'].count().sum() / len(res['themeID'].unique()))
# print('每个概念累计流出的均值:')
# print(res[res['tmp_count_t']==0].groupby(['dt','themeID'])['Ticker'].count().sum() / len(res['themeID'].unique()))