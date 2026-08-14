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
def get_content(url):
    nd = NewsData()
    content = nd.get_zxai_news_content(url=url)
    # print(content)
    return pd.Series({url: content})
def get_content_by_url(df):
    content_list = Parallel(n_jobs=30)(delayed(get_content)(url) for url in df['contentUrl'])
    df_content = pd.DataFrame(pd.concat(content_list,axis=0))
    df_content = df_content.rename(columns = {0:'content'})
    df = pd.merge(df, df_content, left_on='contentUrl', right_index=True, how='left')
    return df
date = '2024-10-25'
data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]), end_date="{} 20:59:59".format(str(date).split(' ')[0]))
print(date,len(data))
print(time.strftime('%Y%m%d %H:%M:%S', time.localtime()))
data = get_content_by_url(data)
print(time.strftime('%Y%m%d %H:%M:%S', time.localtime()))