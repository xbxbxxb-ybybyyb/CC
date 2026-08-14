# 每次修改第二行
from run_factor_demo import run_factor
from factor_qyh_lzttick_b1amt_after2zt_max_2max30s import factor_qyh_lzttick_b1amt_after2zt_max_2max30s
from project_2_factor_test_v2 import pj2FactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type
'''

date = '20230316'# 周四日期
factor_name = 'factor_qyh_lzttick_amt_after2to12zt_2max30s_1'
print('saturn')
print(factor_name)
factor_path = '/data/user/015585/01-因子挖掘/' + date + '/'
# run_factor(func = factor_qyh_lzttick_b1amt_after2zt_max_2max30s,
#           factor_name = factor_name,
#           factor_type = 'LastZtLastTick',
#           start_date = 20160101,
#           end_date = 20181231,
#           basic_file_path = '/data/user/018107/factor_zoo2/warehouse/warehouse_931/Basic_closed_hf_finish_20160101_20181231.h5',
#           result_path = factor_path)

start_date, end_date = 20160101, 20181231
# df = pd.read_hdf('/data/user/015585/01-因子挖掘/' + date + '/' + factor_name + '_20160101_20181231.h5')
df = pd.read_hdf('/data/user/015585/01-因子挖掘/04-Sell/' + '20230316' + '/' + factor_name + '_20160101_20181231.h5')
result_path = '/data/user/015585/01-因子挖掘/' + date + '/'
factor_test = pj2FactorTest(start_date, end_date,
                            test_sample = 'bt',
                            style_list=['T_o2pre','tradingday'],
                            cal_mi = True,
                            buy_type='0931',
                            lzt_pattern=[3, 4],
                            sell_type='v')
# factor_test = pj2FactorTest(start_date, end_date, test_sample = 'bt',style_list=['T_o2pre','lzt_label_pattern'],
#                             cal_mi=True, buy_type = '0931',sell_type = 'v',lzt_pattern=[3, 4])
res = []
for col in df.columns:
    print(col)
    factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
    print('check_score:')
    check_score = factor_test.check_score(double_group_df = factor_test.result_dic['double_group_sort']['T_o2pre'].copy(),
                                  month_df=factor_test.result_dic['corr_month'].copy(),
                                  dir=np.sign(factor_test.result_dic['corr_sta'].loc['corr_tot']),
                                  )[1]
    print(check_score['value_diff_score']['score'],check_score['value_stability_score']['score'])
    print('总分:',check_score.loc['score','tot_score'])
    print('CORR：')
    print(factor_test.result_dic['corr_sta'])
    print('weight_ic')
    print(factor_test.result_dic['head_weight_ic'])
    print('高corr库中因子：')
    print(factor_test.result_dic['factor_corr_summary'])
