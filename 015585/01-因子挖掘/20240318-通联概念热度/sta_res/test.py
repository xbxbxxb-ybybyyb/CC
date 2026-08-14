import pandas as pd
## 个股所属概念的准确度
# theme_basicinfo = pd.read_pickle('/data/user/015585/01-因子挖掘/20240318-通联概念热度/file_ori/theme_basicinfo.pkl')
# path2 = '/dfs/user/015585/20240318-通联概念热度/file_ori/correlation/'
# correlation_file = '002229.pkl'
# df_correlation = pd.read_pickle(path2 + correlation_file)[['themeID', 'statDate', 'secID','score']]
# df_correlation = pd.merge(df_correlation,theme_basicinfo[['themeID','themeName']],left_on = 'themeID',right_on = 'themeID')
# df_correlation = df_correlation.sort_values(['statDate','score'],ascending = [True,False])
# res_correlation = df_correlation.groupby('statDate')['themeName'].apply(lambda x : list(x))

## 概念中的个股情况
