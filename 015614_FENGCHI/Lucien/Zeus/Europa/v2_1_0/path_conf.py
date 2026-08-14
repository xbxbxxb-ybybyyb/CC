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
data_path = os.path.join('/data/user/018107/', 'share_file/for_fc/europa/20230329_new/')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20230331.pkl')
data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20230331.pkl')

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/Europa_20221024/20230412-fac-20230329/')
xgb_imptc_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20230329_FSV8_all_label_pct_graded_lowCost_new.xlsx')
xgb_imptc_o2ul_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20230329_FSV8_all_label_TN_931o2ul_graded_lowCost_new.xlsx')
xgb_imptc_fsv10_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20230329_FSV10_all_label_pct_graded_lowCost_new.xlsx')
xgb_imptc_fsv10_o2ul_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_reg15_second_fac_20230329_FSV10_all_label_TN_931o2ul_graded_lowCost_new.xlsx')
xgb_imptc_fsv11_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_first_fac_20230329_FSV11_label_pct_graded.xlsx')
xgb_imptc_fsv11_o2ul_period5_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20211231_first_fac_20230329_FSV11_label_TN_931o2ul_graded.xlsx')

fsrsv2_imptc_path = os.path.join(group_path, 'sunss/europa/20230329_new/fsrs/')
fsrsv2_imptc_period5_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_pct_graded_20160101_20211231.xlsx')
fsrsv2_imptc_o2ul_period5_fpath = os.path.join(fsrsv2_imptc_path, 'fsrsv2_label_TN_o2ul_graded_20160101_20211231.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/europa/20230329_new/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_20160101_20211231.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

junk_path = os.path.join(fc_path, 'junkData/')

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20211231,
                    test_start_date=20191001, test_end_date=20211231, fit_start_date=20200401, fit_end_date=20201231)
}