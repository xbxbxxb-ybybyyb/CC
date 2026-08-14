import pandas as pd
import numpy as np
import datetime
from xquant.textdata import NewsData
import os
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import re
import time
from tools import send_message

nd = NewsData()
'''
'''
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
def get_clean_text(text):
    if text is None:
        clean_text = ''
    elif type(text) != str:
        clean_text = ''
    else:
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        clean_text = clean_text.replace('\n',' ')
        clean_text = clean_text.replace('\r',' ')
        clean_text = clean_text.replace('\t',' ')
        clean_text = clean_text.replace('\xa0',' ')
        clean_text = clean_text.replace('\u00A0',' ')
        clean_text = clean_text.replace('\u3000', '')
        clean_text = clean_text.replace('\\', '')
        clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text
def get_content(url):
    nd = NewsData()
    try:
        content = nd.get_zxai_news_content(url=url)
        # print(content)
        return pd.Series({url: get_clean_text(content)})
    except:
        print(f"failed for {url}")
        return pd.Series({url: '未获取到正文文件'})
def get_content_by_url(df):
    content_list = Parallel(n_jobs=30)(delayed(get_content)(url) for url in df['contentUrl'])
    df_content = pd.DataFrame(pd.concat(content_list,axis=0))
    df_content = df_content.rename(columns = {0:'content'})
    df = pd.merge(df, df_content, left_on='contentUrl', right_index=True, how='left')
    return df
def transfer_AINEWS(date):
    path = '/dfs/group/800463/data/news_data/AI_newsdata/'
    if os.path.exists(path + date + '.pkl'):
        df = pd.read_pickle(path + date + '.pkl')
        # 列名和格式调整
        df = df.rename(columns={
                        'id':'id',
                        'textTitle':'title',
                        'content':'content',
                        'pubDate':'pubtime',
                        'new_tags':'Ticker',
                        'abs':'abstract',
                        'mediaName':'medianame',
                        'entryTime':'entrytime',
                        'updateTime':'updatetime',
                        'tags':'Tickerlist'
                        })
        df['resource'] = 'ITAINEWS'
        df['Ticker'] = df['Ticker'].apply(lambda x : np.nan if x == 'nostock' else x)
        df['Tickerlist'] = df['Tickerlist'].apply(lambda x : [] if x == ['nostock'] else x)
        df['dt'] = df['pubtime'].apply(lambda x: pd.Timestamp(str(x).split(' ')[0]))
        df['is_value_by_time'] = 1
        # 计算effectivetime
        df['effectivetime'] = df['pubtime']
        df['timedelta'] = df['entrytime'] - df['pubtime']
        df.loc[(df['timedelta'] <= pd.Timedelta(days=1)) & (df['timedelta'] >= pd.Timedelta(days=0)),'effectivetime'] = \
            df.loc[(df['timedelta'] <= pd.Timedelta(days=1)) & (df['timedelta'] >= pd.Timedelta(days=0)),'entrytime']
        # 规范化
        col_list = ['id',
                    'title',
                    'abstract',
                    'content',
                    'pubtime',
                    'effectivetime',
                    'entrytime',
                    'updatetime',
                    'medianame',
                    'resource',
                    'dt',
                    'Ticker',
                    'Tickerlist',
                    'is_value_by_time'
                    ]
        df = df.reindex(columns= col_list)
        return df
    else:
        print('IT_AInews该日无文件：{}'.format(date))
        return pd.DataFrame()
def main_download_news_data(start_date,end_date,out_path1,out_path2,need_content = True):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    for date in date_list:
        # if os.path.exists('{}{}.pkl'.format(out_path,str(date).split(' ')[0].replace('-',''))):
        #     continue
        try:
            data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]), end_date="{} 23:59:59".format(str(date).split(' ')[0]))
            print(date,len(data))
            data = columns_filter(data)
            if need_content:
                data = get_content_by_url(data)
            else:
                data['content'] = ''
            data = change_col_type(data)
            data = generate_category(data)
            data = tags_shsz(data)
            data = split_stock_tags(data)
            data.to_pickle('{}{}.pkl'.format(out_path1,str(date).split(' ')[0].replace('-',''))) # 存到单独的AI_newsdata文件夹
            #
            df = transfer_AINEWS(str(date).split(' ')[0].replace('-',''))
            for col in ['content', 'title', 'abstract']:
                df[col] = df[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
            df.reset_index(drop=True, inplace=True)
            df.to_pickle(out_path2 + str(date).split(' ')[0].replace('-','') + '.pkl', compression='gzip')
        except Exception as e:
            print('{}：数据下载失败')
            print(e)
    return

start_date = pd.Timestamp('20241227')
end_date = pd.Timestamp('20241227')
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
for start_date in date_list:
    start_date = start_date.strftime('%Y%m%d')
    print(start_date)
    end_date = start_date

    print(start_date,end_date,time.localtime())
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    out_path1 = '/dfs/group/800463/data/news_data/AI_newsdata/'
    out_path2 = '/dfs/group/800463/data/news_data/news_data_combo/'
    need_content = True

    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    main_download_news_data(start_date,end_date,out_path1,out_path2,need_content = need_content)
    if end_date == start_date:
        try:
            df_check = pd.read_pickle('{}{}.pkl'.format(out_path2, str(end_date).split(' ')[0].replace('-','')), compression='gzip')
            message_to_qyh_wys = '{}数据下载完成，新闻数量：{}，正文大于20的新闻数量：{}，新闻起始时间：{}，新闻截止时间：{}，df长度：{}'\
                .format(str(end_date).split( )[0],
                        len(set(df_check['id'])),
                        len(set(df_check[df_check['content'].apply(len) > 20]['id'])),
                        df_check['pubtime'].min(),
                        df_check['pubtime'].max(),
                        len(df_check))
            if len(df_check) < 100:
                message_to_qyh_wys = '警告！！新闻df长度小于100，' + message_to_qyh_wys
        except Exception as e:
            message_to_qyh_wys = "{}新闻数据下载失败，{}".format(str(end_date).split( )[0],e)
        print(message_to_qyh_wys)
        send_message(message_to_qyh_wys, users=['015585','022325'])