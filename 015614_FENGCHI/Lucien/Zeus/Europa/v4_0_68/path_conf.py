# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

#%% 数据集
data_path = os.path.join(group_path, f'sunss/europa/20240630_emotion/')
data_all_fpath = os.path.join(data_path, f'factor_df_all_20160101_20221130.pkl')

profit_data_fpath = f'/data/group/800463/sunss/profit/europa/20240401/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, f'xiely/factor_select/Europa/fac_20240630_emotion/base/all/')
xgb_imptc_pct_fsv8_period1_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20191130_reg15_second_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period2_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20200531_reg15_second_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period3_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20201130_reg15_second_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period4_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20210531_reg15_second_FSV8_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv8_period5_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20211130_reg15_second_FSV8_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv8_period6_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20220531_reg15_second_FSV8_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv8_period7_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20221130_reg15_second_FSV8_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv8_period8_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20230531_reg15_second_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period1_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20191130_reg15_second_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period2_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20200531_reg15_second_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period3_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20201130_reg15_second_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period4_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20210531_reg15_second_FSV10_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv10_period5_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20211130_reg15_second_FSV10_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv10_period6_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20220531_reg15_second_FSV10_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv10_period7_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20221130_reg15_second_FSV10_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv10_period8_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20230531_reg15_second_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period1_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20191130_first_FSV11_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period2_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20200531_first_FSV11_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period3_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20201130_first_FSV11_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period4_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20210531_first_FSV11_all_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv11_period5_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20211130_first_FSV11_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv11_period6_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20220531_first_FSV11_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv11_period7_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20221130_first_FSV11_label_pct_graded.xlsx')
# xgb_imptc_pct_fsv11_period8_fpath = os.path.join(xgb_imptc_path, f'europa_xgb_importance_20230531_first_FSV11_label_pct_graded.xlsx')

fsrs_imptc_path = os.path.join(group_path, f'sunss/europa/20240630_emotion/fsrs/')
fsrs_imptc_pct_period1_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20191130.xlsx')
fsrs_imptc_pct_period2_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20200531.xlsx')
fsrs_imptc_pct_period3_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20201130.xlsx')
fsrs_imptc_pct_period4_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20210531.xlsx')
# fsrs_imptc_pct_period5_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20211130.xlsx')
# fsrs_imptc_pct_period6_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20220531.xlsx')
# fsrs_imptc_pct_period7_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20221130.xlsx')
# fsrs_imptc_pct_period8_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_pct_graded_20160101_20230531.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, f'sunss/europa/20240630_emotion/')
factor_score_20191130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
factor_score_20200531_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
factor_score_20201130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
factor_score_20210531_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
# factor_score_20211130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
# factor_score_20220531_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
# factor_score_20221130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')
# factor_score_20230531_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_period.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

model_save_path = os.path.join(fc_path, 'Zeus/pred/')

#%% 因子筛选设置
fs_config = {
    'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_68/rffs_%s.pkl' % period.replace('_roll', '')",
    'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_68/rffs2_%s.pkl' % period.replace('_roll', '')",
}

#%% 标签设置
label_config = {
    'pct': 'label_pct_graded',
    # 'pctAfter': 'label_pct_after_graded'
}

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
                    test_start_date=20191201, test_end_date=20200531, fit_start_date=20200601, fit_end_date=20210531),
    # 'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
    #                 test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20200531,
                         test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period2': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20200531,
                    test_start_date=20200601, test_end_date=20201130, fit_start_date=20201201, fit_end_date=20211130),
    # 'period2': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20200531,
    #                 test_start_date=20200601, test_end_date=20201130, fit_start_date=20201101, fit_end_date=20201130),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20201130,
                         test_start_date=20200601, test_end_date=20201130, fit_start_date=20201101, fit_end_date=20201130),
    'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201130,
                    test_start_date=20201201, test_end_date=20210531, fit_start_date=20210601, fit_end_date=20220531),
    # 'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201130,
    #                 test_start_date=20201201, test_end_date=20210531, fit_start_date=20210501, fit_end_date=20210531),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210531,
                         test_start_date=20201201, test_end_date=20210531, fit_start_date=20210501, fit_end_date=20210531),

    'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210531,
                    test_start_date=20210601, test_end_date=20211130, fit_start_date=20211201, fit_end_date=20221130),
    # 'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210531,
    #                 test_start_date=20210601, test_end_date=20211130, fit_start_date=20211101, fit_end_date=20211130),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20211130,
                         test_start_date=20210601, test_end_date=20211130, fit_start_date=20211101, fit_end_date=20211130),

    # 'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20211130,
    #                 test_start_date=20211201, test_end_date=20220531, fit_start_date=20220601, fit_end_date=20230531),
    'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20211130,
                    test_start_date=20211201, test_end_date=20220531, fit_start_date=20220501, fit_end_date=20220531),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20220531,
                         test_start_date=20211201, test_end_date=20220531, fit_start_date=20220501, fit_end_date=20220531),

    # 'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220531,
    #                 test_start_date=20220601, test_end_date=20221130, fit_start_date=20221201, fit_end_date=20231130),
    'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220531,
                    test_start_date=20220601, test_end_date=20221130, fit_start_date=20221101, fit_end_date=20221130),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20221130,
                         test_start_date=20220601, test_end_date=20221130, fit_start_date=20221101, fit_end_date=20221130),

    # 'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20221130,
    #                 test_start_date=20221201, test_end_date=20230531, fit_start_date=20230601, fit_end_date=20231130),
    'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20221130,
                    test_start_date=20221201, test_end_date=20230531, fit_start_date=20230501, fit_end_date=20230531),
    'period7_roll': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20230531,
                         test_start_date=20221201, test_end_date=20230531, fit_start_date=20230501, fit_end_date=20230531),

    # 'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230531,
    #                 test_start_date=20230601, test_end_date=20231130, fit_start_date=20231201, fit_end_date=20240531),
    'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230531,
                    test_start_date=20230601, test_end_date=20231130, fit_start_date=20231101, fit_end_date=20231130),
    'period8_roll': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20231130,
                    test_start_date=20230601, test_end_date=20231130, fit_start_date=20231101, fit_end_date=20231130),
}