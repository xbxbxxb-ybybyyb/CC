import pandas as pd
import numpy as np
import datetime
import os
from xquant.textdata import NewsData
nd = NewsData()
# data_info = nd.getNewsInfoByEntryTime("20240723","07:00","23:59","XNEWS")
def columns_filter(df,col=[]):
    if len(col) > 0:
        df = df[col]
    else:
        col = ['newscode','newssource','author','entrydate','entrytime','newstime',
               'newstimeupdate','hypertitle','newstitle','newsentrytime','summary','symbol','exchange','setype']
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.reindex(columns=col, fill_value=np.nan)
    return df
def del_duplicates(df):# 得到groupby newsid后，count > 1的id集合，和symbol == nan的id集合，删除交集且symbol==nan的部分
    tmp1 = df.groupby('newscode')['newscode'].count()
    list1 = list(set(tmp1[tmp1>1].index))
    df = df[~((df['newscode'].isin(list1)) & (df['symbol'].isna()))]
    return df
def sh_sz_transfer(df):
    df.loc[df['exchange'] == '001003','symbol'] = df.loc[df['exchange'] == '001003','symbol'] + '.SZ'
    df.loc[df['exchange'] == '001002', 'symbol'] = df.loc[df['exchange'] == '001002', 'symbol'] + '.SH'
    return df
def get_content(df):
    df_content = nd.getNewsBody(list(set(df['newscode'].apply(lambda x : str(x)))),"XNEWS")
    df_content['newscode'] = df_content['newscode'].apply(lambda x : int(x))
    df = pd.merge(df,df_content,left_on='newscode',right_on='newscode',how='left')
    return df
def parallel_main(date):
    date = date.strftime('%Y%m%d')
    try:
        df = nd.getNewsInfoByEntryTime(date, "00:00", "23:59", "XNEWS")
        df = columns_filter(df)
        df = del_duplicates(df)
        df = get_content(df)
        df = sh_sz_transfer(df)
        df.to_pickle(save_path + date + '.pkl')
        print(date,len(df),len(df[df['newsBody'].apply(lambda x : len(x) if type(x) == str else x) > 20]))
    except Exception as e:
        error_list.append(date)
        print(date,'error')
        print(e)
    return
#
from joblib import Parallel, delayed
start_date = '20160101'
end_date = '20240630'
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
# date_list去掉删掉已经落地的部分
file_list = os.listdir('/dfs/group/800463/data/news_data/XNEWS/')
file_list = [pd.Timestamp(x.replace('.pkl','')) for x in file_list]
date_list = list(set(date_list) - set(file_list))
date_list.sort()
#
save_path = '/dfs/group/800463/data/news_data/XNEWS/'
error_list = []

# factor_df_list = Parallel(n_jobs=5)(delayed(parallel_main)(date) for date in date_list)
# print(date_list)
# date = '20240828'
# df = nd.getNewsInfoByEntryTime(date, "00:00", "23:59", "XNEWS")
# df_content = nd.getNewsBody(list(df['newscode'].apply(lambda x : str(x))),"XNEWS")
# print(df_content)