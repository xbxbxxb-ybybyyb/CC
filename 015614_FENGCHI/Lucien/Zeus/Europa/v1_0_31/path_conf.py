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
data_path = os.path.join(group_path, 'sunss/for_xly/europa/20221116_new/')
data_test_fpath = os.path.join(data_path, 'factor_df_all_20160101_20220630.pkl')
data_fit_fpath = os.path.join(data_path, 'factor_df_all_20160101_20220630.pkl')
# data_test_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20211231.pkl')
# data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20211231.pkl')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20220630.pkl')
data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20220630.pkl')
# data_test_fpath_cheat = os.path.join(fc_cheat_path, 'factor_df_all_20160101_20220930.pkl')
# data_fit_fpath_cheat = os.path.join(fc_cheat_path, 'factor_df_all_20160101_20220930.pkl')

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/Europa_20221024/')
xgb_imptc_path_20210630new = os.path.join(group_path, 'xiely/factor_select/Europa_20221024/20210630_new/')
xgb_imptc_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20190930_reg15_second_fac_20221116_FSV8_all_pct_graded_lowCost.xlsx')
xgb_imptc_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200331_reg15_second_fac_20221116_FSV8_all_pct_graded_lowCost.xlsx')
xgb_imptc_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200930_reg15_second_fac_20221116_FSV8_all_pct_graded_lowCost.xlsx')
xgb_imptc_period4_fpath = os.path.join(xgb_imptc_path_20210630new, 'xgb_importance_20210630_reg15_second_fac_20221116_FSV8_all_pct_graded_lowCost.xlsx')
xgb_imptc_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20221116_FSV8_all_label_pct_graded_lowCost.xlsx')

xgb_imptc_o2ul_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20190930_reg15_second_fac_20221116_FSV8_all_o2ul_lowCost.xlsx')
xgb_imptc_o2ul_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200331_reg15_second_fac_20221116_FSV8_all_o2ul_lowCost.xlsx')
xgb_imptc_o2ul_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200930_reg15_second_fac_20221116_FSV8_all_o2ul_lowCost.xlsx')
xgb_imptc_o2ul_period4_fpath = os.path.join(xgb_imptc_path_20210630new, 'xgb_importance_20210630_reg15_second_fac_20221116_FSV8_all_o2ul_lowCost.xlsx')
xgb_imptc_o2ul_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20221116_FSV8_all_label_TN_o2ul_lowCost.xlsx')

# 分场景因子
xgb_imptc_hml0_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20190930_reg15_second_fac_20221116_FSV8_hml0_pct_graded_lowCost.xlsx')
xgb_imptc_hml1_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20190930_reg15_second_fac_20221116_FSV8_hml1_pct_graded_lowCost.xlsx')
xgb_imptc_hml2_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20190930_reg15_second_fac_20221116_FSV8_hml2_pct_graded_lowCost.xlsx')
xgb_imptc_hml0_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200331_reg15_second_fac_20221116_FSV8_hml0_pct_graded_lowCost.xlsx')
xgb_imptc_hml1_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200331_reg15_second_fac_20221116_FSV8_hml1_pct_graded_lowCost.xlsx')
xgb_imptc_hml2_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200331_reg15_second_fac_20221116_FSV8_hml2_pct_graded_lowCost.xlsx')
xgb_imptc_hml0_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200930_reg15_second_fac_20221116_FSV8_hml0_pct_graded_lowCost.xlsx')
xgb_imptc_hml1_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200930_reg15_second_fac_20221116_FSV8_hml1_pct_graded_lowCost.xlsx')
xgb_imptc_hml2_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20200930_reg15_second_fac_20221116_FSV8_hml2_pct_graded_lowCost.xlsx')
xgb_imptc_hml0_period4_fpath = os.path.join(xgb_imptc_path_20210630new, 'xgb_importance_20210630_reg15_second_fac_20221116_FSV8_hml0_pct_graded_lowCost.xlsx')
xgb_imptc_hml1_period4_fpath = os.path.join(xgb_imptc_path_20210630new, 'xgb_importance_20210630_reg15_second_fac_20221116_FSV8_hml1_pct_graded_lowCost.xlsx')
xgb_imptc_hml2_period4_fpath = os.path.join(xgb_imptc_path_20210630new, 'xgb_importance_20210630_reg15_second_fac_20221116_FSV8_hml2_pct_graded_lowCost.xlsx')
xgb_imptc_hml0_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20221116_FSV8_hml0_label_pct_graded_lowCost.xlsx')
xgb_imptc_hml1_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20221116_FSV8_hml1_label_pct_graded_lowCost.xlsx')
xgb_imptc_hml2_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20221116_FSV8_hml2_label_pct_graded_lowCost.xlsx')

