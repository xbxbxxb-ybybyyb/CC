import pandas as pd
import numpy as np
import datetime
from xquant.textdata import NewsData
import os
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import re
import time



out_path = '/dfs/group/800463/data/news_data/news_data_combo/'


def get_interval_num(date, interval):
    df = pd.read_pickle(f'{out_path}{date}.pkl',compression='gzip')
    df = df.drop_duplicates(subset=['id'], keep='first')
    df = df.drop_duplicates(subset=['title'], keep='first')
    df_interval = df[(df['entrytime'] < pd.Timestamp(f'{date} {interval[1]}')) & (df['entrytime'] >= pd.Timestamp(f'{date} {interval[0]}'))]
    return pd.DataFrame({'dt':[date], 'len_all':[len(df)], 'len_interval':[len(df_interval)]})

res = []
interval = ['20:00:00','21:00:00']
start_date = '20250801'
end_date = '20250831'
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
date_list = [x.strftime('%Y%m%d') for x in date_list]

for date in date_list:
    print(date)
    res.append(get_interval_num(date, interval))
res = pd.concat(res)
res['ratio'] = res['len_interval'] / res['len_all']