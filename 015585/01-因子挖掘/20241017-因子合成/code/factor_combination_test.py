import numpy as np
import pandas as pd
import os
import sys

strategy = 'europa' # saturn
time_type = '20241017_ttick_t_1'
std_method = 'zscore' # ['zscore','minmax']
combine_method = 'ic' # 'ic','ir','equal','mult'
start_date = 20160101
end_date = 20191231
path1_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017T-1_combination/'
path1_test = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/回测报告/20241017T-1_combination/'
path2_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017TTick_combination/'
path2_test = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/回测报告/20241017TTick_combination/'
def ic_combinate(factor1, factor2, res1, res2):
    ic1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_tot', 'value']
    ic2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_tot', 'value']
    res = ic1 * res1[factor1] + ic2 * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'ic', factor2)])
def ir_combinate(factor1, factor2, res1, res2):
    ir1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_month_std', 'value']
    ir2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_month_std', 'value']
    res = ir1 * res1[factor1] + ir2 * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'ir', factor2)])
def equal_combinate(factor1, factor2, res1, res2):
    ic1 = pd.read_pickle('{}{}.pkl'.format(path1_test, factor1))['corr_sta'].loc['corr_tot', 'value']
    ic2 = pd.read_pickle('{}{}.pkl'.format(path2_test, factor2))['corr_sta'].loc['corr_tot', 'value']
    res = np.sign(ic1) * res1[factor1] + np.sign(ic2) * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'equal', factor2)])
def mult_combinate(factor1, factor2, res1, res2):
    res = res1[factor1] * res2[factor2]
    return pd.DataFrame(res, columns = ['{}*{}*{}'.format(factor1, 'mult', factor2)])
dic_combine_method = {
    'ic': ic_combinate,
    'ir': ir_combinate,
    'equal': equal_combinate,
    'mult': mult_combinate
}
# 读取已有的回测Pkl文件 新框架
path = f'/dfs/user/015585/01_factor_develop_store/fast_factor_combination/{strategy}/{time_type}/factor_test/{std_method}/{combine_method}/'
file_ori = os.listdir(path)
file_list = []
for i in file_ori:
    if i[-3:] == 'pkl':
        file_list.append(i)
res = pd.DataFrame(columns = ['IC','score','corr_factor','corr_max_score',
                              'same_ratio','2019IC',
                              'corr_l','corr_r','IC_l','IC_r','score_l','score_r',
                              'group_max','group_min'])
def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r+str(i)+':'+'nan'+";"
    return r
file_list = file_list[:]
for i in file_list:
    sys.stdout.write('\r'+str(i))
    sys.stdout.flush()
    result_dic_i = pd.read_pickle(path + i)
    i = i[:-4]
    #
    left_name = i.split('*')[0]
    right_name = i.split('*')[2]
    factor_df = pd.read_pickle(path.replace('factor_test','h5') + i + '.pkl').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    left_h5 = pd.read_hdf(path1_factor + left_name + '.h5').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    right_h5 = pd.read_hdf(path2_factor + right_name + '.h5').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    res.loc[i, 'corr_l'] = pd.concat([left_h5, factor_df],axis=1).corr(method = 'spearman').iloc[0, 1]
    res.loc[i, 'corr_r'] = pd.concat([right_h5, factor_df], axis=1).corr(method='spearman').iloc[0, 1]
    res.loc[i, 'IC_l'] = pd.read_pickle(path1_test + left_name + '.pkl')['corr_sta'].loc['corr_tot','value']
    res.loc[i, 'IC_r'] = pd.read_pickle(path2_test + right_name + '.pkl')['corr_sta'].loc['corr_tot','value']
    res.loc[i, 'score_l'] = pd.read_pickle(path1_test + left_name + '.pkl')['check_score_res'].loc['score','tot_score']
    res.loc[i, 'score_r'] = pd.read_pickle(path2_test + right_name + '.pkl')['check_score_res'].loc['score','tot_score']
    #
    res.loc[i,'IC'] = result_dic_i['corr_sta'].loc['corr_tot','value']
    res.loc[i,'score'] = result_dic_i['check_score_res'].loc['score','tot_score']
    res.loc[i,'corr_factor'] = get_corr_factor(result_dic_i['factor_corr_summary'])
    if strategy in ['europa']:
        res.loc[i,'same_ratio'] = result_dic_i['other_sta'].iloc[0,2]
    else:
        res.loc[i,'same_ratio'] = result_dic_i['max_same_ratio'].iloc[0,1]
    if res.loc[i,'IC'] > 0:
        res.loc[i,'group_max'] = result_dic_i['group_tot']['value'].tail(1).mean()
        res.loc[i,'group_min'] = result_dic_i['group_tot']['value'].head(1).mean()
    else:
        res.loc[i,'group_max'] = result_dic_i['group_tot']['value'].head(1).mean()
        res.loc[i,'group_min'] = result_dic_i['group_tot']['value'].tail(1).mean()
    res.loc[i,'2019IC'] = result_dic_i['2019IC']
    corr_max_score_i = result_dic_i['factor_corr_summary']['in_score'].fillna(100).max()
    res.loc[i,'corr_max_score'] = corr_max_score_i if corr_max_score_i < 1000 else 0
    res.loc[i,'corr_max'] = result_dic_i['factor_corr']['factor_corr'].max()

