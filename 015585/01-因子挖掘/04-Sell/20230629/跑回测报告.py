# 每次修改第二行
from run_factor_demo import run_factor
from factor_qyh_lzo_length_bt2_zt_sdel import factor_qyh_lzo_length_bt2_zt_sdel as func
from project_sell_factor_test_origin_forzbw import FactorTest
import pandas as pd
import numpy as np
'''
每次修改:
date
factor_name
参数里的func
参数里的factor_type
'''
date = '20230629'# 周四日期
factor_name = 'factor_qyh_lzo_length_bt2_zt_sdel'
print(factor_name)
factor_path = '/data/user/015585/01-因子挖掘/04-Sell/' + date + '/'
# run_factor(func = func,
#           factor_name = factor_name,
#           factor_type = 'LastZtLastOrder',
#           start_date = 20160101,
#           end_date = 20191231,
#           basic_file_path = '/data/user/018107/factor_zooS/factor_lib_v2/931_public/Basic_closed_hf_finish_20160101_20191231.h5',
#           result_path = factor_path)

start_date, end_date = 20160101, 20191231
df = pd.read_hdf('/data/user/015585/01-因子挖掘/04-Sell/' + date + '/' + factor_name + '_20160101_20191231.h5')
result_path = '/data/user/015585/01-因子挖掘/04-Sell/' + date + '/'
factor_test = FactorTest(start_date, end_date,
                            # test_sample = 'bt',
                            style_list=['T_o2pre', 'free_turn'],
                            cal_mi = True,
                            buy_type='0931',
                            strategy_name='sell')
# factor_test = pj2FactorTest(start_date, end_date, test_sample = 'bt',style_list=['T_o2pre','lzt_label_pattern'],
#                             cal_mi=True, buy_type = '0931',sell_type = 'v',lzt_pattern=[3, 4])
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
