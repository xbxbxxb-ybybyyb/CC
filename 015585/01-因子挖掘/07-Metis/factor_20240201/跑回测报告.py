# 每次修改第二行
from run_factor_demo_metis import run_factor
import os
# from metis_test_demo import strongFactorTest
from metis_test_demo_forzbw import strongFactorTest
import pandas as pd
import numpy as np
'''
'''
date = '20240201'#周四日期
factor_name = 'factor_qyh_20240201_test'
m = __import__(factor_name)
func = getattr(m,factor_name)
print(factor_name)
start_date, end_date = 20160101, 20191231  # 因子的样本内区间：16-19年
basic_file_path = '/dfs/group/800463/data/project1_public/factor_lib_metis/Basic_metis_20160101_20191231.h5'
result_path = '/data/user/015585/01-因子挖掘/07-Metis/factor_' + date + '/'
if os.path.exists(result_path + factor_name + '.h5'):
    os.remove(result_path + factor_name + '.h5')
factor_df0 = run_factor(func,
                        factor_name,
                        'TTickab_MetisAll',##
                        start_date, end_date,
                        basic_file_path,
                        result_path, interval_res=False)
df = pd.read_hdf(result_path + factor_name + '.h5')
# 非快速拉升
# print('全样本')
factor_test = strongFactorTest(start_date, end_date)
# factor_test = StrongFactorTest(start_date, end_date,cal_mi=None,strategy_name = 'europa')
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]],result_path=result_path, factor_corr_test=True,)
    check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['Touch_Time'].copy(),
                                 factor_test.result_dic['corr_month'].copy(),
                                 np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
    print('check_score:',check_score.loc['score','tot_score'])
    print('IC：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
    print('均值和中位数: ',factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
    print('重复值: ',factor_test.result_dic['other_sta'])
    test = factor_test.basic_df[['factor','value']]
    corr_qr = test[abs(test['value'])>=5].corr(method = 'spearman').iloc[0,1]
    print('强势股与弱势股IC：',corr_qr)
    test = factor_test.basic_df[['factor', 'value']].sort_values('factor')
    print('2019年IC: ',
          test[test.index.get_level_values(0) >pd.Timestamp('20190101')]
          .corr(method='spearman').loc['factor','value'])