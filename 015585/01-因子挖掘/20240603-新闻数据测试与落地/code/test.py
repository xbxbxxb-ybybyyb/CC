import pandas as pd
import numpy as np
import os
# import sys
print(os.getcwd())
# # 检查通联content是否可读取
# path = '/dfs/group/800463/data/news_data/datayes_content/'
# file_list = os.listdir(path)
# file_list.sort()
# error_date = {'error':[],'short':[]}
# for file in file_list:
#     sys.stdout.write('\r' + file)
#     sys.stdout.flush()
#     if '.h5' in file:
#         try:
#             df = pd.read_hdf(path + file)
#             if df[df['newsBody'].apply(lambda x : len(x)) > 20].shape[0] / df.shape[0] < 0.7:
#                 error_date['short'].append(file)
#         except:
#             error_date['error'].append(file)
# # 检查通联basicinfo是否可读取
# path = '/dfs/group/800463/data/news_data/datayes_basicinfo/'
# file_list = os.listdir(path)
# file_list.sort()
# error_date = {'error':[],'short':[]}
# for file in file_list:
#     sys.stdout.write('\r' + file)
#     sys.stdout.flush()
#     if '.h5' in file:
#         try:
#             df = pd.read_hdf(path + file)
#             if len(df) < 100:
#                 error_date['short'].append(file)
#         except:
#             error_date['error'].append(file)
#
#
# 检查通联正文是否覆盖一些新闻
path = '/dfs/group/800463/data/news_data/datayes_content/'
date = '20240614.h5'
df = pd.read_hdf(path + date)
print(df[df['newsBody'].str.contains('智能电网概念逆势走强')]['newsBody'])

path = '/dfs/group/800463/data/news_data/datayes_basicinfo/'
date = '20240624.h5'
df = pd.read_hdf(path + date)
print(df[df['newsTitle'].str.contains('PCB概念板块强势')]['newsTitle'])