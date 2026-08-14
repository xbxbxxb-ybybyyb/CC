import pandas as pd
import numpy as np
import datetime
from xquant.textdata import NewsData
import os
nd = NewsData()
# data = nd.get_ai_news_data(start_date="2021-06-30 00:00:00",
#                            end_date="2021-06-30 23:59:59")
def columns_filter(df,col=[]):
    if len(col) > 0:
        df = df[col]
    else:
        col = ['id','pubDate','textTitle','abs','tags','contentUrl',
                 'mediaName','categorys','industrySw','riskLevel','importance','sentiment','entryTime','updateTime']
        df = df.reindex(columns=col, fill_value=np.nan)
    return df
def generate_category(df,finchina_category_list=[]): # 保留category里面的tagcategory，只保留在财汇分类里的部分
    if 'categorys' in df.columns:
        def func_get_tagcategory(x):
            res = []
            if type(x) == list:
                for i in x:
                    res.append(i['tagcategory'])
            return res
        df['categorys'] = df['categorys'].apply(lambda x : func_get_tagcategory(x))
    else:
        pass
    return df
def tags_shsz(df):
    def get_shsz_stock(x):
        res = []
        if type(x) == list:
            for i in x:
                if 'tag' in i:
                    if '.SH' in i['tag'] or '.SZ' in i['tag']:
                        res.append(i['tag'])
        if not res:
            res.append('nostock')
        return res
    df['tags'] = df['tags'].apply(lambda x: get_shsz_stock(x))
    return df
def split_stock_tags(df, col_name='tags'): # 根据tags里在沪深的股票，记录一行变为多行，每行代表一只股票
    df_tmp = df[['id',col_name]]
    df_tmp_columns_list = df_tmp.columns.tolist()
    df_tmp_columns_list.remove(col_name)
    df_tmp = (df_tmp.set_index(df_tmp_columns_list)[col_name].apply(pd.Series).stack().reset_index().drop('level_' + str(len(df_tmp_columns_list)), axis=1)
          .rename(columns={0: 'new_' + col_name}))
    df = pd.merge(df,df_tmp,how = 'outer',left_on='id',right_on='id')
    return df
def change_col_type(df):
    df['pubDate'] = df['pubDate'].apply(lambda x : pd.Timestamp(x))
    df['entryTime'] = df['entryTime'].apply(lambda x : pd.Timestamp(x))
    df['updateTime'] = df['updateTime'].apply(lambda x : pd.Timestamp(x))
    return df
def get_content_by_url(df):
    def get_content(url):
        data = nd.get_zxai_news_content(url=url)
        return data
    df['content'] = df['contentUrl'].apply(lambda x :get_content(x))
    return df
def main_download_news_data(start_date,end_date,out_path,need_content = True):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    for date in date_list:
        if os.path.exists('{}{}.pkl'.format(out_path,str(date).split(' ')[0].replace('-',''))):
            continue
        data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]), end_date="{} 23:59:59".format(str(date).split(' ')[0]))
        print(date,len(data))
        data = columns_filter(data)
        if need_content:
            data = get_content_by_url(data)
        data = change_col_type(data)
        data = generate_category(data)
        data = tags_shsz(data)
        data = split_stock_tags(data)
        data.to_pickle('{}{}.pkl'.format(out_path,str(date).split(' ')[0].replace('-','')))
    return
def parallel_download_news_data(date,out_path,need_content = True):
    try:
        # if not os.path.exists('{}{}.pkl'.format(out_path, str(date).split(' ')[0].replace('-', ''))):
        if True:
            data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]),
                                       end_date="{} 23:59:59".format(str(date).split(' ')[0]))
            print(date, len(data))
            data = columns_filter(data)
            if need_content:
                data = get_content_by_url(data)
            data = change_col_type(data)
            data = generate_category(data)
            data = tags_shsz(data)
            data = split_stock_tags(data)
            data.to_pickle('{}{}.pkl'.format(out_path, str(date).split(' ')[0].replace('-','')))
    except:
        print(date,'数据错误')
    return
start_date = '20240601'
end_date = '20240731'
print(start_date,end_date)
out_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
need_content = True

from joblib import Parallel, delayed
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
factor_df_list = Parallel(n_jobs=2)(delayed(parallel_download_news_data)(date,out_path) for date in date_list)
# main_download_news_data(start_date,end_date,out_path,need_content = False)