import pandas as pd
import os
import difflib
import copy
from joblib import Parallel, delayed
'''
按“正文优先”“时间优先”原则对新闻数据逻辑删除
对按时间排序后的每一条记录i：
1、若自身有正文，则
    1）若无相似度高于0.8的有效新闻，i的is_value记为1
    2）否则，若有效新闻中存在有正文且相似度高于0.8的记录，i的is_value记为0（逻辑删除）
    3）否则说明有效新闻中相似度高于0.8的均无正文，i的is_Value记为1，相似度高于0.8的有效新闻置为无效
2、否则自身无正文，则
    1）若有效新闻中存在相似度高于0.8的记录，i的is_value记为0
    2）否则i的is_value记为1
注意：按长度是否>20作为有无正文的判断标准
'''
def calculate_similarity(text1, text2):
    matcher = difflib.SequenceMatcher(None, text1[:50], text2[:50])
    similarity = matcher.ratio()
    return similarity
def drop_duplicate_by_time(df):
    df_ori = copy.deepcopy(df)
    df = df.reset_index(drop=True)
    df = df.drop_duplicates(subset=['id','resource'])
    df['is_value_by_time'] = 0
    df = df.sort_values('effectivetime')
    print(len(df))
    count = 0
    for i in df.index:
        # print(count)
        count = count+1
        df_is_value = df[df['is_value_by_time'] == 1].copy()
        df_is_value['similarity_ratio'] = df_is_value['title'].apply(lambda x : calculate_similarity(x ,df.loc[i,'title']))
        if len(df.loc[i,'content']) > 20:
            if not df_is_value['similarity_ratio'].max() >= 0.8:
                df.loc[i,'is_value_by_time'] = 1
            elif df_is_value[df_is_value['similarity_ratio'] >= 0.8]['content'].apply(lambda x :len(x)).max() > 20:
                df.loc[i, 'is_value_by_time'] = 0
            else:
                df.loc[i, 'is_value_by_time'] = 1
                df.loc[df_is_value[df_is_value['similarity_ratio'] >= 0.8].index, 'is_value_by_time'] = 0
        else:
            if df_is_value['similarity_ratio'].max() >= 0.8:
                df.loc[i, 'is_value_by_time'] = 0
            else:
                df.loc[i, 'is_value_by_time'] = 1
    df = pd.merge(df_ori,df[['id','resource','is_value_by_time']],left_on=['id','resource'],right_on=['id','resource'])
    df = df.sort_values(['effectivetime','id']).reset_index(drop=True)
    return df
def parallel_main(date):
    df = pd.read_pickle(base_path + date + '.pkl', compression='gzip')
    for col in ['content', 'title', 'abstract']:
        df[col] = df[col].apply(lambda x: '' if (type(x) == float or x is None) else x)
    try:
        print(date)
        if not 'is_value_by_time' in list(df.columns):
            df = drop_duplicate_by_time(df)
            df.to_pickle(base_path + date + '.pkl', compression='gzip')
        else:
            print(date , '已进行过去重')
    except Exception as e:
        print(e)
        print(date,'error')
    return

base_path = '/dfs/group/800463/data/news_data/news_data_combo/'
start_date = '20200101'
end_date = '20240630'
date_list = os.listdir(base_path)
date_list = [x.replace('.pkl','') for x in date_list]
date_list = [x for x in date_list if x >= start_date and x <= end_date]
date_list.sort()
# date = date_list[0]
#
Parallel(n_jobs=24)(delayed(parallel_main)(date) for date in date_list)

