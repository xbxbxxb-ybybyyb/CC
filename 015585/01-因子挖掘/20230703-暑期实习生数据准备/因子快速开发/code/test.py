import numpy as np
import pandas as pd
import os
import sys

# 读取已有的回测pkl文件 非mercury
path ='/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/因子快速开发/'
file_ori = os.listdir(path)
file_list = []
for i in file_ori:
    if i[-3:] == 'pkl':
#     if (i[-3:] == 'pkl') & ('vwap' in i):
        file_list.append(i)
res = pd.DataFrame(columns = ['IC','score','corr_factor','corr_max','corr_max_score','same_ratio','2019IC','group_max','group_min'])
def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r+str(i)+':'+str(round(df.loc[i,'in_score'],2))+";"
        r = r+str(i)+';'
    return r
for i in file_list:
    sys.stdout.write('\r'+str(i))
    sys.stdout.flush()
    result_dic_i = pd.read_pickle(path + i)
#     res.loc[i,'factor_name'] = i[:-4]
    i = i[:-4]
    res.loc[i,'IC'] = result_dic_i['corr_sta'].loc['corr_tot','value']
#     res.loc[i,'INFO'] = result_dic_i['corr_sta'].loc['mic_tot','value']
    res.loc[i,'score'] = result_dic_i['check_score_res'].loc['score','tot_score']
    res.loc[i,'corr_factor'] = get_corr_factor(result_dic_i['factor_corr_summary'])
    res.loc[i,'same_ratio'] = result_dic_i['other_sta'].iloc[0,2]
#     res.loc[i,'same_ratio'] = result_dic_i['max_same_ratio'].iloc[0,1]
    if res.loc[i,'IC'] > 0:
        res.loc[i,'group_max'] = result_dic_i['group_tot']['value'].tail(1).mean()
        res.loc[i,'group_min'] = result_dic_i['group_tot']['value'].head(1).mean()
    else:
        res.loc[i,'group_max'] = result_dic_i['group_tot']['value'].head(1).mean()
        res.loc[i,'group_min'] = result_dic_i['group_tot']['value'].tail(1).mean()
    # res.loc[i,'2019IC'] = result_dic_i['2019IC']
    corr_max_score_i = result_dic_i['factor_corr_summary']['in_score'].fillna(100).max()
    res.loc[i,'corr_max_score'] = corr_max_score_i if corr_max_score_i < 1000 else 0
    res.loc[i,'corr_max'] = result_dic_i['factor_corr']['factor_corr'].max()