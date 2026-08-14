# 新闻全局统计
import os
import pandas as pd
#

path_news_data = '/dfs/group/800463/data/news_data/news_data_combo/'
file_list = os.listdir(path_news_data)
file_list = [x for x in file_list if '.pkl' in x and x >= '20160101.pkl' and x <= '20221231.pkl']
file_list.sort()
news_df = pd.DataFrame()
for file in file_list:
    print(file)
    df = pd.read_pickle(path_news_data + file, compression='gzip')
    df = df[df['Ticker'].notna()][['dt','Ticker','id','resource','is_value_by_time']]
    df = df[~df['Ticker'].str.contains('HK')]
    news_df = news_df.append(df)
news_df.to_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl',compression = 'gzip')