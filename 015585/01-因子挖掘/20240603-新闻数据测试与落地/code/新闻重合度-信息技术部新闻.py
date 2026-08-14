import pandas as pd
import numpy as np
import os
import difflib
from joblib import Parallel, delayed
import datetime

def calculate_similarity(text1, text2):
    matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity = matcher.ratio()
    return similarity
def generate_max_similarity(text1,series2):
    return series2.apply(lambda x : calculate_similarity(text1,x)).max()
def max_similarity(df1,col_title1,df2,col_title2,df2_name):
    '''
    在df1中新增一列，含义为“df1的标题列，在df2中的最大相似度”
    '''
    tmp = df2[col_title2].apply(lambda x : x[:20])
    df1['max_similarity_' + df2_name] = df1[col_title1].apply(lambda x : generate_max_similarity(x[:20], tmp))
    return df1
def max_auto_similarity(df,col,ratio = 0.8):
    '''
    返回list
    1、剔除该列和自身其他元素相关性>0.8的行后的df
    2、剔除比例
    '''
    res = []
    error_list = []
    length1 = len(df)
    tmp = df.copy()
    tmp[col] = tmp[col].apply(lambda x : x[:20])
    for i in tmp.index:
        simi = generate_max_similarity(str(tmp.loc[i,col]),tmp[tmp.index>i][col])
        # print(i,simi)
        if simi >= ratio:
            tmp.drop(i,inplace=True)
            error_list.append(i)
    res.append(df.reindex(tmp.index))
    res.append(len(tmp) / length1)
    res.append(error_list)
    return res
# for date in date_list:
def parallel_main_IT(date):
    print(date)
    file2 = date.strftime('%Y%m%d') + '.pkl'
    #
    df2 = pd.read_pickle(path2 + file2)
    df2 = df2[~df2['id'].duplicated()]
    df2 = df2.reset_index(drop=True)
    #
    res_autosimi_df2 = max_auto_similarity(df2,'textTitle')
    df2 = res_autosimi_df2[0]
    df2.to_pickle('/dfs/group/800463/data/news_data/AI_newsdata_delsimi/' + file2)
    return

start_date = '20240601'
end_date = '20240630'
print(start_date,end_date)
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
# AI新闻自相关度
path2 = '/dfs/group/800463/data/news_data/AI_newsdata/'
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
Parallel(n_jobs=11)(delayed(parallel_main_IT)(date,) for date in date_list)
#
res = pd.DataFrame(columns = ['length_ori','length_delsimi','length_ori_a','length_delsimi_a'])
for file in os.listdir('/dfs/group/800463/data/news_data/AI_newsdata_delsimi/'):
    df_delsimi = pd.read_pickle('/dfs/group/800463/data/news_data/AI_newsdata_delsimi/' + file)
    # file2 = file[:4]+'-'+file[4:6]+'-'+file[6:8]+'.h5'
    df_ori = pd.read_pickle(path2 + file)
    res.loc[file.replace('.pkl',''),'length_ori'] = len(df_ori[~df_ori['id'].duplicated()])
    res.loc[file.replace('.pkl',''),'length_delsimi'] = len(df_delsimi)
    res.loc[file.replace('.pkl',''),'length_ori_a'] = len(df_ori[(~df_ori['id'].duplicated()) & (df_ori['new_tags'] != 'nostock')])
    res.loc[file.replace('.pkl',''),'length_delsimi_a'] = len(df_delsimi[df_delsimi['new_tags'] != 'nostock'])
res['ratio_autosimi'] = 1 - res['length_delsimi']/res['length_ori']
res['ratio_autosimi_a'] = 1 - res['length_delsimi_a']/res['length_ori_a']
print('IT新闻自我相似度',res.mean()['ratio_autosimi'])
print('IT新闻自我相似度-A股',res.mean()['ratio_autosimi_a'])

