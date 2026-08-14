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
data_path = os.path.join(group_path, 'sunss/jupiterZ/20230415/')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20230331_xly.pkl')

profit_data_fpath = '/data/group/800463/sunss/jupiterZ/newData/JupiterZ_Label_0.10_800_190_SH450_SZ100.pkl'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/JupiterZ_20230205/fac_20230415/')
xgb_imptc_afterZ_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_reg15_second_fac_20230415_FSV8_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_afterZ_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_reg15_second_fac_20230415_FSV8_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_afterZ_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_reg15_second_fac_20230415_FSV8_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_afterZ_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_reg15_second_fac_20230415_FSV8_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_afterZ_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_reg15_second_fac_20230415_FSV8_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv10_afterZ_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_reg15_second_fac_20230415_FSV10_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv10_afterZ_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_reg15_second_fac_20230415_FSV10_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv10_afterZ_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_reg15_second_fac_20230415_FSV10_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv10_afterZ_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_reg15_second_fac_20230415_FSV10_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv10_afterZ_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_reg15_second_fac_20230415_FSV10_all_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv11_afterZ_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_first_fac_20230415_FSV11_label_diff_pct_afterZ_graded.xlsx')
xgb_imptc_fsv11_afterZ_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_first_fac_20230415_FSV11_label_diff_pct_afterZ_graded.xlsx')
xgb_imptc_fsv11_afterZ_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_first_fac_20230415_FSV11_label_diff_pct_afterZ_graded.xlsx')
xgb_imptc_fsv11_afterZ_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_first_fac_20230415_FSV11_label_diff_pct_afterZ_graded_lowCost.xlsx')
xgb_imptc_fsv11_afterZ_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_first_fac_20230415_FSV11_label_diff_pct_afterZ_graded_lowCost.xlsx')

xgb_imptc_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_reg15_second_fac_20230415_FSV8_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_reg15_second_fac_20230415_FSV8_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_reg15_second_fac_20230415_FSV8_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_reg15_second_fac_20230415_FSV8_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_reg15_second_fac_20230415_FSV8_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv10_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_reg15_second_fac_20230415_FSV10_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv10_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_reg15_second_fac_20230415_FSV10_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv10_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_reg15_second_fac_20230415_FSV10_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv10_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_reg15_second_fac_20230415_FSV10_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv10_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_reg15_second_fac_20230415_FSV10_all_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv11_lowCost_period1_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20190930_first_fac_20230415_FSV11_label_diff_pct_graded.xlsx')
xgb_imptc_fsv11_lowCost_period2_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200331_first_fac_20230415_FSV11_label_diff_pct_graded.xlsx')
xgb_imptc_fsv11_lowCost_period3_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20200930_first_fac_20230415_FSV11_label_diff_pct_graded.xlsx')
xgb_imptc_fsv11_lowCost_period4_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20210630_first_fac_20230415_FSV11_label_diff_pct_graded_lowCost.xlsx')
xgb_imptc_fsv11_lowCost_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_jupiterZ_20211231_first_fac_20230415_FSV11_label_diff_pct_graded_lowCost.xlsx')

fsrsv2_imptc_path = os.path.join(group_path, 'sunss/jupiterZ/20230415/fsrs/')
fsrsv2_imptc_lowCost_period1_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_pct_graded_20160101_20190930.xlsx')
fsrsv2_imptc_lowCost_period2_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_pct_graded_20160101_20200331.xlsx')
fsrsv2_imptc_lowCost_period3_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_pct_graded_20160101_20200930.xlsx')
fsrsv2_imptc_lowCost_period4_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_pct_graded_20160101_20210630.xlsx')
fsrsv2_imptc_afterZ_lowCost_period1_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_afterZ_graded_20160101_20190930.xlsx')
fsrsv2_imptc_afterZ_lowCost_period2_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_afterZ_graded_20160101_20200331.xlsx')
fsrsv2_imptc_afterZ_lowCost_period3_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_afterZ_graded_20160101_20200930.xlsx')
fsrsv2_imptc_afterZ_lowCost_period4_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_diff_afterZ_graded_20160101_20210630.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/jupiterZ/20230415/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_xly.xlsx')

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
                    test_start_date=20210701, test_end_date=20211231, fit_start_date=20211201, fit_end_date=20211231),
    # 滚动了三个月
    'period5': dict(train_start_date=20160101, train_end_date=20210630, valid_start_date=20211001, valid_end_date=20220331,
                    test_start_date=20220401, test_end_date=20220930, fit_start_date=20221001, fit_end_date=20230331),
}