import os

import pandas as pd
import numpy as np
import datetime
from xquant.textdata import NewsData
nd = NewsData()
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

# wind-申万行业代码匹配表
'''
用新闻表中industrySw = df.INDUSTRIESALIAS获取df.INDUSTRIESCODE
再用df.INDUSTRIESCODE = df2.S_INFO_INDUSTRYCODE获取df2.S_INFO_INDEXCODE即为指数代码
'''
df = s.get_factor_value('WIND_AShareIndustriesCode')
df = df[df['INDUSTRIESCODE'].str.startswith('76')]
df['INDUSTRIESALIAS'] = df['INDUSTRIESALIAS'].apply(lambda x : str(x).ljust(6,'0'))
df2 = s.get_factor_value('WIND_IndexContrastSector')
# sentiment
'''
（0-中性，1-正面，2-负面）
'''
# risklevel
'''
（0-低风险，1-中风险，2-高风险）
'''
# importance
'''
（1:重要 2:中等 3:一般 4:非金融）

'''
# categorys
'''
本质上是一个合集，包括涨乐栏目名称（名称编码），财汇新闻分类编码
信息技术部仍然在整理编码对应的中文释义和来源，可以先不使用
'''
# 财汇-分类表
df_finchina_category = pd.read_excel('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/tagcategory整理.xlsx')
df_finchina_category['TAGCATEGORY'] = df_finchina_category['TAGCATEGORY'].apply(lambda x : str(x))
df_finchina_category = df_finchina_category[~df_finchina_category['TAGCATEGORY'].duplicated()]
df_finchina_category = df_finchina_category.set_index('TAGCATEGORY')
dic_finchina_category = df_finchina_category.to_dict('index')
def get_finchina_category(x,dic_finchina_category):
    res = []
    for i in x:
        if i in dic_finchina_category.keys():
            res.append(dic_finchina_category[i]['中文释义'])
        else:
            print(i,'没有找到释义')
    return res
df['tmp'] = df['categorys'].apply(lambda x : get_finchina_category(x,dic_finchina_category))

'''
'''
date = pd.Timestamp('20240520')
data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]), end_date="{} 23:59:59".format(str(date).split(' ')[0]))
print(set(data['infoSource']))


# path = '/dfs/group/800463/data/news_data/AI_newsdata/'
# for file in os.listdir(path):
#     df = pd.read_pickle(path + file)
#     df['tmp'] = df['content'].apply(lambda x : len(x))
#     print(file,len(df[df['tmp']>5]) / (len(df)+1))