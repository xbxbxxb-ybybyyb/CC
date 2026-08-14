import pandas as pd
import numpy as np
import os
import IO
from xquant.factordata import FactorData
import sys
import time

s = FactorData()
from xquant.xqutils.helper import link
lm = link.LinkMessage()

def get_feidi_data(tradingday, save_path):
    print(tradingday)
    df = s.get_factor_value("GOGOAL2_STOCK_CHANGE_ATTRIBUTION", PUBDATE=[f'>={tradingday} 000000', f'<={tradingday} 205959'])
    # 数据预处理
    for col in ['PUBDATE', 'ENTRYTIME', 'UPDATETIME', 'GROUNDTIME']:
        df[col] = df[col].apply(lambda x : pd.Timestamp(x))
    df = df.rename(columns = {'PUBDATE':'PUBTIME'})
    df['PUBDATE'] = df['PUBTIME'].apply(lambda x : x.normalize() if not pd.isna(x) else np.nan)
    df['year'] = df['PUBDATE'].apply(lambda x: x.year)
    df.to_pickle(f'{save_path}{tradingday}.pkl')
    message = f'{tradingday}飞笛个股异动更新完成：df长度为{len(df)}'
    lm.sendMessage(message)
    return

local_time = time.strftime('%Y%m%d', time.localtime())
start_date = local_time # '20220701'
end_date = local_time
# date_list = s.tradingday(int(start_date), int(end_date))
date_list = s.tradingday(int(start_date), 1)
save_path = '/dfs/group/800463/data/news_data/fid_abnormal/'

# tradingday = '20250519'
for tradingday in date_list:
    get_feidi_data(tradingday, save_path)