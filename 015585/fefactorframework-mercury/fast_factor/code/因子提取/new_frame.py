import numpy as np
import pandas as pd
import os
import sys

strategy = 'neptune' # saturn
time_type = '20250820_xdbtick1m'
time_type_2021 = '20250820_xdbtick1m_2'
# 读取已有的回测Pkl文件 新框架
path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type + '/factor_test/' + strategy + '/'
file_ori = os.listdir(path)
print(f'共计{len(file_ori)}个文件')
file_list = []
## 新增获取因子分数要用v3的处理
if strategy == 'europa':
    check_res = pd.read_excel('/data/group/800463/data/project1_public/factor_lib_v3/check_res_tot_europa.xlsx')
    check_res = check_res.set_index('factor_name')[['in_score', 'in_IC_tot']]
elif strategy == 'saturn':
    check_res = pd.read_excel('/dfs/group/800463/data/project2_public/factor_lib/check_res_tot_saturn.xlsx')
    check_res = check_res.set_index('factor_name')[['in_score', 'in_IC_tot']]
elif strategy == 'neptune':
    check_res = pd.read_excel('/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx')
    check_res = check_res.set_index('factor_name')[['in_score', 'in_IC_tot']]

for i in file_ori:
    if i[-3:] == 'pkl':
        file_list.append(i)
res = pd.DataFrame(
    columns=['IC', 'score', 'score_2021','corr_factor', 'corr_max_score', 'same_ratio', '2019IC', 'group_max', 'group_min',
             'mutual_info'])

def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r + str(i) + ':' + 'nan' + ";"
    return r

# 补充和特定因子的相关性
special_factor_list = [
    # '930_after_all_all_0_bigger_all_b_change',
]
df_factor_spe = pd.DataFrame()
special_path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250806_t1mtickab/factor_value/neptune/'
for i in special_factor_list:
    df_factor_spe[i] = pd.read_hdf(f'{special_path}{i}.h5')[i]
#
path_spe = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type + '/factor_value/' + strategy + '/'
for i in file_list:
    sys.stdout.write('\r' + str(i))
    sys.stdout.flush()
    result_dic_i = pd.read_pickle(path + i)
    if strategy == 'neptune':
        path2021 = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type_2021 + '/factor_test/' + strategy + '/'
        result_dic_i_2021 = pd.read_pickle(path2021 + i)
    i = i[:-4]
    res.loc[i, 'IC'] = result_dic_i['corr_sta'].loc['corr_tot', 'value']
    if strategy == 'hotspot':
        res.loc[i, 'same_ratio'] = result_dic_i['other_sta'].iloc[0, 2]
    else:
        res.loc[i, 'score'] = result_dic_i['check_score_res'].loc['score', 'tot_score']
        res.loc[i, 'score_2021'] = result_dic_i_2021['check_score_res'].loc['score', 'tot_score']
        res.loc[i, 'corr_factor'] = get_corr_factor(
            result_dic_i['factor_corr_summary'].drop(['in_score', 'in_IC_tot'], axis=1).join(check_res))
        if strategy in ['europa']:
            res.loc[i, 'same_ratio'] = result_dic_i['other_sta'].iloc[0, 2]
        else:
            res.loc[i, 'same_ratio'] = result_dic_i['max_same_ratio'].iloc[0, 1]
        if res.loc[i, 'IC'] > 0:
            res.loc[i, 'group_max'] = result_dic_i['group_tot']['value'].tail(1).mean()
            res.loc[i, 'group_min'] = result_dic_i['group_tot']['value'].head(1).mean()
        else:
            res.loc[i, 'group_max'] = result_dic_i['group_tot']['value'].head(1).mean()
            res.loc[i, 'group_min'] = result_dic_i['group_tot']['value'].tail(1).mean()
        if strategy != 'neptune':
            try:
                res.loc[i, '2019IC'] = result_dic_i['2019IC']
            except:
                res.loc[i, '2019IC'] = np.nan
        corr_max_score_i = result_dic_i['factor_corr_summary'].drop(['in_score', 'in_IC_tot'], axis=1).join(check_res)[
            'in_score'].fillna(100).max()
        res.loc[i, 'corr_max_score'] = corr_max_score_i if corr_max_score_i < 1000 else 0
        res.loc[i, 'corr_max'] = result_dic_i['factor_corr']['factor_corr'].max()
        # 剔除和特定因子相关性过高的因子
        if len(special_factor_list) > 0:
            df_i = pd.read_hdf(path_spe + i + '.h5')
            corr_max = abs(df_factor_spe.corrwith(df_i[i])).max()
            if corr_max >= 0.7:
                res.loc[i, 'corr_max_score'] = 1000
                res.loc[i, 'corr_max'] = corr_max
                print(i, '和特别因子高相关，剔除')
print(len(res))

