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
用于信息技术部新闻数据的日度更新
1、每天20：45运行，更新当日0点到20：45点的数据
2、次日每天3：00运行，更新前一日20:45到23点59的数据
以上包括格式转换、正文正则化，不包括内容去重；默认只更新ITAINEWS，2025年5月加入DATAYES
'''
cut_time = '20:00:00'
cut_time2 = '23:59:59'
print(f'时间：{cut_time}~{cut_time2}')
# ==================================================信息技术部财汇新闻===========================================================================================
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
        if type(url) == str:
            content = nd.get_zxai_news_content(url=url)
        else:
            content = '未获取到正文文件'
        return pd.Series({url: get_clean_text(content)})
    except:
        print(f"failed for {url}")
        return pd.Series({url: '未获取到正文文件'})
def get_content_by_url(df):
    content_list = Parallel(n_jobs=24)(delayed(get_content)(url) for url in df['contentUrl'])
    df_content = pd.DataFrame(pd.concat(content_list,axis=0))
    df_content = df_content.rename(columns = {0:'content'})
    df = pd.merge(df, df_content, left_on='contentUrl', right_index=True, how='left')
    return df
def transfer_AINEWS(df):
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
    # 新增文字内容的规范化
    for col in ['content', 'title', 'abstract']:
        df[col] = df[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
    return df
# ==================================================以下新增通联的部分===========================================================================================
def get_datayes_basicinfo(date):
    if '-' not in date:
        date_ = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    else:
        date_ = date
    df = pd.DataFrame()
    for i in [1,2,3]: # 3种新闻类型
        df_i = nd.get_datayes_news(f'{date_} {cut_time}', f'{date_} {cut_time2}', i, date_field='pubdate')
        df_i['newstype'] = i
        df = pd.concat([df,df_i])
    return df

def get_datayes_stock(date):
    if '-' not in date:
        date_ = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    else:
        date_ = date
    df_stock = nd.get_datayes_company_score_news(start_date=f'{date_} {cut_time}', end_date=f'{date_} {cut_time2}', )
    df_stock = df_stock[df_stock['exchangecode'].isin(['XBEI','XSHE','XSHG'])]
    df_stock.loc[df_stock['exchangecode'] == 'XBEI', 'tradingcode'] = df_stock.loc[df_stock['exchangecode'] == 'XBEI', 'tradingcode'] + '.BJ'
    df_stock.loc[df_stock['exchangecode'] == 'XSHE', 'tradingcode'] = df_stock.loc[df_stock['exchangecode'] == 'XSHE', 'tradingcode'] + '.SZ'
    df_stock.loc[df_stock['exchangecode'] == 'XSHG', 'tradingcode'] = df_stock.loc[df_stock['exchangecode'] == 'XSHG', 'tradingcode'] + '.SH'
    df_stock = df_stock[df_stock['tradingcode'].apply(lambda x : str(x)[0].isdigit())]
    df_ticker_list = df_stock.groupby('newsid').apply(lambda x : list(x['tradingcode'])).reset_index()
    df_ticker_list.columns = ['newsid','Tickerlist']
    df_stock = pd.merge(df_stock, df_ticker_list , left_on='newsid', right_on='newsid', how='left')
    return df_stock

def get_content_datayes(url):
    nd = NewsData()
    try:
        if type(url) == str:
            content = nd.get_zxai_news_content(url=url)
        else:
            content = '未获取到正文文件'
        return pd.Series({url: get_clean_text(content)})
    except:
        print(f"failed for {url}")
        return pd.Series({url: '未获取到正文文件'})
def get_content_by_url_datayes(df):
    df['contenturl'] = df['contenturl'].apply(lambda x : x.replace('https://kf077vr01.s3.cn-north-1.amazonaws.com.cn', 'http://168.7.16.200:28118/kf077vr01') if type(x) == str else x)
    content_list = Parallel(n_jobs=30)(delayed(get_content_datayes)(url) for url in df['contenturl'])
    df_content = pd.DataFrame(pd.concat(content_list,axis=0))
    df_content = df_content.rename(columns = {0:'content'})
    df_content = df_content[df_content['content'] != '未获取到正文文件']
    df = pd.merge(df, df_content, left_on='contenturl', right_index=True, how='left')
    df['content'] = df['content']
    return df

def transfer_datayes(df): # 调整df格式
    used_col = ['newsid', 'texttitle', 'content', 'pubdate', 'effectivetime', 'entrytime', 'updatetime', 'publishsource',
                'tradingcode', 'Tickerlist']
    df = df[used_col]
    df = df.rename(columns = {'newsid':'id',
                              'texttitle':'title',
                              'pubdate':'pubtime',
                              'publishsource':'medianame',
                              'tradingcode':'Ticker'})
    df['resource'] = 'DATAYES'
    df['Tickerlist'] = df['Tickerlist'].apply(lambda x: [] if type(x) != list else x)
    df['dt'] = df['pubtime'].apply(lambda x: pd.Timestamp(str(x).split(' ')[0]))
    df['is_value_by_time'] = 1
    final_col = ['id', 'title', 'abstract', 'content', 'pubtime', 'effectivetime',
                'entrytime', 'updatetime', 'medianame', 'resource', 'dt', 'Ticker',
                'Tickerlist', 'is_value_by_time']
    df = df.reindex(columns = final_col)
    for col in ['content', 'title', 'abstract']:
        df[col] = df[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
    return df
# ===================================================================
def main_download_news_data(start_date,end_date,out_path,need_content = True):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    for date in date_list:
        try:
            data = nd.get_ai_news_data(start_date=f"{str(date).split(' ')[0]} {cut_time}", end_date= f"{str(date).split(' ')[0]} {cut_time2}")
            print(date,'财汇新闻数量：',len(data))
            data = columns_filter(data)
            if need_content:
                data = get_content_by_url(data)
            else:
                data['content'] = ''
            data = change_col_type(data)
            data = generate_category(data)
            data = tags_shsz(data)
            data = split_stock_tags(data)
            data = transfer_AINEWS(data)
            for col in ['content', 'title', 'abstract']:
                data[col] = data[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
            data.reset_index(drop=True, inplace=True)
            # 加入通联
            df_datayes = get_datayes_basicinfo(str(date).split(' ')[0])
            print(date,'通联新闻数量',len(df_datayes))
            df_datayes = get_content_by_url_datayes(df_datayes)
            df_datayes_stock = get_datayes_stock(str(date).split(' ')[0])
            df_datayes = pd.merge(df_datayes, df_datayes_stock[['newsid', 'tradingcode', 'Tickerlist']],
                                  left_on='newsid', right_on='newsid', how='left')
            df_datayes = transfer_datayes(df_datayes)
            # 合并通联
            df = data.append(df_datayes)
            df = df.sort_values('pubtime')
            # 合并cut_time1之前的
            df_ori = pd.read_pickle(out_path + str(date).split(' ')[0].replace('-','') + '.pkl', compression='gzip')
            df = df_ori.append(df)
            df = df.sort_values('pubtime')
            df.to_pickle(out_path + str(date).split(' ')[0].replace('-','') + '.pkl', compression='gzip')
        except Exception as e:
            print('{}：数据下载失败')
            print(e)
    return

start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
#start_date = '20250527'
end_date = start_date

print(start_date,end_date)
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

out_path = '/dfs/group/800463/data/news_data/news_data_combo/'
need_content = True

date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
main_download_news_data(start_date,end_date,out_path,need_content = need_content)
if end_date == start_date:
    try:
        df_check = pd.read_pickle('{}{}.pkl'.format(out_path, str(end_date).split(' ')[0].replace('-','')), compression='gzip')
        message_to_qyh_wys = '{}数据20:00~24:00新闻补充完成，新闻数量：{}，20：00以后新闻数量：{}，正文大于20的新闻数量：{}，新闻起始时间：{}，新闻截止时间：{}，df长度：{}'\
            .format(str(end_date).split( )[0],
                    len(set(df_check['id'])),
                    len(set(df_check[df_check['pubtime'] >= pd.Timestamp(f'{str(end_date).split( )[0]} {cut_time}')]['id'])),
                    len(set(df_check[df_check['content'].apply(len) > 20]['id'])),
                    df_check['pubtime'].min(),
                    df_check['pubtime'].max(),
                    len(df_check))
        if len(df_check) < 100:
            message_to_qyh_wys = '警告！！新闻df长度小于100，' + message_to_qyh_wys
    except Exception as e:
        message_to_qyh_wys = "{}新闻22：00~24：00数据补充失败，{}".format(str(end_date).split( )[0],e)
    print(message_to_qyh_wys)
    send_message(message_to_qyh_wys, users=['015585','003371','021012'])
#    send_message(message_to_qyh_wys, users=['015585'])