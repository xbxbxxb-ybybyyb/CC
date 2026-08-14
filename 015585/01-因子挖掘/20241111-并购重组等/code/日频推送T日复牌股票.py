import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
import datetime
import tools
from xquant.textdata import NewsData

nd = NewsData()
s = FactorData()
def columns_filter(df,col=[]):
    if len(col) > 0:
        df = df[col]
    else:
        col = ['id','pubDate','textTitle','abs','tags','contentUrl',
                 'mediaName','categorys','industrySw','riskLevel','importance','sentiment','entryTime','updateTime']
        df = df.reindex(columns=col, fill_value=np.nan)
    return df
def generate_category(df,finchina_category_list=[]): # 保留category里面的tagcategory，只保留在财汇分类里的部分
    if 'categorys' in df.columns:
        def func_get_tagcategory(x):
            res = []
            if type(x) == list:
                for i in x:
                    res.append(i['tagcategory'])
            return res
        df['categorys'] = df['categorys'].apply(lambda x : func_get_tagcategory(x))
    else:
        pass
    return df
def tags_shsz(df):
    def get_shsz_stock(x):
        res = []
        if type(x) == list:
            for i in x:
                if 'tag' in i:
                    if '.SH' in i['tag'] or '.SZ' in i['tag']:
                        res.append(i['tag'])
        if not res:
            res.append('nostock')
        return res
    df['tags'] = df['tags'].apply(lambda x: get_shsz_stock(x))
    return df
def split_stock_tags(df, col_name='tags'): # 根据tags里在沪深的股票，记录一行变为多行，每行代表一只股票
    df_tmp = df[['id',col_name]]
    df_tmp_columns_list = df_tmp.columns.tolist()
    df_tmp_columns_list.remove(col_name)
    df_tmp = (df_tmp.set_index(df_tmp_columns_list)[col_name].apply(pd.Series).stack().reset_index().drop('level_' + str(len(df_tmp_columns_list)), axis=1)
          .rename(columns={0: 'new_' + col_name}))
    df = pd.merge(df,df_tmp,how = 'outer',left_on='id',right_on='id')
    return df
def change_col_type(df):
    df['pubDate'] = df['pubDate'].apply(lambda x : pd.Timestamp(x))
    df['entryTime'] = df['entryTime'].apply(lambda x : pd.Timestamp(x))
    df['updateTime'] = df['updateTime'].apply(lambda x : pd.Timestamp(x))
    return df
def transfer_AINEWS(df):
    df = df.rename(columns={
                    'id':'id',
                    'textTitle':'title',
                    'content':'content',
                    'pubDate':'pubtime',
                    'new_tags':'Ticker',
                    'abs':'abstract',
                    'mediaName':'medianame',
                    'entryTime':'entrytime',
                    'updateTime':'updatetime',
                    'tags':'Tickerlist'
                    })
    df['resource'] = 'ITAINEWS'
    df['Ticker'] = df['Ticker'].apply(lambda x : np.nan if x == 'nostock' else x)
    df['Tickerlist'] = df['Tickerlist'].apply(lambda x : [] if x == ['nostock'] else x)
    df['dt'] = df['pubtime'].apply(lambda x: pd.Timestamp(str(x).split(' ')[0]))
    df['is_value_by_time'] = 1
    # 计算effectivetime
    df['effectivetime'] = df['pubtime']
    df['timedelta'] = df['entrytime'] - df['pubtime']
    df.loc[(df['timedelta'] <= pd.Timedelta(days=1)) & (df['timedelta'] >= pd.Timedelta(days=0)),'effectivetime'] = \
        df.loc[(df['timedelta'] <= pd.Timedelta(days=1)) & (df['timedelta'] >= pd.Timedelta(days=0)),'entrytime']
    # 规范化
    col_list = ['id',
                'title',
                'abstract',
                'content',
                'pubtime',
                'effectivetime',
                'entrytime',
                'updatetime',
                'medianame',
                'resource',
                'dt',
                'Ticker',
                'Tickerlist',
                'is_value_by_time'
                ]
    df = df.reindex(columns= col_list)
    return df
## 入参
date = datetime.date.today().strftime('%Y-%m-%d')
next_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')

date = '2024-11-18'
next_date = '20241119'
tradingday_list = s.tradingday(next_date, -1)
# wind公告表部分
suspension = s.get_factor_value('WIND_AShareTradingSuspension',S_DQ_RESUMPDATE=['>={}'.format(tradingday_list[0])])
# 新闻数据部分
data = nd.get_ai_news_data(start_date="{} 00:00:00".format(str(date).split(' ')[0]), end_date="{} 23:00:00".format(str(date).split(' ')[0]))
data = columns_filter(data)
data['content'] = ''
data = change_col_type(data)
data = generate_category(data)
data = tags_shsz(data)
data = split_stock_tags(data)
data = transfer_AINEWS(data)
for col in ['content', 'title', 'abstract']:
    data[col] = data[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
data.reset_index(drop=True, inplace=True)
data = data[data['entrytime'] >= pd.Timestamp(f'{date} 15:00:00')]
suspension_news = data[(data['title'].str.contains('复牌')) & (~data['title'].str.contains('公告精选')) & (~data['title'].str.contains('涨停'))]
#
if suspension.empty and suspension_news.empty:
    tools.send_message(f'明日无复牌标的', ['015585'])
else:
    df_stk = s.get_factor_value('WIND_AShareDescription')
    list_stk = list(set(suspension['S_INFO_WINDCODE'])) if not suspension.empty else []
    list_stk_news = list(set(suspension_news['Ticker']))
    for i in list_stk_news:
        list_stk.append(str(i))
    list_stk.sort()
    list_stk = [x for x in list_stk if x.startswith('6') or x.startswith('3') or x.startswith('0')]
    name_list = list(df_stk[df_stk['S_INFO_WINDCODE'].isin(list_stk)]['S_INFO_NAME'])
    # tools.send_message(f'{list_stk}  {name_list}',['015585'])

print(list_stk)
print(name_list)