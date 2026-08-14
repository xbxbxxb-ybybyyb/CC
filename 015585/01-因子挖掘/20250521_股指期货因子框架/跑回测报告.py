from run_factor_demo_parallel_im import run_factor
from future_factor_test import FactorTest
# from StrongFactorTest import StrongFactorTest
import pandas as pd
import numpy as np
import os
'''
'''

start_date = '20220801'
end_date = '20230731'
basic_file_path = '/data/group/800463/data/projectF_public/factor_lib/Basic_future_20220801_20230731.h5'
result_path = '/data/user/015585/01-因子挖掘/08-neptune/future_factor_20250523/'
res = {}

# for factor_name in [f'factor_qyh_future_sample{i}' for i in range(1,11)]:
#     m = __import__(factor_name)
#     func = getattr(m,factor_name)
#     print(factor_name)
#     if os.path.exists(result_path + factor_name.replace('factor_','') + '.h5'):
#         os.remove(result_path + factor_name + '.h5')
#     factor_df0 = run_factor(func, factor_name.replace('factor_',''), 'TTickabAll',
#                                start_date, end_date, basic_file_path, result_path,interval_res=False)

for factor_name in [f'factor_qyh_future_sample{i}' for i in range(1,2)]:
    df = pd.read_hdf(result_path + factor_name.replace('factor_','') + '.h5')
    factor_test = FactorTest(start_date, end_date)
    for col in df.columns:
        print(col)
        res_factor = factor_test.factor_test(df[[col]],result_path=result_path, factor_corr_test=True, generate_pdf=True)
        res[col] = res_factor

for factor in res:
    print(factor)
    print(res[factor]['corr_sta'].loc['corr_tot', 'value'])
    # print(res[factor]['check_score_res'].iloc[-1,-1])
    print(res[factor]['check_score_res'])
    print('')

factor_name = 'qyh_future_sample7'
df = pd.read_hdf(result_path + factor_name + '.h5')
# factor_test = FactorTest(start_date, end_date)
# for col in df.columns:
#     print(col)
#     res_factor = factor_test.factor_test(df[[col]], result_path=result_path, factor_corr_test=False, generate_pdf=False)
#     res[col] = res_factor



