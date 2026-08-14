import pandas as pd
import numpy as np
import os

def get_all_basicinfo(start_date, end_date, basicinfo_path):
    res = pd.DataFrame()
    file_list = os.listdir(basicinfo_path)
    file_list = [f'{basicinfo_path}{i}' for i in file_list if i.replace('.pkl','') >= start_date and i.replace('.pkl','') <= end_date]
    file_list.sort()
    files = map(pd.read_pickle, file_list)
    res = pd.concat(files, sort = True)
    return res

def get_url(x):
    if len(x) > 1:
        print(f'存在不止1个url，annex={x}')
        url = ''
    elif len(x) == 0:
        # print(f'没有pdf的url，annex={x}')
        url = ''
    else:
        url = x[0]['url']
    return url
basicinfo_path = '/dfs/group/800463/data/research_report_data/rr_basicinfo/'
start_date = '20160101'
end_date = '20241231'

df_ori = get_all_basicinfo(start_date, end_date, basicinfo_path)
print(f'已获取{start_date}到{end_date}的研报基本信息')
# 预处理
df_ori['content_url'] = df_ori['annex'].apply(lambda x : get_url(x))
df_ori['pubDate'] = df_ori['pubDate'].apply(pd.Timestamp)
df_ori['year'] = df_ori['pubDate'].apply(lambda x : x.year)
df_ori['month'] = df_ori['pubDate'].apply(lambda x : str(x.month).zfill(2))
df_ori['date'] = df_ori['pubDate'].apply(lambda x : x.date())
df_ori['industrySw_name'] = df_ori['industrySw'].apply(lambda x : x[0]['induname'] if len(x) > 0 else '')
df_ori['industrySw_level'] = df_ori['industrySw'].apply(lambda x : x[0]['indulevel'] if len(x) > 0 else '')

df_ori['entryTime'] = df_ori['entryTime'].apply(pd.Timestamp)
df_ori['time_delta'] = df_ori['entryTime'] - df_ori['pubDate']
print(f'原始shape = {df_ori.shape[0]}')
df_ori = df_ori[~df_ori['reportCode'].duplicated()].reset_index()
print(f'根据reportCode去重后shape = {df_ori.shape[0]}')
# 全面性
'''
只考虑非微信、中文、有pdf的报告
1、分年度，每天多少篇研报
2、分年度，申万行业分布、个股报告占比
3、深度报告占比
'''
total_num = df_ori.shape[0]
notwx_total_num = df_ori[df_ori['isWx'] == 0].shape[0]
chinese_total_num = df_ori[df_ori['isoType'] == '中文'].shape[0]


url_total_num = df_ori[df_ori['content_url'].apply(len) >= 5].shape[0]

df_ori_filter = df_ori[(df_ori['isWx'] == 0) & (df_ori['isoType'] == '中文') & (df_ori['content_url'].apply(len) >= 5)]
print(f'一共{total_num}篇研报')
print(f'其中非微信研报{notwx_total_num}篇，占比{notwx_total_num/total_num}；中文研报{chinese_total_num}篇，占比{chinese_total_num/total_num}；'
      f'有原文pdf的研报{url_total_num}篇，占比{url_total_num/total_num}')
print(f'只考虑中文、非微信来源、有pdf原件的研报，占比{df_ori_filter.shape[0] / total_num}')
#
num_by_year = df_ori_filter.groupby('year').apply(lambda x : x.groupby('date')['reportCode'].count().mean())
print('分年度，每日平均研报数量：')
print(num_by_year)
#
indu_num_by_year = df_ori_filter[df_ori_filter['industrySw'].apply(len) > 0].groupby('year').apply(lambda x : x.groupby('date')['reportCode'].count().mean())
print('分年度，每日平均行业研报数量：')
print(indu_num_by_year)

per_indu_num_all = df_ori_filter[df_ori_filter['industrySw_level'] == '1'].groupby('industrySw_name')['reportCode'].count()
per_indu_num_all = per_indu_num_all.sort_values()
print('全区间上，各一级行业研报数量分布：')
print(per_indu_num_all)

stock_num_by_year = df_ori_filter[df_ori_filter['tradingcode_list'].apply(lambda x : len(x[0]) == 6 if len(x) > 0 else False)].groupby('year').apply(lambda x : x.groupby('date')['reportCode'].count().mean())
print('分年度，每日平均个股研报数量：')
print(stock_num_by_year)
print(f'考察个股研报中是否有行业研报，0表示没有: {df_ori_filter[df_ori_filter["tradingcode_list"].apply(lambda x : len(x[0]) == 6 if len(x) > 0 else False)]["industrySw"].apply(len).max()}')
print(f'考察行业研报中是否有个股研报，0表示没有: {df_ori_filter[df_ori_filter["industrySw"].apply(lambda x : len(x)>0)]["tradingcode_list"].apply(len).max()}')

deep_num_by_year = df_ori_filter[df_ori_filter['pages'] >= 20].groupby('year')['reportCode'].count()
print('分年度，深度报告（20页以上）数量：')
print(deep_num_by_year)

## 个股覆盖度
'''
按月统计，该股票（限定A股）当月有个股研报则视为覆盖
'''
stock_num_by_month = df_ori_filter[df_ori_filter['tradingcode_list'].apply(lambda x : len(x[0]) == 6 if len(x) > 0 else False)].\
    groupby(['year','month']).apply(lambda x : len(set(x['tradingcode_list'].apply(lambda x : x[0]))))
print('每个月覆盖的股票数目：')
print(stock_num_by_month)

# 时效性
'''
分年度统计entrytime和pubdate的差异，统计2小时以内、2小时-12小时，12小时-24小时，24小时-48小时，48小时以上的占比
'''
df_ori_filter_time = df_ori_filter[df_ori_filter['pubDate'] >= pd.Timestamp('20240101')]
def get_time_delta_type(x):
    if x <= pd.Timedelta(hours=2):
        return 1
    elif x <= pd.Timedelta(hours=12):
        return 2
    elif x <= pd.Timedelta(hours=24):
        return 3
    elif x <= pd.Timedelta(hours=48):
        return 4
    elif x <= pd.Timedelta(hours=168):
        return 5
    else:
        return 6
df_ori_filter_time['time_delta_type'] = df_ori_filter_time['time_delta'].apply(get_time_delta_type)
time_delta_type_group = df_ori_filter_time.groupby('time_delta_type').count()['reportCode']
print(time_delta_type_group)
print(time_delta_type_group / time_delta_type_group.sum())

##### 测试解析结果
def get_all_content(start_date, end_date, content_path):
    res = pd.DataFrame()
    file_list = os.listdir(content_path)
    file_list = [f'{content_path}{i}' for i in file_list if i.replace('.pkl','') >= start_date and i.replace('.pkl','') <= end_date]
    file_list.sort()
    files = map(pd.read_pickle, file_list)
    res = pd.concat(files, sort = True)
    return res
content_path = '/dfs/group/800463/data/research_report_data/rr_content/'
df_content = get_all_content('20210101', '20211231', content_path)
df_content['content_length'] = df_content['content'].apply(len)
df_content[df_content['content_length'] >= 100].shape[0] / df_content.shape[0]

df_content[df_content['content_length'] >= 100].shape[0] / df_content[df_content['content_url'].apply(len) >= 10].shape[0]