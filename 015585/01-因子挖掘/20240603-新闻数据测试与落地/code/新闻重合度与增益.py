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
def ths_is_a_stock(x):
    res = 0
    try:
        for i in eval(x)['stockInfo']:
            try:
                if '.SZ' in i['additionalParams']['hqCode'] or '.SH' in i['additionalParams']['hqCode']:
                    return 1
            except:
                pass
    except:
        return res
# for date in date_list:
def parallel_main_ths(date):
    print(date)
    file1 = date.strftime('%Y-%m-%d') + '.h5'
    file2 = date.strftime('%Y%m%d') + '.pkl'
    df1 = pd.read_hdf(path1 + file1)
    for del_string in del_string_list:
        df1 = df1[~df1['title'].str.contains(del_string)]
    df1 = df1[~df1['itemId'].duplicated()]
    df1 = df1.reset_index(drop=True)
    #
    df2 = pd.read_pickle(path2 + file2)
    df2 = df2[~df2['id'].duplicated()]
    df2 = df2.reset_index(drop=True)
    #
    res_autosimi_df1 = max_auto_similarity(df1,'title')
    df1 = res_autosimi_df1[0]
    res_date = max_similarity(df1,'title',df2,'textTitle',df2_name = df2_name) # 全部新闻相对于已有新闻的最大相似度
    res_date.to_pickle('/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/' + file2)
    return
def parallel_main_ths_a(date,delsimifile_path='/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/'):
    print(date)
    file1 = date.strftime('%Y%m%d') + '.pkl'
    file2 = date.strftime('%Y%m%d') + '.pkl'
    df1 = pd.read_pickle(delsimifile_path + file1)
    df1['is_a_stock'] = df1['entityLabel'].apply(lambda x : ths_is_a_stock(x))
    df1 = df1[df1['is_a_stock']==1]
    df1 = df1.reset_index(drop=True)
    #
    df2 = pd.read_pickle(path2 + file2)
    df2 = df2[df2['new_tags'] != 'nostock'] # A股相关
    df2 = df2[~df2['id'].duplicated()]
    df2 = df2.reset_index(drop=True)
    #
    res_date_tmp = max_similarity(df1,'title',df2,'textTitle',df2_name = 'ITnews_a') # 全部新闻相对于已有新闻的最大相似度
    res_date = pd.read_pickle(delsimifile_path + file1)
    res_date = pd.merge(res_date,res_date_tmp[['itemId','max_similarity_ITnews_a']],left_on='itemId',right_on='itemId',how='left')
    res_date.to_pickle(delsimifile_path + file1)
    return
start_date = '20240601'
end_date = '20240630'
print(start_date,end_date)
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
# 同花顺相对于AI新闻在2024年的增益
path1 = '/dfs/group/800463/data/news_data/ths_basicinfo/'
path2 = '/dfs/group/800463/data/news_data/AI_newsdata/'
date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
del_string_list = ['全球实时财经新闻直播',] # 特殊的标题做删除
df2_name = 'ITnews'
Parallel(n_jobs=20)(delayed(parallel_main_ths)(date,) for date in date_list)
Parallel(n_jobs=16)(delayed(parallel_main_ths_a)(date,) for date in date_list)
#
# # 读取同花顺相似度
res = pd.DataFrame(columns = ['length_ori','length_delsimi','length_upper80_afterdelsimi','length_a','length_a_delsimi','length_a_upper80_afterdelsimi'])
for file in os.listdir('/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/'):
    df_delsimi = pd.read_pickle('/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/' + file)
    file2 = file[:4]+'-'+file[4:6]+'-'+file[6:8]+'.h5'
    df_ori = pd.read_hdf(path1 + file2)
    res.loc[file.replace('.pkl',''),'length_ori'] = len(df_ori[~df_ori['itemId'].duplicated()])
    res.loc[file.replace('.pkl',''),'length_delsimi'] = len(df_delsimi)
    res.loc[file.replace('.pkl',''),'length_upper80_afterdelsimi'] = len(df_delsimi[df_delsimi['max_similarity_'+df2_name] > 0.8])
    res.loc[file.replace('.pkl',''),'length_a'] = len(df_ori[df_ori['entityLabel'].apply(lambda x : ths_is_a_stock(x)) == 1])
    res.loc[file.replace('.pkl',''),'length_a_delsimi'] = len(df_delsimi[~df_delsimi['max_similarity_ITnews_a'].isna()])
    res.loc[file.replace('.pkl',''),'length_a_upper80_afterdelsimi'] = len(df_delsimi[df_delsimi['max_similarity_ITnews_a'] > 0.8])
res['ratio_autosimi'] = 1 - res['length_delsimi']/res['length_ori']
res['ratio_simi_IT'] = res['length_upper80_afterdelsimi']/res['length_delsimi']
res['ratio_autosimi_a'] = 1 - res['length_a_delsimi']/res['length_a']
res['ratio_simi_IT_a'] = res['length_a_upper80_afterdelsimi']/res['length_a_delsimi']
print('自我相似度',res.mean()['ratio_autosimi'])
print('去重后所有新闻与所有已有新闻相似的占比:',res.mean()['ratio_simi_IT'])
print('自我相似度-A股部分',res.mean()['ratio_autosimi_a'])
print('去重后A股新闻与A股已有新闻相似的占比:',res.mean()['ratio_simi_IT_a'])
