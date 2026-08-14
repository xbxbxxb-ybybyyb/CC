import os
import pandas as pd
import numpy as np
import IO
import ast

print(os.getcwd())
dic_news_basicinfo_path = {
    '普通新闻':'/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02普通新闻去重表vnews_content_nondupbd/',
    '微信新闻':'/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02微信新闻去重表vnews_nondupbd_wechat.csv',
    '快讯新闻':'/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02快讯新闻去重表vnews_nondupbd_flash.csv'
}
dic_news_content_path = {
    '普通新闻': '/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02普通新闻原文vnews_body_v1_s3/',
    '微信新闻': '/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02微信新闻原文vnews_body_wechat_s3.csv',
    '快讯新闻': '/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02通联剩余9张表/2025-04-02快讯新闻原文vnews_body_flash_s3.csv'
}
dic_related_path = {
    'A股公司':'/data/user/015585/01-因子挖掘/20250403_通联技术侧验证/file/2025-04-02A股公司新闻关联表news_a_share_rel/'
}
# 获取各类新闻的基本信息文件
dic_news_basicinfo = {}
for type_news in dic_news_basicinfo_path:
    if '.csv' in dic_news_basicinfo_path[type_news]:
        dic_news_basicinfo[type_news] = pd.read_csv(dic_news_basicinfo_path[type_news],sep='\t')
    else:
        file_list = os.listdir(dic_news_basicinfo_path[type_news])
        df = pd.concat([pd.read_csv(f'{dic_news_basicinfo_path[type_news]}{file}',sep='\t') for file in file_list])
        dic_news_basicinfo[type_news] = df
# 获取各类新闻的原文地址
dic_news_content = {}
for type_news in dic_news_content_path:
    if '.csv' in dic_news_content_path[type_news]:
        dic_news_content[type_news] = pd.read_csv(dic_news_content_path[type_news],sep='\t')
    else:
        file_list = os.listdir(dic_news_content_path[type_news])
        df = pd.concat([pd.read_csv(f'{dic_news_content_path[type_news]}{file}',sep='\t') for file in file_list])
        dic_news_content[type_news] = df
# 获取新闻和A股公司的关联关系
file_list = os.listdir(dic_related_path['A股公司'])
df_related_a = pd.concat([pd.read_csv(f'{dic_related_path["A股公司"]}{file}',sep='\t') for file in file_list])
df_related_a['TICKER_SYMBOL'] = df_related_a['TICKER_SYMBOL'].apply(lambda x : str(int(x)).zfill(6) if not pd.isna(x) else x)

# 统计：每日新闻数量
list_basicinfo = []
for k in dic_news_basicinfo:
    df = dic_news_basicinfo[k]
    df['resource'] = k
    list_basicinfo.append(df.copy())
    print(k,df.shape)
news_basicinfo = pd.concat(list_basicinfo)
news_basicinfo['dt'] = news_basicinfo['NEWS_PUBLISH_TIME'].apply(lambda x : x.split(' ')[0])
print('每日每种新闻的全部数量:')
print(news_basicinfo.groupby(['dt','resource'])['NEWS_ID'].count())
print('每日新闻的全部数量:')
print(news_basicinfo.groupby(['dt'])['NEWS_ID'].count())
# 统计：每日有content的新闻数量
list_content = []
for k in dic_news_content:
    df = dic_news_content[k]
    list_content.append(df.copy())
    print(k,df.shape)
news_content = pd.concat(list_content)
news_basicinfo_content = pd.merge(news_basicinfo,news_content,left_on='NEWS_ID',right_on='NEWS_ID',how='left')
print('有content_url的比例：',news_basicinfo_content[news_basicinfo_content['NEWS_URL'].apply(len) > 20].shape[0] / news_basicinfo_content.shape[0])
# 统计：A股新闻数量、A股新闻覆盖度
news_basicinfo_content_stock = pd.merge(news_basicinfo_content,df_related_a,left_on='NEWS_ID',right_on='NEWS_ID',how='left')
print('新闻数量：',news_basicinfo_content.shape[0])
print('有A股的新闻数量：',len(set(news_basicinfo_content_stock[~news_basicinfo_content_stock['TICKER_SYMBOL'].isna()]['NEWS_ID'])))
print('A股新闻日均数量：',
      news_basicinfo_content_stock[~news_basicinfo_content_stock['TICKER_SYMBOL'].isna()]
      .drop_duplicates(subset=['NEWS_ID']).groupby('dt')['NEWS_ID'].apply(lambda x :len(set(x))))
print('日均A股覆盖度：', news_basicinfo_content_stock[~news_basicinfo_content_stock['TICKER_SYMBOL'].isna()]
      .groupby('dt')['TICKER_SYMBOL'].apply(lambda x :len(set(x))))
# 统计：时效性
print('UPDATE_TIME - NEWS_PUBLISH_TIME')
print((news_basicinfo[~news_basicinfo['NEWS_PUBLISH_TIME'].str.contains('00:00:00')]['UPDATE_TIME'].apply(pd.Timestamp)
       - news_basicinfo[~news_basicinfo['NEWS_PUBLISH_TIME'].str.contains('00:00:00')]['NEWS_PUBLISH_TIME'].apply(pd.Timestamp)).quantile([0.25,0.5,0.75,0.9]))
print('EFFECTIVE_TIME - NEWS_PUBLISH_TIME')
print((news_basicinfo[(~news_basicinfo['NEWS_PUBLISH_TIME'].str.contains('00:00:00')) & (~news_basicinfo['EFFECTIVE_TIME'].str.contains('00:00:00'))]['EFFECTIVE_TIME'].apply(pd.Timestamp)
       - news_basicinfo[(~news_basicinfo['NEWS_PUBLISH_TIME'].str.contains('00:00:00')) & (~news_basicinfo['EFFECTIVE_TIME'].str.contains('00:00:00'))]['NEWS_PUBLISH_TIME'].apply(pd.Timestamp)).quantile([0.25,0.5,0.75,0.9]))


