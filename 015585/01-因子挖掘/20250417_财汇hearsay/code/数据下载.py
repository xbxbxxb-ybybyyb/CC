import pandas as pd
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()
from xquant.textdata import NewsData
nd = NewsData()
import datetime
import os


def get_content(url):
    url = url.replace('https://kf077vr01.s3.cn-north-1.amazonaws.com.cn','http://168.7.16.200:28118/kf077vr01')
    text = nd.get_zxai_news_content(url=url)
    return text
def get_basicinfo_content(date, columns, save_path):
    print(date)
    df = s.get_factor_value("ODS_NEWS_HEARSAY_D", factors = columns, pubdate=[f'>={date}000000', f'<={date}235959'])
    df['content'] = df['contenturl'].apply(get_content)
    df.to_pickle(f'{save_path}{date}.pkl')
    return
columns = ['id', 'pubdate', 'texttitle', 'contenturl', 'medianame', 'authors', 'channel', 'originalurl', 'infosource']
save_path = '/dfs/user/015585/20250423_财汇hearsay数据/原始结果/'
tradingday_list = []
from multiprocessing import Pool
pool = Pool(28)
start_date = '20230101'
end_date = '20231231'
task_list = []

start_date_ = pd.Timestamp(start_date)
end_date_ = pd.Timestamp(end_date)
date_list = [start_date_ + datetime.timedelta(days=i) for i in range((end_date_ - start_date_).days + 1)]
date_list = [i.strftime('%Y%m%d') for i in date_list]

for tradingday in date_list:
    task_list.append(pool.apply_async(get_basicinfo_content, args=(tradingday, columns, save_path)))
pool.close()
pool.join()






