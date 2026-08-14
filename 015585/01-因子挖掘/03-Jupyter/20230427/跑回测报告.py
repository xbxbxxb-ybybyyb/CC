# 每次修改第二行
from run_factor_demo import run_factor
from factor_qyh_mind_count1_1 import factor_qyh_mind_count1_1
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type'''
date = '20230427'#周四日期
factor_name = 'factor_qyh_mind_count1_1'
print(factor_name)
start_date, end_date = 20160101, 20191231  # 因子的样本内区间：16-19年
basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'
result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/' + date + '/'
factor_df0 = run_factor(factor_qyh_mind_count1_1,
                        factor_name,
                        'MarketIndTTick',
                        start_date, end_date,
                        basic_file_path,
                        result_path, interval_res=False)
# TTransaction,LastTouchTTick
df = pd.read_hdf(result_path + factor_name + '.h5')
result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/' + date + '/'
# factor_test = pj2FactorTest(start_date, end_date, buy_type='0931', lzt_pattern=[3, 4], high_open=0.08)
factor_test = strongFactorTest(start_date, end_date)
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    print('check_score:')
    check_score = factor_test.check_score(factor_test.result_dic['double_group_sort']['ZT_Time'].copy(),
                                 factor_test.result_dic['corr_month'].copy(),
                                 np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']))[1]
    print(check_score.loc['score','tot_score'])
    print('互信息：')
    print(factor_test.result_dic['corr_sta'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
    print('均值和中位数')
    print(factor_test.basic_df['factor'].mean(),"",factor_test.basic_df['factor'].median())
