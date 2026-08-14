# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01
"""
20230705:为了给敬姐测试滚动的效果
"""
import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

#%% 数据集
data_path = os.path.join(group_path, 'sunss/saturn/20230524/')
# filtered_data_test_fpath_with_label = os.path.join(data_path, 'factor_df_filter_931_20160101_20211231_graded.pkl')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_931_20160101_20221231.pkl')

profit_data_fpath = '/data/group/800463/sunss/saturn/data/p2_profit_931_0.20_0.10_500_1500.h5'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/S1/fac_20230524/')
xgb_imptc_fsv8_period4_fpath = os.path.join(xgb_imptc_path, 'S1_xgb_importance_20210331_reg15_second_fac_20230524_FSV8_all_label_v2o10d1_graded_total.xlsx')
xgb_imptc_fsv10_period4_fpath = os.path.join(xgb_imptc_path, 'S1_xgb_importance_20210331_reg15_second_fac_20230524_FSV10_all_label_v2o10d1_graded_total.xlsx')
xgb_imptc_fsv11_period4_fpath = os.path.join(xgb_imptc_path, 'S1_xgb_importance_20210331_first_fac_20230524_FSV11_label_v2o10d1_graded_total.xlsx')

fsrs_imptc_path = os.path.join(group_path, 'sunss/saturn/20230524/fsrs_all/')
fsrs_imptc_period4_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_v2o10d1_graded_20160101_20210331.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/saturn/20230524/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_931_20160101_20200930_noEmotion.xlsx')

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
    # 'period4': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210331,
    #                 test_start_date=20210401, test_end_date=20210930, fit_start_date=20211001, fit_end_date=20220630),
    # 'period4': dict(train_start_date=20160101, train_end_date=20200630, valid_start_date=20210701, valid_end_date=20211231,
    #                 test_start_date=20220101, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),
    'period4': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20220101, valid_end_date=20220630,
                    test_start_date=20220601, test_end_date=20220630, fit_start_date=20220601, fit_end_date=20220630),
}