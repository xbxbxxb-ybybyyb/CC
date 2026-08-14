# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'
fc_cheat_path = '/data/user/015614/junkData/cheat/'

#%% 数据集
data_path = os.path.join(group_path, 'sunss/project_sell/20230330/')
# data_test_fpath_with_label = os.path.join(data_path, 'factor_df_931_20160101_20211231_xly.pkl')
# data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_931_20160101_20211231_xly.pkl')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_931_20160101_20220930_1.pkl')
data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_931_20160101_20220930_1.pkl')

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/project_sell/fac-20230330/')
xgb_imptc_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_reg15_second_fac_20230330_FSV8_all_label_diff_pct_graded.xlsx')
xgb_imptc_next_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_reg15_second_fac_20230330_FSV8_all_label_diff_pct_graded.xlsx')
xgb_imptc_fsv10_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_reg15_second_fac_20230330_FSV10_all_label_diff_pct_graded.xlsx')
xgb_imptc_fsv10_next_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_reg15_second_fac_20230330_FSV10_all_label_diff_pct_graded.xlsx')
xgb_imptc_fsv11_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_first_fac_20230330_FSV11_label_diff_pct_graded.xlsx')
xgb_imptc_fsv11_next_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_sell_20210630_first_fac_20230330_FSV11_label_TN_931o2ul_graded.xlsx')

fsrsv2_imptc_path = os.path.join(group_path, 'sunss/project_sell/20230330/fsrs/')
fsrsv2_imptc_period4_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_pct_next_graded_20160101_20210630.xlsx')
fsrsv2_imptc_o2ul_period4_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_graded_20160101_20210630.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/europa/20230317/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_20160101_20200930.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

junk_path = os.path.join(fc_path, 'junkData/')

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20190331, valid_start_date=20190401, valid_end_date=20190930,
                    test_start_date=20191001, test_end_date=20200331, fit_start_date=20200401, fit_end_date=20201231),
    'period2': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331,
                    test_start_date=20200401, test_end_date=20200930, fit_start_date=20201001, fit_end_date=20210630),
    'period3': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210401, fit_end_date=20211231),
    'period4': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210630,
                    test_start_date=20210701, test_end_date=20211231, fit_start_date=20220101, fit_end_date=20220930)
}