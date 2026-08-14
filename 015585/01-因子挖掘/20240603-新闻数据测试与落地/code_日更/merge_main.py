import pandas as pd
import numpy as np
import datetime
import os
from joblib import Parallel, delayed
'''
1、合并通联历史（2016-2020）、AI新闻最新（2016-202406）、XNEWS新闻历史（2016-202406）
2、数据结构见excel
'''
def split_stock_tags(df, col_id = 'id',col_name='Tickerlist'): # 根据tags里在沪深的股票，记录一行变为多行，每行代表一只股票
    df_tmp = df[[col_id,col_name]]
    df_tmp_columns_list = df_tmp.columns.tolist()
    df_tmp_columns_list.remove(col_name)
    df_tmp = (df_tmp.set_index(df_tmp_columns_list)[col_name].apply(pd.Series).stack().reset_index().drop('level_' + str(len(df_tmp_columns_list)), axis=1)
          .rename(columns={0: 'Ticker'}))
    df = pd.merge(df,df_tmp,how = 'outer',left_on=col_id,right_on=col_id)
    return df
def transfer_DATAYES(date):
    path = '/dfs/group/800463/data/news_data/datayes_basicinfo/'
    if os.path.exists(path + date + '.h5') and date <= '20201231':
        df = pd.read_hdf(path + date + '.h5')
        # 列名和格式调整
        df = df.rename(columns={'newsID':'id',
                        'newsTitle':'title',
                        'newsBody':'content',
                        'newsPublishTime':'pubtime',
                        'effectiveTime':'effectivetime',
                        'ticker':'Tickerlist',
                        })
        df['effectivetime'] = df['effectivetime'].apply(lambda x : pd.Timestamp(x))
        df['entrytime'] = df['effectivetime']
        df['updatetime'] = df['effectivetime']
        df['medianame'] = df['newsPublishSite'].apply(lambda x : x + '_') + df['newsOriginSource']
        df['resource'] = 'DATAYES'
        # 展开Ticker
        def get_Tickerlist(x):
            res = []
            if type(x) == str:
                for i in eval(x):
                    if len(i) == 5:
                        res.append(i+'.HK')
                    if len(i) == 6:
                        res.append(i+'.SH') if i.startswith('6') else res.append(i+'.SZ')
            return res
        df['Tickerlist'] = df['Tickerlist'].apply(lambda x : get_Tickerlist(x))
        df['dt'] = df['pubtime'].apply(lambda x : pd.Timestamp(str(x).split(' ')[0]))
        df = split_stock_tags(df,'id','Tickerlist')
        # 获取content
        content_path = '/dfs/group/800463/data/news_data/datayes_content/'
        df_content = pd.read_hdf(content_path + date + '.h5')
        df_content['newsID'] = df_content['newsID'].apply(lambda x : int(x))
        df = pd.merge(df,df_content,left_on='id',right_on='newsID',how='left')
        df = df.rename(columns={'newsBody':'content'})
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
                    ]
        df = df.reindex(columns= col_list)
        return df
    else:
        if date <= '20201231':
            print('datayes该日无文件：{}'.format(date))
        else:
            print('非2016-2020，datayes无文件：{}'.format(date))
        return pd.DataFrame()
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
        # 计算effectivetime
        df['effectivetime'] = df['pubtime']
        df['timedelta'] = df['entrytime'] - df['pubtime']
        df.loc[df['timedelta'] <= pd.Timedelta(days=1),'effectivetime'] = df.loc[df['timedelta'] <= pd.Timedelta(days=1),'entrytime']
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
                    ]
        df = df.reindex(columns= col_list)
        return df
    else:
        print('IT_AInews该日无文件：{}'.format(date))
        return pd.DataFrame()
def transfer_XNEWS(date):
    path = '/dfs/group/800463/data/news_data/XNEWS/'
    if os.path.exists(path + date + '.pkl'):
        df = pd.read_pickle(path + date + '.pkl')
        # 列名和格式调整
        df = df.rename(columns = {'content':'contenturl'})
        df = df.rename(columns={
                        'newscode':'id',
                        'newstitle':'title',
                        'newstime':'pubtime',
                        'symbol':'Ticker',
                        'newssource':'medianame',
                        'newsBody':'content'
                        })
        df['resource'] = 'XNEWS'
        # Tickerlist
        def get_Tickerlist_XNEWS(df):
            df_Tickerlist = pd.DataFrame(df.groupby('id')['Ticker'].apply(lambda x : list(x)))
            df_Tickerlist.columns = ['Tickerlist']
            df_Tickerlist['Tickerlist'] = df_Tickerlist['Tickerlist'].apply(lambda x : [i for i in x if type(i) == str])
            df = pd.merge(df,df_Tickerlist,left_on='id',right_on='id')
            return df
        df = get_Tickerlist_XNEWS(df)
        # entry update effectivetime dt
        df['entrytime'] = (df['entrydate'].apply(lambda x : x.strftime('%Y%m%d')) + ' ' + df['entrytime']).apply(lambda x : pd.Timestamp(x))
        df['updatetime'] = df['entrytime']
        df['effectivetime'] = df['pubtime']
        df['timedelta'] = df['entrytime'] - df['pubtime']
        df.loc[df['timedelta'] <= pd.Timedelta(days=1),'effectivetime'] = df.loc[df['timedelta'] <= pd.Timedelta(days=1),'entrytime']
        df['dt'] = df['pubtime'].apply(lambda x: pd.Timestamp(str(x).split(' ')[0]))
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
                    ]
        df = df.reindex(columns= col_list)
        return df
    else:
        print('XNEWS该日无文件：{}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'.format(date))
        return pd.DataFrame()

def combo_main(date):
    print(date)
    df_datayes = transfer_DATAYES(date)
    df_ainews = transfer_AINEWS(date)
    df_xnews = transfer_XNEWS(date)
    df = pd.concat([df_datayes,df_ainews,df_xnews],axis=0)
    for col in ['content', 'title', 'abstract']:
        df[col] = df[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
    df.reset_index(drop=True,inplace=True)
    df.to_pickle('/dfs/group/800463/data/news_data/news_data_combo/' + date +'.pkl',compression='gzip')
    return
start_date = '20190101'
end_date = '20240630'
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
date_list = [x.strftime('%Y%m%d') for x in date_list]
#
factor_df_list = Parallel(n_jobs=24)(delayed(combo_main)(date) for date in date_list)