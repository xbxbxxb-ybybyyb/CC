# 每次修改第二行
from run_factor_demo_parallel import run_factor
from project_2_factor_test_origin import pj2FactorTest
import pandas as pd
import os

date = '20231130'#周四日期
factor_name = 'factor_qyh_next_md_20231130_1'
m = __import__(factor_name)
func = getattr(m,factor_name)
print(factor_name)
factor_path = '/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/'
start_date = 20160101
end_date = 20191231
if os.path.exists(factor_path + factor_name + '_'+str(start_date)+'_'+str(end_date) + '.h5'):
    print('remove')
    os.remove(factor_path + factor_name + '_'+str(start_date)+'_'+str(end_date) + '.h5')
run_factor(func = func,
          factor_name = factor_name,
          factor_type = 'Next_T-1_factor',#TallTick,Next_T-1_factor,Next1mTickab
          start_date = start_date,
          end_date = end_date,
          basic_file_path = '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5',
          result_path = factor_path)

# start_date, end_date = 20180601, 20180601
df = pd.read_hdf('/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/' + factor_name +
                 '_'+str(start_date)+'_'+str(end_date)+'.h5')
result_path = '/data/user/015585/01-因子挖掘/06-SaturnNext/' + date + '/'
factor_test = pj2FactorTest(start_date, end_date,cal_mi = False)
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
    print('均值与中位数与标准差:',factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median(),'',factor_test.basic_df['factor'].std())
    print(factor_test.result_dic['max_same_ratio'])
    test = factor_test.basic_df[['factor','value']]
    corr_qr = test[abs(test['value'])>=5].corr(method = 'spearman').iloc[0,1]
    print('强势股与弱势股IC：',corr_qr)
    test = factor_test.basic_df[['factor', 'value']].sort_values('factor')
    print('2019年IC: ',
          test[test.index.get_level_values(0) >pd.Timestamp('20190101')]
          .corr(method='spearman').loc['factor','value'])
