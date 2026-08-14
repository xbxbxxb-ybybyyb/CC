# coding: utf-8
# Author：fengchi863
# Date ：2024/5/22 9:10

"""测试用例"""
import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData
from tqdm import tqdm
nd = NewsData()
s = FactorData()

stock_list = ['000001.SZ', '000002.SZ']

info_list = list()
for stock in tqdm(stock_list):
    info = nd.getAnnouncement([stock], '20231231', '20240521')
    info['newsID'] = info['ORIGINALCODE'].astype(str)
    info = info[['PUBDATE', 'TEXTTITLE', 'newsID']]
    info_list.append(info)
news_info = pd.concat(info_list, ignore_index=True)

print('准备第一次调用FactorData')
print('第一次打印：', s.tradingday(20240501, 20240601))

newID_list = news_info['newsID'].map(int).tolist()[:10]
news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]

print('准备第二次调用FactorData')
print('第二次打印：', s.tradingday(20240501, 20240601))

news_bodies_df2 = nd.getAnnouncementContent(newID_list).loc[newID_list]

print('准备第三次调用FactorData')
print('第三次打印：', s.tradingday(20240501, 20240601))   # 本次开始无法调用，卡在这行
print('finish')