fsrs_imptc_path = '/data/group/800463/sunss/for_xly/europa/20221116_new/'
fsrs_imptc_period1_fpath = os.path.join(fsrs_imptc_path, 'regression_select_result_20160101_20190930.xlsx')
fsrs_imptc_period2_fpath = os.path.join(fsrs_imptc_path, 'regression_select_result_20160101_20200331.xlsx')
fsrs_imptc_period3_fpath = os.path.join(fsrs_imptc_path, 'regression_select_result_20160101_20200930.xlsx')
fsrs_imptc_period4_fpath = os.path.join(fsrs_imptc_path, 'regression_select_result_20160101_20210630.xlsx')
fsrs_imptc_period5_fpath = os.path.join(fsrs_imptc_path, 'regression_select_result_20160101_20211231.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/for_xly/europa/20221116_new/')
# factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_xly.xlsx')    # 前四个区间用这个
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_20160101_20211231.xlsx')    # 第五个区间用这个

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

junk_path = os.path.join(fc_path, 'junkData/')

#%% 时间设置
date_config = {
    'period1_test': dict(train_start_date=20160101, train_end_date=20181231, valid_start_date=20190102, valid_end_date=20190930, test_start_date=20191001, test_end_date=20200331),
    'period1_fit': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20191001, valid_end_date=20200331, test_start_date=20200401, test_end_date=20201231),
    'period2_test': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331, test_start_date=20200401, test_end_date=20200930),
    'period2_fit': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20200401, valid_end_date=20200930, test_start_date=20201001, test_end_date=20210630),
    'period3_test': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930, test_start_date=20201001, test_end_date=20210331),
    'period3_fit': dict(train_start_date=20160101, train_end_date=20210331, valid_start_date=20201001, valid_end_date=20210331, test_start_date=20210401, test_end_date=20211231),
    'period4_test': dict(train_start_date=20160101, train_end_date=20201231, valid_start_date=20210101, valid_end_date=20210630, test_start_date=20210701, test_end_date=20211231),
    # 'period4_fit': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20210701, valid_end_date=20211231, test_start_date=20220101, test_end_date=20220930)
    'period4_fit': dict(train_start_date=20160101, train_end_date=20201231, valid_start_date=20210101, valid_end_date=20210630, test_start_date=20220101, test_end_date=20220630),
    'period5_test': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20210701, valid_end_date=20211231, test_start_date=20220101, test_end_date=20220630),
    'period5_fit': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20210701, valid_end_date=20211231, test_start_date=20220701, test_end_date=20220930)
}

xbc_rolling_config = {
    'period1_test': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331, test_start_date=20200401, test_end_date=20201231),
    'period1_fit': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331, test_start_date=20200401, test_end_date=20201231),
    'period2_test': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930, test_start_date=20201001, test_end_date=20210630),
    'period2_fit': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930, test_start_date=20201001, test_end_date=20210630),
    'period3_test': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210331, test_start_date=20210401, test_end_date=20211231),
    'period3_fit': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210331, test_start_date=20210401, test_end_date=20211231),
}