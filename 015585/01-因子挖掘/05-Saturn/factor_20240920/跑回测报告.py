# 每次修改第二行
from run_factor_demo import run_factor
from project_2_factor_test_origin import pj2FactorTest
import pandas as pd
import numpy as np
import os
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type'''

date = '20240920' #周四日期
factor_name = 'factor_qyh_sat_news_20240920_1'
m = __import__(factor_name)
func = getattr(m,factor_name)
factor_path = '/data/user/015585/01-因子挖掘/05-Saturn/factor_' + date + '/'
start_date = 20160101
end_date = 20191231
if os.path.exists(factor_path + factor_name + '_'+str(start_date)+'_'+str(end_date) + '.h5'):
    print('remove')
    os.remove(factor_path + factor_name + '_'+str(start_date)+'_'+str(end_date) + '.h5')
run_factor(func = func,
          factor_name = factor_name,
          factor_type = 'T-1_factor',# LastZtLastTick,T-1_factor，T1mTickab
          start_date = start_date,
          end_date = end_date,
          basic_file_path = '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5',
          result_path = factor_path )
df = pd.read_hdf(factor_path + factor_name +
                 '_'+str(start_date)+'_'+str(end_date)+'.h5')
# df = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/saturn/wj_TTick_new_test.h5')
result_path = factor_path
factor_test = pj2FactorTest(start_date, end_date, cal_mi=False)
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    check_score = factor_test.result_dic['check_score_res']
    # print(check_score['value_diff_score']['score'],check_score['value_stability_score']['score'])
    print('总分:', check_score.loc['score', 'tot_score'])
    print('CORR：', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'].sort_values('factor_corr',ascending = False))
    print('均值与中位数与标准差:', factor_test.basic_df['factor'].mean(), '', factor_test.basic_df['factor'].median(), '',
          factor_test.basic_df['factor'].std())
    print(factor_test.result_dic['max_same_ratio'])
    test = factor_test.basic_df[['factor', 'value']]
    corr_qr = test[abs(test['value']) >= 5].corr(method='spearman').iloc[0, 1]
    print('强势股与弱势股IC：', corr_qr)
    print('2019年IC: ',factor_test.result_dic['2019IC'])
