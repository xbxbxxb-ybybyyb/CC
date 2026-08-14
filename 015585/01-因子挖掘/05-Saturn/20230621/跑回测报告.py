# 每次修改第二行
from run_factor_demo import run_factor
from factor_qyh_2t_max_uldown import factor_qyh_2t_max_uldown as func
from project_2_factor_test_origin import pj2FactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type'''

date = '20230621'#周四日期
factor_name = 'factor_qyh_2t_max_uldown'
factor_path = '/data/user/015585/01-因子挖掘/' + date + '/jupyter调试/'
run_factor(func = func,
          factor_name = factor_name,
          factor_type = 'T-1_factor',
          start_date = 20160101,
          end_date = 20181231,
          basic_file_path = '/data/user/018107/factor_zoo2/factor_lib_update/warehouse/warehouse_931/Basic_closed_hf_finish.h5',
          result_path = factor_path )

start_date, end_date = 20160101, 20181231
df = pd.read_hdf('/data/user/015585/01-因子挖掘/' + date + '/jupyter调试/' + factor_name + '_20160101_20181231.h5')
result_path = '/data/user/015585/01-因子挖掘/' + date + '/jupyter调试/'
factor_test = pj2FactorTest(start_date, end_date, buy_type='0931', lzt_pattern=[3, 4])
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    print('check_score:')
    check_score = factor_test.check_score(double_group_df = factor_test.result_dic['double_group_sort']['tradingday'].copy(),
                                  month_df=factor_test.result_dic['corr_month'].copy(),
                                  dir=np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']),
                                  )[1]
    print(check_score)
    print('互信息：')
    print(factor_test.result_dic['corr_sta'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
