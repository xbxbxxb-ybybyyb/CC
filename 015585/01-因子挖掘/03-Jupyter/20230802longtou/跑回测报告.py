# 每次修改第二行
from run_factor_demo import run_factor
from factor_qyh_days_listdate import factor_qyh_days_listdate as func
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type
'''
date = '20230802longtou'#周四日期
factor_name = 'factor_qyh_days_listdate'
print(factor_name)
start_date, end_date = 20160101, 20191231  # 因子的样本内区间：16-19年
basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'
result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/' + date + '/'
factor_df0 = run_factor(func,
                        factor_name,
                        'T-1_factor',## TTickab,TOrder
                        start_date, end_date,
                        basic_file_path,
                        result_path, interval_res=False)
# TTransaction,LastTouchTTick
df = pd.read_hdf(result_path + factor_name + '.h5')
# 非快速拉升
print('全样本')
factor_test = strongFactorTest(20160101, 20191231,after_not_ul_len = 40)
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['ZT_Time'].copy(),
                                 factor_test.result_dic['corr_month'].copy(),
                                 np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
    print('check_score:',check_score.loc['score','tot_score'])
    print('IC：',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
    print('均值和中位数: ',factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
    print('重复值: ',factor_test.result_dic['other_sta'])