# @Time : 2020/12/7 9:51
# @Author : Zhichen Lu
# @File : factor5min_analysis.py

import pandas as pd
import os
from conf.path_config import root_path
factor_path = '/data/group/800319/junkBigFactorPool/'
factor_eval_path = factor_path+'level2_waiting/'
# factor_eval_path = '/data/group/800319/FixFactorTestResult/'
eval_res_list = os.listdir(factor_eval_path)

barly_ret = []
ic_list = []
for each in eval_res_list:
    temp_res = pd.read_pickle(factor_eval_path+each)
    barly_ret.append([each]+temp_res['dc_t_all_ret'].tolist())
    ic_list.append([each,temp_res['ic_all_t'],temp_res['ic_all_d'],temp_res['ic_all_c'],temp_res['ic_all_dtc']])
    break

ic_df = pd.DataFrame(ic_list).set_index(0)
ic_df.columns = ['ic_all_t','ic_all_d','ic_all_c','ic_all_dtc']
check = pd.DataFrame(barly_ret).set_index(0)
check['std'],check['mean'] = check.std(axis=1),check.mean(axis=1)
check['adjusted_std'] = check['std']/check['mean']
check = pd.concat([check,abs(ic_df)],axis=1)
# check = check.sort_values('std').T.drop(['std'],axis=0)
check.to_excel('/data/user/015664/AFuckingTrigger/barly_ret.xlsx')

factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
factor_list = factor_evaluation['ic_all_t'].apply(abs).sort_values(ascending=False).index.tolist()[:400]


check = pd.read_excel('/data/user/015664/AFuckingTrigger/barly_ret.xlsx',index_col=0)
check['t_to_std'] = check['ic_all_t']/check['adjusted_std']
check['c_to_std'] = check['ic_all_c']/check['adjusted_std']
check['d_to_std'] = check['ic_all_d']/check['adjusted_std']
check['score'] = check[['t_to_std','c_to_std','d_to_std']].mean(axis=1)
selected = check.sort_values('score',ascending=False)[:300]
selected = selected[((selected['ic_all_t']>check['ic_all_t'].quantile(0.8))+
                 (selected['ic_all_c']>check['ic_all_c'].quantile(0.8))+
                 (selected['ic_all_d']>check['ic_all_d'].quantile(0.8)))>0]
selected = selected.sort_values('score',ascending=False)




################F
import pandas as pd
import os
from conf.path_config import root_path
# factor_path = '/data/group/800319/junkBigFactorPool/'
# factor_eval_path = factor_path+'level2_waiting/'
factor_eval_path = '/data/group/800319/FixFactorTestResult/'
eval_res_list = os.listdir(factor_eval_path)
barly_ret = []
ic_list = []
for each in eval_res_list:
    temp_res = pd.read_pickle(factor_eval_path+each)
    barly_ret.append([each]+temp_res['dc_t_all_ret'].tolist())
check = pd.DataFrame(barly_ret).set_index(0)
check['std'],check['mean'] = check.std(axis=1),check.mean(axis=1)
check['adjusted_std'] = (check['std']/check['mean']).apply(abs)
factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
check[['ic_all_t','ic_all_d','ic_all_c','ic_all_dtc']] = abs(factor_evaluation[['ic_all_t','ic_all_d','ic_all_c','ic_all_dtc']])
check['t_to_std'] = check['ic_all_t']/check['adjusted_std']
check['c_to_std'] = check['ic_all_c']/check['adjusted_std']
check['d_to_std'] = check['ic_all_d']/check['adjusted_std']
check['score'] = check[['t_to_std','c_to_std','d_to_std']].mean(axis=1)
selected = check.sort_values('t_to_std',ascending=False)[:600]
selected = selected[((selected['ic_all_t']>check['ic_all_t'].quantile(0.8))+
                 (selected['ic_all_c']>check['ic_all_c'].quantile(0.8))+
                 (selected['ic_all_d']>check['ic_all_d'].quantile(0.8)))>0]
