import pandas as pd
import numpy as np
import datetime
from xquant.textdata import NewsData
import os
from joblib import Parallel, delayed
import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import re
import time

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
nd = NewsData()


def get_content(url, max_retries=3):
    """获取单个 URL 的内容，支持重试"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # 如果响应状态不是 200，则抛出异常
            return pd.Series({url:get_clean_text(response.text)})
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt + 1 == max_retries:
                print(f"All attempts failed for {url}.")
                return pd.Series({url:'未获取到正文文件'})
            # 等待一段时间再重试
            time.sleep(2 ** attempt)  # 指数退避

def get_content_parallel(df, col_url = 'contentUrl', max_retries = 3, n_jobs = 12):
    content_list = Parallel(n_jobs=n_jobs)(delayed(get_content)(url, max_retries) for url in df['contentUrl'])
    df_content = pd.DataFrame(pd.concat(content_list,axis=0))
    df_content = df_content.rename(columns = {0:'content'})
    df = pd.merge(df, df_content, left_on='contentUrl', right_index=True, how='left')
    return df
data = nd.get_ai_news_data(start_date="2024-10-20 00:00:00",
                           end_date="2024-10-20 23:59:59")
print(len(data))
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
data = get_content_parallel(data, col_url = 'contentUrl', max_retries = 3, n_jobs = 24)
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))