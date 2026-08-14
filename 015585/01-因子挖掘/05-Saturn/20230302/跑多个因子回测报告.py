from project_2_group_factors_test_v1 import generate_factors_pdf
'''
每次修改:
'''
date = '20230216'
result_path = '/data/user/015585/01-因子挖掘/' + date + '/'
save_name = 'Test Factors'
test_factor_list = ['factor_qyh_T1mtra_cct_buy',
                    'factor_qyh_T1mtra_r_amt2pct_ud_1_ln']#待测因子列表
res = generate_factors_pdf(date=date,
                           result_path=result_path,
                           save_name = 'Test Factors',
                           path_ori = '/data/user/015585/01-因子挖掘/',
                           test_factor_list=['factor_qyh_T1mtra_cct_buy',
                                             'factor_qyh_T1mtra_r_amt2pct_ud_1_ln'])