# 生成因子相关性 新框架
score_para = 35
delta_para = 5
path = f'/dfs/user/015585/01_factor_develop_store/fast_factor_combination/{strategy}/{time_type}/h5/{std_method}/{combine_method}/'
def get_factor_corr(path):
    file_ori = os.listdir(path)
    file_list = []
    for i in file_ori:
        if i[-3:] == 'pkl':
            file_list.append(i)
    factor_value = pd.DataFrame()
    print('筛选{}分以上,且若相关性高于70%，得分超出{}以上的因子'.format(score_para,delta_para))
    condition1 = ((res['score'] > res['score_l'] + delta_para) & (abs(res['corr_l']) >= 0.68)) | (abs(res['corr_l']) < 0.68)
    condition2 = ((res['score'] > res['score_r'] + delta_para) & (abs(res['corr_r']) >= 0.68)) | (abs(res['corr_r']) < 0.68)
    list_linear = list(res[(res['score']>score_para) & condition1 & condition2].index)
    file_list = [x for x in file_list if x[:-4] in list_linear]
    print('{}分以上,得分超出{}以上因子个数'.format(score_para,delta_para),len(file_list))
    for i in file_list:
        sys.stdout.write('\r'+str(i))
        sys.stdout.flush()
        factor_name = i.split('.')[0]
        df_i = pd.read_pickle(path + i)
        factor_value[factor_name] = df_i[factor_name]
    print('开始计算corr矩阵')
    factor_value = factor_value.rank().corr()
    return factor_value
factor_corr = get_factor_corr(path)

# 新增描述相关性的列 新框架
res['是否linear'] = 0
condition1 = ((res['score'] > res['score_l'] + delta_para) & (abs(res['corr_l']) >= 0.68)) | (abs(res['corr_l']) < 0.68)
condition2 = ((res['score'] > res['score_r'] + delta_para) & (abs(res['corr_r']) >= 0.68)) | (abs(res['corr_r']) < 0.68)
res.loc[(res['score'] > score_para) & (res['same_ratio'] < 0.18) & (res['corr_factor'] == '')
        & (abs(res['2019IC']) >= abs(res['IC'])*0.7)
        & condition1 & condition2,'是否linear'] = 1
res['是否upper_base'] = 0
res.loc[res['score'] >= res['corr_max_score'],'是否upper_base'] = 1
res['good_factor'] = 0
for i in res[(res['是否linear'] ==1) & (res['是否upper_base'] == 1) & ((res['corr_max']<0.68)|(res['corr_max_score'] > 1))].index:
    sys.stdout.write('\r'+str(i))
    sys.stdout.flush()
    list_inbase = list(res[res['good_factor']==1].index)
    corr_series_i = factor_corr[i]
    corr_series_i = set(corr_series_i[abs(corr_series_i)>=0.7].index)&set(list_inbase) # 计算得到高于0.7且在库内的因子
    list_i = list(set(corr_series_i))
    max_score = res.loc[list_i,'score'].max()
    if np.isnan(max_score):
        max_score = 0
    if res.loc[i,'score'] > max_score:
        res.loc[i,'good_factor'] = 1
        res.loc[list_i,'good_factor'] = 0
res_good_factor = res[res['good_factor']==1].sort_values('score',ascending = False)
#=========================================================================================
print('')
print(len(res_good_factor))