# 生成因子相关性 新框架
score_para = 15
IC_para = 0.01
mutual_para = 0.043
mutual = False
path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' +time_type + '/factor_value/' + strategy + '/'
if strategy == 'saturn':
    sft_basic_path = '/dfs/group/800463/data/project2_public/factor_lib/sft_update_filter_20160101_20191231.pkl'
    sft_basic_file = pd.read_pickle(sft_basic_path).loc[
         pd.to_datetime(str(int(20170110))):pd.to_datetime(str(int(20191231)))]
def get_factor_corr(path):
    file_ori = os.listdir(path)
    file_list = []
    for i in file_ori:
        if i[-2:] == 'h5':
            file_list.append(i)
    factor_value = pd.DataFrame()
    if strategy == 'hotspot':
        print('筛选IC={}以上因子'.format(IC_para))
        list_linear = list(res[abs(res['IC'])> IC_para].index)
        file_list = [x for x in file_list if x[:-3] in list_linear]
        print('{}IC以上因子个数'.format(IC_para),len(file_list))
    else:
        if mutual:
            print('筛选互信息{}以上因子'.format(mutual_para))
            list_linear = list(res[res['mutual_info']>mutual_para].index)
            file_list = [x for x in file_list if x[:-3] in list_linear]
            print('互信息{}以上因子个数'.format(mutual_para),len(file_list))
        else:
            print('筛选{}分以上因子'.format(score_para))
            list_linear = list(res[res['score']>score_para].index)
            file_list = [x for x in file_list if x[:-3] in list_linear]
            print('{}分以上因子个数'.format(score_para),len(file_list))
    for i in file_list:
        sys.stdout.write('\r'+str(i))
        sys.stdout.flush()
        factor_name = i.split('.')[0].replace('_20160101_20191231','')
        df_i = pd.read_hdf(path + i)
        factor_value[factor_name] = df_i[factor_name]
    print('')
    print('开始计算corr矩阵')
    if strategy == 'saturn':
        factor_corr = factor_value.reindex(sft_basic_file.index).rank().corr()
    if strategy == 'neptune':
        factor_corr = factor_value.rank().corr()
    if strategy == 'europa':
        factor_corr = factor_value.rank().corr()
    return factor_corr
factor_corr = get_factor_corr(path)

# 新增描述相关性的列 新框架
res['是否linear'] = 0
if strategy == 'hotspot':
    res.loc[(abs(res['IC']) > IC_para) & (res['same_ratio'] < 0.18),'是否linear'] = 1
    res['是否upper_base'] = 1
elif strategy == 'neptune':
    res.loc[(abs(res['IC']) > 0.008) & (res['same_ratio'] < 0.08) & (res['score'] > score_para) & (res['score_2021'] > res['score']*0.6),'是否linear'] = 1
    res['是否upper_base'] = 0
    res.loc[res['score'] >= res['corr_max_score']+4.5,'是否upper_base'] = 1
else:
    if mutual:
        res.loc[(res['mutual_info'] > mutual_para) & (res['same_ratio'] < 0.05),'是否linear'] = 1
        res['是否upper_base'] = 1
    else:
    #     res.loc[(res['score'] > score_para) & (res['same_ratio'] < 0.18)
    #             & (abs(res['2019IC']) >= abs(res['IC'])*0.7) & (abs(res['2019IC']) >= 0.04),'是否linear'] = 1
        res.loc[(res['score'] > score_para) & (res['same_ratio'] < 0.05),'是否linear'] = 1
        res['是否upper_base'] = 1
res['good_factor'] = 0
res['corr_factor'] = res['corr_factor'].apply(str)
# for i in res[(res['是否linear'] ==1) & (res['是否upper_base'] == 1) & ((res['corr_max']<0.685)|(res['corr_max_score'] > 1))].index:
for i in res[(res['是否linear'] ==1) & (res['是否upper_base'] == 1)].index:
    sys.stdout.write('\r'+str(i))
    sys.stdout.flush()
    list_inbase = list(res[res['good_factor']==1].index)
    corr_series_i = factor_corr[i]
    corr_series_i = set(corr_series_i[abs(corr_series_i)>=0.69].index)&set(list_inbase) # 计算得到高于0.7且在库内的因子
    list_i = list(set(corr_series_i))
    if strategy == 'hotspot':
        max_IC = abs(res.loc[list_i,'IC']).max()
        if np.isnan(max_IC):
            max_IC = 0
        if abs(res.loc[i,'IC']) > max_IC:
            res.loc[i,'good_factor'] = 1
            res.loc[list_i,'good_factor'] = 0
    else:
        max_score = res.loc[list_i,'score'].max()
        if np.isnan(max_score):
            max_score = 0
        if res.loc[i,'score'] > max_score:
            res.loc[i,'good_factor'] = 1
            res.loc[list_i,'good_factor'] = 0
if strategy == 'hotspot':
    res_good_factor = res[res['good_factor']==1].sort_values('IC',ascending = False)
else:
    res_good_factor = res[res['good_factor']==1].sort_values('score',ascending = False)
#=========================================================================================
print('')
print(len(res_good_factor))
print(res_good_factor)