import os

import pandas as pd

sta_path = '/dfs/user/015585/20250423_财汇hearsay数据/衍生结果/'
df = pd.DataFrame()
file_list = os.listdir(sta_path)
file_list.sort()

for i in file_list:
    print(i)
    df_date = pd.read_pickle(f'{sta_path}{i}')
    df = df.append(df_date)
df = df.sort_values(['dt' ,'Ticker', 'medianame'])

sta_count = df.reset_index().groupby(['dt']).apply(lambda x : len(set(x['Ticker'])))
'''
数据虽然20230101起，但覆盖度太低，2023年上半年覆盖度在100只以内，下半年在100-600，2024年也仅仅500-1000，无法衍生因子
'''



