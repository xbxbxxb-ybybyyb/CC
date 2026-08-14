import numpy as np
import pandas as pd
import os
import sys

strategy = 'neptune' #
time_type = '20250918_xdb_balancesheet_cs'
time_type_2021 = '20250901_xdbtick1m_2'
special_factor_list = [
    # '930_after_all_all_0_bigger_all_b_change',
] # 特定因子列表
special_path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250806_t1mtickab/factor_value/neptune/' # 特定因子路径
# =================读取已有的回测Pkl文件 新框架========================
path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type + '/factor_test/' + strategy + '/'
file_ori = os.listdir(path)
print(f'共计{len(file_ori)}个文件')
file_list = []
for i in file_ori:
    if i[-3:] == 'pkl':
        file_list.append(i)
## 获取因子分数
check_res = pd.read_excel('/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx')
check_res = check_res.set_index('factor_name')[['in_score', 'in_IC_tot']]
## 初始化
res = pd.DataFrame(
    columns=['IC', 'IC_2021', 'score', 'score_2021','corr_factor', 'corr_max_score', 'same_ratio', 'group_max', 'group_min',
             'mutual_info'])
def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r + str(i) + ':' + 'nan' + ";"
    return r
## 特定因子值
df_factor_spe = pd.DataFrame()
for i in special_factor_list:
    df_factor_spe[i] = pd.read_hdf(f'{special_path}{i}.h5')[i]
#
path2021 = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type_2021 + '/factor_test/' + strategy + '/'
for i in file_list:
    sys.stdout.write('\r' + str(i))
    sys.stdout.flush()
    result_dic_i = pd.read_pickle(path + i)
    try:
        result_dic_i_2021 = pd.read_pickle(path2021 + i)
    except:
        print('')
        print(i,'无2021文件')
        continue
    i = i[:-4]
    res.loc[i, 'IC'] = result_dic_i['corr_sta'].loc['corr_tot', 'value']
    res.loc[i, 'IC_2021'] = result_dic_i_2021['corr_sta'].loc['corr_tot', 'value']
    res.loc[i, 'score'] = result_dic_i['check_score_res'].loc['score', 'tot_score']
    res.loc[i, 'score_2021'] = result_dic_i_2021['check_score_res'].loc['score', 'tot_score']
    res.loc[i, 'corr_factor'] = get_corr_factor(
        result_dic_i['factor_corr_summary'].drop(['in_score', 'in_IC_tot'], axis=1).join(check_res))
    res.loc[i, 'same_ratio'] = result_dic_i['max_same_ratio'].iloc[0, 1]
    if res.loc[i, 'IC'] > 0:
        res.loc[i, 'group_max'] = result_dic_i['group_tot']['value'].tail(1).mean()
        res.loc[i, 'group_min'] = result_dic_i['group_tot']['value'].head(1).mean()
    else:
        res.loc[i, 'group_max'] = result_dic_i['group_tot']['value'].head(1).mean()
        res.loc[i, 'group_min'] = result_dic_i['group_tot']['value'].tail(1).mean()
    corr_max_score_i = result_dic_i['factor_corr_summary'].drop(['in_score', 'in_IC_tot'], axis=1).join(check_res)[
        'in_score'].fillna(100).max()
    res.loc[i, 'corr_max_score'] = corr_max_score_i if corr_max_score_i < 1000 else 0
    res.loc[i, 'corr_max'] = result_dic_i['factor_corr']['factor_corr'].max()
    # 剔除和特定因子相关性过高的因子
    if len(special_factor_list) > 0:
        df_i = pd.read_hdf(path + i + '.h5')
        corr_max = abs(df_factor_spe.corrwith(df_i[i])).max()
        if corr_max >= 0.7:
            res.loc[i, 'corr_max_score'] = 1000
            res.loc[i, 'corr_max'] = corr_max
            print(i, '和特别因子高相关，剔除')
print('')
# =================生成因子相关性 新框架========================
score_para = 13
IC_para = 0.008
mutual_para = 0.043
same_ratio_para = 0.08
mutual = False
path = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/' + strategy + '/' + time_type + '/factor_value/' + strategy + '/'

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
    factor_corr = factor_value.rank().corr()
    return factor_corr
factor_corr = get_factor_corr(path)

# =================输出最终结果 新框架========================
res['是否linear'] = 0
res['good_factor'] = 0
res['是否upper_base'] = 0

res.loc[(abs(res['IC']) >= IC_para)
        & (res['same_ratio'] <= same_ratio_para)
        & (res['score'] >= score_para)
        & (res['score_2021'] > res['score']*0.6),'是否linear'] = 1
        # & (res['IC'].apply(np.sign) == res['IC_2021'].apply(np.sign)),'是否linear'] = 1
res.loc[res['score'] >= res['corr_max_score']+4.5,'是否upper_base'] = 1
res['corr_factor'] = res['corr_factor'].apply(str)

for i in res[(res['是否linear'] ==1) & (res['是否upper_base'] == 1)].index:
    sys.stdout.write('\r'+str(i))
    sys.stdout.flush()
    list_inbase = list(res[res['good_factor']==1].index)
    corr_series_i = factor_corr[i]
    corr_series_i = set(corr_series_i[abs(corr_series_i)>=0.69].index)&set(list_inbase) # 计算得到高于0.7且在库内的因子
    list_i = list(set(corr_series_i))

    max_score = res.loc[list_i,'score_2021'].max() # 库内因子的max score，可以用2021代替
    if np.isnan(max_score):
        max_score = 0
    if res.loc[i,'score_2021'] > max_score:
        res.loc[i,'good_factor'] = 1
        res.loc[list_i,'good_factor'] = 0
res_good_factor = res[res['good_factor']==1].sort_values('score',ascending = False)
#=========================================================================================
print('')
print(len(res_good_factor))
print(res_good_factor)

# 930_after_all_all_0_bigger_all_ratiob_m2m
# 930_after_all_all_0_bigger_all_s12s_tail
# 930_after_all_all_0_bigger_all_tran2b_m2m
# 930_after_all_all_0_bigger_all_b_max
# 930_after_all_all_0_bigger_all_s2transtd_std
# 930_after_all_all_0_bigger_all_abspchange_cct
# 930_after_all_all_0_bigger_all_b12b_med
# 930_after_all_all_0_bigger_all_pv_skew
# 930_after_all_all_0_bigger_all_pv_kurt
# 930_after_all_all_0_bigger_all_b12b_kurt
# 930_after_all_all_0_bigger_all_amt2newamt_std
# 930_after_all_all_0_bigger_all_s2transtd_min
# 930_after_all_all_0_bigger_all_tvwap2pmin_nocalc
