# 每次修改第二行
from run_factor_demo_parallel import run_factor
from factor_qyh_md_plus_price_20_mean import factor_qyh_md_plus_price_20_mean as func
from project_2_factor_test_origin import pj2FactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type
'''

date = '20230727'#周四日期
factor_name = 'factor_qyh_md_plus_price_20_mean'
factor_path = '/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/'
run_factor(func = func,
          factor_name = factor_name,
          factor_type = 'Next_T-1_factor',
          start_date = 20160101,
          end_date = 20191231,
          basic_file_path = '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5',
          result_path = factor_path)

start_date, end_date = 20160101, 20191231
df = pd.read_hdf('/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/' + factor_name + '_20160101_20191231.h5')
result_path = '/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/'
factor_test = pj2FactorTest(start_date, end_date)
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    check_score = factor_test.result_dic['check_score_res']
    # print(check_score['value_diff_score']['score'],check_score['value_stability_score']['score'])
    print('总分:',check_score.loc['score','tot_score'])
    print('CORR：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
    print('均值与中位数:',factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
    print(factor_test.result_dic['max_same_ratio'])
