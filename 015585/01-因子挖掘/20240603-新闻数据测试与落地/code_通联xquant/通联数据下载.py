from xquant.textdata import NewsData
import pandas as pd
from bs4 import BeautifulSoup
import re
import numpy as np
from joblib import Parallel, delayed
import datetime
nd = NewsData()
'''
该脚本需要已有相关数据文件，会执行如下步骤：
1、删除原先新闻文件中DATAYES的部分
2、下载EFFECTIVE_TIME在该日的DATAYES新闻，APPEND到剩余部分中
3、重新按时间排序，保存为gzip文件
'''

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
def get_ori_df_without_datayes(date, ori_path):
    df_ori = pd.read_pickle(f'{ori_path}{date}.pkl', compression='gzip')
    df_ori = df_ori[df_ori['resource'] != 'DATAYES']
    return df_ori

def get_datayes_basicinfo(date):
    date_ = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    df = pd.DataFrame()
    for i in [1,2,3]: # 3种新闻类型
        df_i = nd.get_datayes_news(f'{date_} 00:00:00', f'{date_} 23:59:59', i, date_field='pubdate')
        df_i['newstype'] = i
        df = pd.concat([df,df_i])
    return df

def get_datayes_stock(date):
    date_ = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    df_stock = nd.get_datayes_company_score_news(start_date=f'{date_} 00:00:00', end_date=f'{date_} 23:59:59', )
    df_stock = df_stock[df_stock['exchangecode'].isin(['XBEI','XSHE','XSHG'])] # !!!! 注意这里要补充上交所，目前有问题，下面也要添加一行
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
        # url = url.replace('https://kf077vr01.s3.cn-north-1.amazonaws.com.cn', 'http://168.7.16.200:28118/kf077vr01')
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

def main_supple_datayes(date, ori_path, save_path): # 必须已有文件
    print(date)
    df_ori = get_ori_df_without_datayes(date, ori_path) # 待替换的文件
    print('原始文件大小：',df_ori.shape)
    # datayes
    df_datayes = get_datayes_basicinfo(date)
    ## get content
    df_datayes = get_content_by_url_datayes(df_datayes)
    ## 关联股票
    df_datayes_stock = get_datayes_stock(date)
    df_datayes = pd.merge(df_datayes, df_datayes_stock[['newsid', 'tradingcode', 'Tickerlist']], left_on='newsid', right_on='newsid', how='left')
    ## 格式转换
    df_datayes = transfer_datayes(df_datayes)
    # 添加到待替换文件中
    df = df_ori.append(df_datayes)
    df = df.sort_values('pubtime')
    print('最终文件大小：',df.shape)
    # 存储
    df.to_pickle(f'{save_path}{date}.pkl', compression='gzip')
    return

start_date = '20250507'
end_date = '20250526'
ori_path = '/dfs/group/800463/data/news_data/news_data_combo/'
save_path = '/dfs/group/800463/data/news_data/news_data_combo_add_datayes/'

date_list = [pd.Timestamp(start_date) + datetime.timedelta(days=i) for i in range((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1)]
date_list = [x.strftime('%Y%m%d') for x in date_list]
for date in date_list:
    main_supple_datayes(date, ori_path, save_path=save_path)

