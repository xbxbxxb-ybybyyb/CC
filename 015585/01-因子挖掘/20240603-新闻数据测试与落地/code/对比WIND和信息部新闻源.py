import os
import pandas as pd
import datetime
# 信息部源
out_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
res = pd.DataFrame()
file_list = os.listdir(out_path)
file_list.sort()
for file in file_list:
    if file.replace('.pkl','') >= '20240301':
        print(file)
        res = pd.concat([res,pd.read_pickle(out_path + file)],axis=0)
res_IT = res.reset_index()
res_IT[res_IT['textTitle'].str.contains('协和电子3连板涨停，封板资金4516.92万元')]
# 同花顺
def time_transfer(x):
    return datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S")
out_path = '/dfs/group/800463/data/news_data/ths_basicinfo/'
res = pd.DataFrame()
file_list = os.listdir(out_path)
file_list.sort()
for file in file_list:
    if file.replace('.h5','') >= '2024-06-01':
        print(file)
        res = pd.concat([res,pd.read_hdf(out_path + file)[['itemId', 'title', 'source', 'time','stocks', 'entityLabel']]],axis=0)
res_ths = res.reset_index()
for col in ['time']:
    res_ths[col] = res_ths[col].apply(lambda x: time_transfer(x))
res_ths[res_ths['title'].str.contains('午间涨跌停股分析')]
# 通联
out_path = '/dfs/group/800463/data/news_data/datayes_basicinfo/'
res = pd.DataFrame()
file_list = os.listdir(out_path)
file_list.sort()
for file in file_list:
    if file.replace('.h5','') >= '20240501':
        print(file)
        res = pd.concat([res,pd.read_hdf(out_path + file)],axis=0)
res_tl = res.reset_index()
res_tl[res_tl['newsTitle'].str.contains('协和电子3连板涨停，封板资金4516.92万元')]
#
media_list = ['证券时报网',
'金融界',
'证券时报',
'中金在线',
'财联社',
'证券之星',
'华尔街见闻',
'新浪网',
'钛媒体',
'格隆汇',
'智通财经',
'界面',
'第一财经',
'新浪',
'券中社',
'每日经济新闻',
'大河财立方',
'36氪',
'乐居财经',
'砍柴网',
'金十数据',
]
stock_list = ['000004',
'000158',
'000410',
'000679',
'000712',
'002261',
'300380',
'300605',
'600187',
'600611',
'603324',
]

# for media in media_list:
#     count = 0
#     for i in set(stock_list):
#         if len(res[(res['new_tags'].str.contains(i)) & (res['mediaName'] == media)]) > 0:
#             count = count + 1
#             print(i)
#     print(media,count)

#
from xquant.textdata import NewsData
import os
# nd = NewsData()
# data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str('2024-07-22').split(' ')[0]), end_date="{} 23:59:59".format(str('2024-07-22').split(' ')[0]))
# tmp = data[data['textTitle'].str.contains('000679')]
#
# tmp = res[res['textTitle'].str.contains('午间涨跌停')]
# tmp = tmp[~tmp['id'].duplicated()]
